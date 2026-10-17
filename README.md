# CμMS Group · IIT Hyderabad

**Computational Microstructure Modeling and Simulation**, part of **M³ Lab: Multiscale Modeling of Materials**.

M³ Lab is jointly led by **Prof. Saswata Bhattacharyya and Prof. Anuj Goyal**, IIT Hyderabad. The CμMS Group is led by Prof. Saswata Bhattacharyya.

Website: https://cmslab-iith.github.io/

## For group members

Read [the step-by-step editing guide](CONTRIBUTING.md) to add posters, group photos, news or profile updates through GitHub or VS Code. No local build is needed to publish: GitHub automatically builds and deploys changes to `main`.

To create or replace your personal poster page from a desktop clone, install the editor requirements and run the guided helper:

```sh
python3 -m pip install -r requirements-editor.txt
python3 add_member_showcase.py
```

See [Pushkar's minimal poster showcase example](SHOWCASE_EXAMPLE.md) for a complete command that new members can adapt.

The helper accepts PDF, PPT and PPTX files, verifies the contributor's `website-editors` membership through GitHub CLI, and opens a pull request. It never asks for a GitHub password or token.

- `data/group.json`: members, collaborators and their work.
- `data/activity.json`: posters, group photos and news.
- `assets/uploads/`: poster PDFs and photographs.
- `add_member_showcase.py`: guided member poster-page and pull-request helper.
- `build.py`: page text and templates.
- `assets/site.css`: visual design.

Local preview: `python3 build.py`, `python3 check_site.py`, then `python3 -m http.server 4175`.

## Sources

Membership, lab hierarchy and supervision reflect Saswata Bhattacharyya's corrections. Research topics and thesis years come from the supplied CV. Publication and profile links identify sources. Portrait provenance is retained in `data/group.json`. Photographs and institutional logos retain their respective owners' rights.
