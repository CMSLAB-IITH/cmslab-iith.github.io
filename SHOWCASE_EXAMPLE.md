# Poster showcase example

This example shows how Pushkar created a personal poster page. Replace the username, displayed name, PDF path, title and description with your own information.

## Before running

- Join the `CMSLAB-IITH/website-editors` team and accept the organization invitation.
- Install Python 3, Git and [GitHub CLI](https://cli.github.com/).
- Keep the PDF outside the repository and start from a clean, current `main` branch.

```bash
cd /path/to/cmslab-iith.github.io
git switch main
git pull --ff-only origin main
git status --short
gh auth login --hostname github.com --git-protocol ssh --web
```

`git status --short` must print nothing. PDF preview generation requires either `PyMuPDF` from `requirements-editor.txt` or the `pdftoppm` program from Poppler.

## Pushkar's example command

```bash
python3 add_member_showcase.py \
  --github-username 'ppandit95' \
  --member-name 'Mr. Pushkar A Pandit' \
  --file '/home/pushkar/Downloads/Poster.pdf' \
  --title 'Research Area: Multicomponent Diffusion and Microstructural Evolution in High-Temperature Alloys' \
  --description 'My research investigates microstructural evolution in Ni-based superalloys, including growth, coarsening, morphological instabilities, and splitting of γ′ precipitates in Ni–Al–X alloys. The work combines diffusion experiments, physics-informed neural networks, CALPHAD thermodynamics, and phase-field modelling to connect alloy chemistry, diffusion kinetics, elastic interactions, and microstructural stability.'
```

The displayed name must identify exactly one person on the website's People page. The helper validates the files, creates a branch and commit, pushes it, and opens a pull request automatically.

## Publish the page

1. Open the pull-request URL printed by the helper.
2. Review the files and wait for the required `build` check to pass.
3. Merge the pull request.
4. Wait for the GitHub Pages workflow in the repository's **Actions** tab.
5. Check the new link beneath your name on <https://cmslab-iith.github.io/people.html>.

Pushkar's resulting page is <https://cmslab-iith.github.io/pushkar-a-pandit-poster.html>. Your page address is generated from your displayed name.

For troubleshooting and replacement instructions, read [CONTRIBUTING.md](CONTRIBUTING.md).
