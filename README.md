# CμS · Computational Microstructures Modeling and Simulations

Independent group website at https://cmslab-iith.github.io/.

## Edit in VS Code

- `data/group.json`: names, affiliations, research, publications and profile links.
- `assets/images/group/`: portraits. Keep the `image` path in each member entry consistent.
- `build.py`: page text and templates.
- `assets/site.css`: layout, colors and thumbnail sizes.

Run `python3 build.py` after editing the data or page templates. Commit the generated HTML together with the changes. GitHub Pages serves the root of the `main` branch. There are no server dependencies or JavaScript requirements.

Preview: `python3 -m http.server 4175`, then visit http://localhost:4175/.

## Sources

Member topics and thesis years come from the supplied CV; membership and joint supervision reflect Saswata Bhattacharya's corrections. Selected works link to their publications. Collaborator links distinguish personal/group homepages from institutional profiles and institute websites. A separate homepage is omitted where it could not be verified.

Portrait provenance is retained in `data/group.json`. Photographs and institutional logos retain their respective owners' rights; no blanket relicensing is implied.
