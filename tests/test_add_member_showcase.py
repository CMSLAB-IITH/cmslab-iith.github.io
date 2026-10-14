import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import add_member_showcase as helper


REPOSITORY = Path(__file__).resolve().parents[1]


def make_sample_pdf(path: Path) -> None:
    stream = b"BT /F1 24 Tf 72 720 Td (Sample Poster) Tj ET"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    content = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(content))
        content.extend(f"{number} 0 obj\n".encode())
        content.extend(obj + b"\nendobj\n")
    xref = len(content)
    content.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    content.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        content.extend(f"{offset:010d} 00000 n \n".encode())
    content.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    path.write_bytes(content)


class HelperUnitTests(unittest.TestCase):
    def test_slug_removes_title_and_normalizes_punctuation(self):
        self.assertEqual(helper.slugify("Mr. Pushkar A. Pandit"), "pushkar-a-pandit")

    def test_find_member_accepts_case_only_difference(self):
        data = {"sections": [{"people": [{"name": "Ms. Example Member"}]}]}
        self.assertEqual(helper.find_member(data, "ms. example member")["name"], "Ms. Example Member")

    def test_find_member_accepts_missing_initial_period(self):
        data = {"sections": [{"people": [{"name": "Mr. Pushkar A. Pandit"}]}]}
        self.assertEqual(helper.find_member(data, "Mr. Pushkar A Pandit")["name"], "Mr. Pushkar A. Pandit")

    def test_parse_ssh_and_https_github_remotes(self):
        expected = ("CMSLAB-IITH", "cmslab-iith.github.io")
        self.assertEqual(helper.parse_github_remote("git@github.com:CMSLAB-IITH/cmslab-iith.github.io.git"), expected)
        self.assertEqual(helper.parse_github_remote("https://github.com/CMSLAB-IITH/cmslab-iith.github.io.git"), expected)

    def test_authenticated_username_must_match(self):
        responses = [
            mock.Mock(returncode=0, stdout="", stderr=""),
            mock.Mock(returncode=0, stdout="someone-else\n", stderr=""),
        ]
        with mock.patch.object(helper.shutil, "which", return_value="/usr/bin/gh"), mock.patch.object(
            helper, "run", side_effect=responses
        ):
            with self.assertRaisesRegex(helper.ShowcaseError, "Authenticated as"):
                helper.authenticate("expected-user", "CMSLAB-IITH", "website-editors")

    def test_active_team_member_is_accepted(self):
        responses = [
            mock.Mock(returncode=0, stdout="", stderr=""),
            mock.Mock(returncode=0, stdout="expected-user\n", stderr=""),
            mock.Mock(returncode=0, stdout="active\n", stderr=""),
        ]
        with mock.patch.object(helper.shutil, "which", return_value="/usr/bin/gh"), mock.patch.object(
            helper, "run", side_effect=responses
        ):
            helper.authenticate("expected-user", "CMSLAB-IITH", "website-editors")


class LocalIntegrationTest(unittest.TestCase):
    def test_sample_poster_creates_valid_local_member_page(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "site"
            root.mkdir()
            for filename in ("build.py", "check_site.py"):
                shutil.copy2(REPOSITORY / filename, root / filename)
            shutil.copytree(REPOSITORY / "data", root / "data")
            shutil.copytree(REPOSITORY / "assets", root / "assets")
            sample = Path(temporary) / "sample-poster.pdf"
            make_sample_pdf(sample)

            with mock.patch.multiple(
                helper,
                ROOT=root,
                GROUP_DATA=root / "data" / "group.json",
                POSTER_DIR=root / "assets" / "uploads" / "posters",
            ):
                result = helper.main(
                    [
                        "--local-only",
                        "--member-name", "Mr. Pushkar A. Pandit",
                        "--file", str(sample),
                        "--title", "Synthetic <Sample> Poster",
                        "--description", "Temporary integration-test description & validation.",
                    ]
                )

            self.assertEqual(result, 0)
            group = json.loads((root / "data" / "group.json").read_text())
            pushkar = helper.find_member(group, "Mr. Pushkar A. Pandit")
            self.assertEqual(pushkar["showcase"]["slug"], "pushkar-a-pandit")
            self.assertTrue((root / "pushkar-a-pandit-poster.html").is_file())
            people = (root / "people.html").read_text()
            self.assertIn('href="pushkar-a-pandit-poster.html"', people)
            self.assertLess(people.index("View poster &amp; project"), people.index("PhD student, IISc"))
            poster_page = (root / "pushkar-a-pandit-poster.html").read_text()
            self.assertIn("Synthetic &lt;Sample&gt; Poster", poster_page)
            self.assertIn("description &amp; validation", poster_page)
            self.assertIn('First-page preview of &quot;Synthetic &lt;Sample&gt; Poster&quot; by Mr. Pushkar A. Pandit', poster_page)

            replacement_args = [
                "--local-only",
                "--member-name", "Mr. Pushkar A. Pandit",
                "--file", str(sample),
                "--title", "Replacement Poster",
                "--description", "Replacement description.",
            ]
            with mock.patch.multiple(
                helper,
                ROOT=root,
                GROUP_DATA=root / "data" / "group.json",
                POSTER_DIR=root / "assets" / "uploads" / "posters",
            ), mock.patch("builtins.input", return_value="n"):
                self.assertEqual(helper.main(replacement_args), 0)
            unchanged = json.loads((root / "data" / "group.json").read_text())
            self.assertEqual(helper.find_member(unchanged, "Mr. Pushkar A. Pandit")["showcase"]["title"], "Synthetic <Sample> Poster")

            with mock.patch.multiple(
                helper,
                ROOT=root,
                GROUP_DATA=root / "data" / "group.json",
                POSTER_DIR=root / "assets" / "uploads" / "posters",
            ):
                self.assertEqual(helper.main([*replacement_args, "--yes"]), 0)
            replaced = json.loads((root / "data" / "group.json").read_text())
            self.assertEqual(helper.find_member(replaced, "Mr. Pushkar A. Pandit")["showcase"]["title"], "Replacement Poster")


if __name__ == "__main__":
    unittest.main()
