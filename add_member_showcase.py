#!/usr/bin/env python3
"""Create or replace one member poster page and optionally open a pull request."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GROUP_DATA = ROOT / "data" / "group.json"
POSTER_DIR = ROOT / "assets" / "uploads" / "posters"
MAX_FILE_BYTES = 95 * 1024 * 1024
SUPPORTED_FILES = {".pdf", ".ppt", ".pptx"}


class ShowcaseError(RuntimeError):
    """An actionable contributor error."""


def run(command: list[str], *, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd or ROOT, check=check, text=True, capture_output=True)


def prompt(value: str | None, label: str) -> str:
    answer = value if value is not None else input(f"{label}: ")
    answer = answer.strip()
    if not answer:
        raise ShowcaseError(f"{label} cannot be empty.")
    return answer


def slugify(name: str) -> str:
    words = name.strip().split()
    if words and words[0].rstrip(".").casefold() in {"mr", "mrs", "ms", "miss", "dr", "prof"}:
        words = words[1:]
    ascii_name = unicodedata.normalize("NFKD", " ".join(words)).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_name.casefold()).strip("-")
    if not slug:
        raise ShowcaseError("The displayed member name cannot be converted to a safe page name.")
    return slug


def normalized_member_name(name: str) -> str:
    """Ignore harmless spacing, case, and punctuation differences in displayed names."""
    return "".join(character.casefold() for character in unicodedata.normalize("NFKC", name) if character.isalnum())


def load_group_data() -> dict:
    try:
        return json.loads(GROUP_DATA.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ShowcaseError(f"Cannot read {GROUP_DATA.relative_to(ROOT)}: {exc}") from exc


def load_group_data_from_main() -> dict:
    run(["git", "fetch", "origin", "main"])
    result = run(["git", "show", "origin/main:data/group.json"])
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ShowcaseError(f"Cannot read data/group.json from origin/main: {exc}") from exc


def find_member(data: dict, displayed_name: str) -> dict:
    people = [person for section in data.get("sections", []) for person in section.get("people", [])]
    exact = [person for person in people if person.get("name") == displayed_name]
    if len(exact) == 1:
        return exact[0]
    normalized = [
        person
        for person in people
        if normalized_member_name(str(person.get("name", ""))) == normalized_member_name(displayed_name)
    ]
    if len(normalized) == 1:
        return normalized[0]
    choices = ", ".join(person.get("name", "") for person in people)
    if not exact and not normalized:
        raise ShowcaseError(f'No member is displayed as "{displayed_name}". Available names: {choices}')
    raise ShowcaseError(f'The displayed name "{displayed_name}" is ambiguous; ask a maintainer to make it unique.')


def validate_source(path_text: str) -> Path:
    source = Path(path_text).expanduser().resolve()
    if not source.is_file():
        raise ShowcaseError(f"Poster or presentation does not exist: {source}")
    if source.suffix.casefold() not in SUPPORTED_FILES:
        raise ShowcaseError("Supported poster formats are PDF, PPT, and PPTX.")
    if source.stat().st_size == 0:
        raise ShowcaseError("The supplied poster file is empty.")
    if source.stat().st_size >= MAX_FILE_BYTES:
        raise ShowcaseError("The supplied file is too large for GitHub. Keep it below 95 MiB.")
    return source


def convert_to_pdf(source: Path, work: Path) -> Path:
    if source.suffix.casefold() == ".pdf":
        output = work / "poster.pdf"
        shutil.copy2(source, output)
        return output
    office = shutil.which("libreoffice") or shutil.which("soffice")
    if not office:
        raise ShowcaseError("LibreOffice is required to convert PPT/PPTX input. Install it or supply a PDF.")
    profile = work / "libreoffice-profile"
    profile.mkdir()
    result = run(
        [
            office,
            f"-env:UserInstallation={profile.as_uri()}",
            "--headless",
            "--convert-to", "pdf:impress_pdf_Export",
            "--outdir", str(work),
            str(source),
        ]
    )
    output = work / f"{source.stem}.pdf"
    if not output.is_file() or output.stat().st_size == 0:
        details = (result.stderr or result.stdout).strip()
        raise ShowcaseError(f"LibreOffice did not produce a PDF. {details}")
    return output


def render_preview(pdf: Path, destination: Path) -> None:
    try:
        import pymupdf as fitz  # type: ignore
    except ImportError:
        try:
            import fitz  # type: ignore
        except ImportError:
            fitz = None
    if fitz is not None:
        try:
            document = fitz.open(pdf)
            if document.needs_pass or document.page_count < 1:
                raise ShowcaseError("The PDF is encrypted or contains no pages.")
            page = document.load_page(0)
            longest = max(page.rect.width, page.rect.height)
            scale = min(3.0, 1800 / longest) if longest else 1.0
            pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
            pixmap.save(destination, jpg_quality=86)
            document.close()
            return
        except ShowcaseError:
            raise
        except Exception as exc:
            raise ShowcaseError(f"Cannot read or render the supplied PDF: {exc}") from exc
    renderer = shutil.which("pdftoppm")
    if not renderer:
        raise ShowcaseError(
            "A PDF preview renderer is required. Install PyMuPDF (`python -m pip install -r requirements-editor.txt`) "
            "or Poppler's pdftoppm."
        )
    base = destination.with_suffix("")
    result = run(
        [renderer, "-f", "1", "-singlefile", "-jpeg", "-jpegopt", "quality=86", "-scale-to", "1800", str(pdf), str(base)],
        check=False,
    )
    produced = base.with_suffix(".jpg")
    if result.returncode or not produced.is_file() or produced.stat().st_size == 0:
        raise ShowcaseError(f"Cannot read or render the supplied PDF: {(result.stderr or result.stdout).strip()}")
    if produced != destination:
        produced.replace(destination)


def parse_github_remote(remote: str) -> tuple[str, str]:
    match = re.search(r"github\.com(?::|/)([^/]+)/([^/]+?)(?:\.git)?$", remote.strip())
    if not match:
        raise ShowcaseError("The origin remote must point to a GitHub repository.")
    return match.group(1), match.group(2)


def ensure_clean_worktree() -> None:
    status = run(["git", "status", "--porcelain"]).stdout.strip()
    if status:
        raise ShowcaseError("The repository has uncommitted changes. Commit or stash them before publishing.")


def authenticate(username: str, owner: str, team: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", username):
        raise ShowcaseError(f'"{username}" is not a valid GitHub username.')
    if not re.fullmatch(r"[A-Za-z0-9_-]+", team):
        raise ShowcaseError(f'"{team}" is not a valid GitHub team slug.')
    if not shutil.which("gh"):
        raise ShowcaseError("GitHub CLI (`gh`) is required. Install it from https://cli.github.com/ and run again.")
    status = run(["gh", "auth", "status", "--hostname", "github.com"], check=False)
    if status.returncode:
        print("GitHub authentication is required; opening the official GitHub CLI login flow.")
        login = subprocess.run(["gh", "auth", "login", "--hostname", "github.com", "--web"], cwd=ROOT)
        if login.returncode:
            raise ShowcaseError("GitHub authentication was cancelled or failed.")
    authenticated = run(["gh", "api", "user", "--jq", ".login"]).stdout.strip()
    if authenticated.casefold() != username.casefold():
        raise ShowcaseError(f'Authenticated as "{authenticated}", but the entered username is "{username}".')
    membership = run(
        ["gh", "api", f"orgs/{owner}/teams/{team}/memberships/{authenticated}", "--jq", ".state"],
        check=False,
    )
    if membership.returncode or membership.stdout.strip() != "active":
        raise ShowcaseError(
            f'GitHub account "{authenticated}" is not an active member of the {owner}/{team} team, '
            "or the login lacks permission to read team membership. Accept the organization invitation and try again."
        )


def write_showcase(data: dict, member: dict, showcase: dict, pdf: Path, preview: Path) -> tuple[Path, Path]:
    slug = showcase["slug"]
    pdf_destination = POSTER_DIR / f"{slug}.pdf"
    preview_destination = POSTER_DIR / f"{slug}-preview.jpg"
    POSTER_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(pdf, pdf_destination)
    shutil.copy2(preview, preview_destination)
    member["showcase"] = showcase
    GROUP_DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return pdf_destination, preview_destination


def build_and_check() -> None:
    for script in ("build.py", "check_site.py"):
        result = run([sys.executable, script], check=False)
        if result.stdout:
            print(result.stdout.rstrip())
        if result.returncode:
            raise ShowcaseError(f"{script} failed:\n{result.stderr.strip()}")


def create_publish_branch(slug: str) -> str:
    stem = f"add-{slug}-poster-{datetime.now(timezone.utc):%Y%m%d}"
    branch = stem
    number = 2
    while run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], check=False).returncode == 0:
        branch = f"{stem}-{number}"
        number += 1
    run(["git", "switch", "--create", branch, "origin/main"])
    return branch


def commit_push_and_open_pr(branch: str, member_name: str, slug: str) -> str:
    paths = ["data/group.json", f"assets/uploads/posters/{slug}.pdf", f"assets/uploads/posters/{slug}-preview.jpg"]
    paths.extend(path.name for path in ROOT.glob("*.html"))
    run(["git", "add", "--", *paths])
    if run(["git", "diff", "--cached", "--quiet"], check=False).returncode == 0:
        raise ShowcaseError("The supplied content is identical to the existing member showcase; there is nothing to publish.")
    run(["git", "commit", "-m", f"Add poster page for {member_name}"])
    run(["git", "push", "--set-upstream", "origin", branch])
    result = run(
        [
            "gh", "pr", "create", "--base", "main", "--head", branch,
            "--title", f"Add poster page for {member_name}",
            "--body", "Generated with `add_member_showcase.py`. The site build and local-link validation passed locally.",
        ]
    )
    return result.stdout.strip()


def description_from_args(args: argparse.Namespace) -> str:
    if args.description and args.description_file:
        raise ShowcaseError("Use either --description or --description-file, not both.")
    if args.description_file:
        try:
            value = Path(args.description_file).expanduser().read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise ShowcaseError(f"Cannot read description file: {exc}") from exc
        return prompt(value, "Brief description")
    return prompt(args.description, "Brief description")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--github-username", help="GitHub username used for publishing")
    parser.add_argument("--member-name", help="Full name exactly as displayed on people.html")
    parser.add_argument("--file", help="Path to a PDF, PPT, or PPTX poster")
    parser.add_argument("--title", help="Poster/page title")
    parser.add_argument("--description", help="Brief plain-text description")
    parser.add_argument("--description-file", help="UTF-8 text file containing the brief description")
    parser.add_argument("--team", default="website-editors", help="GitHub organization team slug")
    parser.add_argument("--local-only", action="store_true", help="Generate and validate locally without GitHub or Git operations")
    parser.add_argument("--yes", action="store_true", help="Confirm replacement of an existing showcase")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        member_name = prompt(args.member_name, "Full name as displayed on the People page")
        source = validate_source(prompt(args.file, "Poster or presentation path"))
        title = prompt(args.title, "Poster title")
        description = description_from_args(args)
        username = ""
        owner = ""
        if not args.local_only:
            username = prompt(args.github_username, "GitHub username")
            ensure_clean_worktree()
            owner, _repository = parse_github_remote(run(["git", "remote", "get-url", "origin"]).stdout)
            authenticate(username, owner, args.team)

        data = load_group_data() if args.local_only else load_group_data_from_main()
        member = find_member(data, member_name)
        existing = member.get("showcase")
        if existing and not args.yes:
            print(f'Existing showcase: {existing.get("title", "Untitled")} ({existing.get("slug", "unknown page")})')
            if input("Replace this member's showcase? [y/N]: ").strip().casefold() not in {"y", "yes"}:
                print("No changes made.")
                return 0
        slug = existing.get("slug") if existing else slugify(member["name"])
        used_by = [
            person["name"]
            for section in data.get("sections", [])
            for person in section.get("people", [])
            if person is not member and person.get("showcase", {}).get("slug") == slug
        ]
        if used_by:
            raise ShowcaseError(f'Showcase page name "{slug}" is already used by {used_by[0]}.')

        with tempfile.TemporaryDirectory(prefix="cmslab-poster-") as temporary:
            work = Path(temporary)
            pdf = convert_to_pdf(source, work)
            if pdf.stat().st_size >= MAX_FILE_BYTES:
                raise ShowcaseError("The converted PDF is too large for GitHub. Keep it below 95 MiB.")
            preview = work / "preview.jpg"
            render_preview(pdf, preview)
            branch = ""
            if not args.local_only:
                branch = create_publish_branch(slug)
            showcase = {
                "slug": slug,
                "title": title,
                "description": description,
                "alt": f'First-page preview of "{title}" by {member["name"]}',
                "pdf": f"assets/uploads/posters/{slug}.pdf",
                "preview": f"assets/uploads/posters/{slug}-preview.jpg",
            }
            write_showcase(data, member, showcase, pdf, preview)
        build_and_check()

        page = f"{slug}-poster.html"
        if args.local_only:
            print(f"Local showcase created successfully: {page}")
            return 0
        pr_url = commit_push_and_open_pr(branch, member["name"], slug)
        print(f"Pull request opened: {pr_url}")
        print("Wait for the required build check to pass, then merge your pull request into main.")
        print("The GitHub Pages site will deploy automatically after the merge.")
        return 0
    except ShowcaseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as exc:
        details = (exc.stderr or exc.stdout or str(exc)).strip()
        print(f"Error: command failed: {' '.join(exc.cmd)}\n{details}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
