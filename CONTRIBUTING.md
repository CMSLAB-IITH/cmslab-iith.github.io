# Updating the CμMS group website

The site belongs to the CμMS Group within **M³ Lab (Multiscale Modeling of Materials)**. M³ Lab is jointly led by Prof. Saswata Bhattacharyya and Prof. Anuj Goyal, IIT Hyderabad.

## Access

Use your own GitHub account. Ask Prof. Saswata Bhattacharyya to add your GitHub username to the **website-editors** team. Accept the GitHub organization invitation before editing. This team has **Write** access only to the public website repository; it does not grant access to private lab or personal-code repositories. No shared password is needed.

## For existing repository administrators: add members

1. Ask each member for their GitHub username. They should create their own account if needed.
2. Open the organization team named **website-editors** and add the exact account as an organization **Member**, never as an Owner.
3. Keep the team's repository access limited to `CMSLAB-IITH/cmslab-iith.github.io` with the **Write** role. Administrator access is unnecessary for posting content.
4. Ask the member to accept the GitHub invitation and share this guide with them.
5. Periodically review the team's membership and remove people who no longer edit the website.

Organization base repository permissions must remain set to **None**. Access to private lab or personal repositories must be granted separately and explicitly. Do not share login credentials.

## Easiest method: edit in your browser

1. Open this repository on GitHub and press `.` to open its browser editor. You can also use VS Code on your computer.
2. Upload photos to `assets/uploads/photos/` and poster PDFs to `assets/uploads/posters/`. Use short filenames without spaces, for example `group-meeting-2026-09.jpg`.
3. Edit `data/activity.json`. Add an entry to `photos`, `posters` or `updates`, following the examples below. Separate multiple entries with commas.
4. Create a branch with a short descriptive name, such as `add-group-meeting-photo`. Open Source Control, describe your change, commit it to that branch and open a pull request into `main`. Direct pushes to `main` are blocked.
5. Wait for the “Build and publish group website” check to pass and for a maintainer to approve the pull request. If the check fails, open it to find and correct the missing file or invalid JSON error.
6. Merge the approved pull request. The merge to `main` publishes the website automatically; confirm that the deployment completes in the Actions tab.

You do **not** need to run Python or edit generated HTML when using GitHub. The publishing workflow rebuilds the pages automatically.

### Group photo

Add to the `photos` array:

```json
{
  "title": "Our group meeting",
  "date": "2026-09-22",
  "author": "Your name",
  "image": "assets/uploads/photos/group-meeting-2026-09.jpg",
  "alt": "Group members gathered after a research discussion",
  "caption": "A short description of the occasion and people pictured."
}
```

### Poster

Add to the `posters` array:

```json
{
  "title": "Your poster title",
  "date": "2026-09-22",
  "author": "Author names",
  "file": "assets/uploads/posters/your-poster.pdf",
  "caption": "Conference name and a brief explanation of the research."
}
```

You may also add `image` and `alt` for a poster preview. For `updates`, use `title`, `date`, `author` and `caption` without a file or image.

## Update a member profile

Edit `data/group.json`. Keep the person in the correct current/former section. Research summaries, selected papers, affiliations and links can be changed independently. Add portraits under `assets/images/group/` and update the person's `image` field.

## Using desktop VS Code

Clone the repository, open the folder and edit the same files. To preview locally, run:

```sh
python3 build.py
python3 check_site.py
python3 -m http.server 4175
```

Open http://localhost:4175/. Commit the changes to a new branch, push that branch and open a pull request into `main`. Direct pushes to `main` are intentionally blocked.

## Before posting

The website and repository are public. Share photos with the pictured people's agreement and posters cleared for public sharing. Credit authors and photographers. Do not upload unpublished confidential results, private contact details or personal documents.
