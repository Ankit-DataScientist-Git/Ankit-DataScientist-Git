# Profile Architecture

This repository is a lightweight, automated GitHub profile system. It keeps presentation in the profile README and keeps generated assets reproducible through GitHub Actions.

## Components

```text
README.md
  ├── theme-aware terminal banner
  ├── generated profile metrics SVG
  ├── contribution snake SVGs
  └── contact / professional sections

.github/workflows/snake.yml
  ├── Platane/snk
  ├── profile metric generator
  └── published assets on output branch

.github/scripts/generate_profile_cards.py
  └── reads GitHub API data and writes profile-stats.svg
```

## Request / generation flow

```text
GitHub Actions trigger
        │
        ▼
      snake.yml
        │
        ├── fetch contribution data
        │
        ├── generate light/dark snake SVGs
        │
        ├── call GitHub REST API for profile/repository metrics
        │
        └── publish dist/ to output branch
                       │
                       ▼
                  raw GitHub URLs
                       │
                       ▼
                  profile README
```

## Credential handling

The workflow uses GitHub's built-in workflow token:

```yaml
permissions:
  contents: write
```

The generator receives the workflow credential through an environment variable:

```yaml
env:
  GH_USERNAME: ${{ github.repository_owner }}
  GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

The Python generator only adds an `Authorization: Bearer ...` header when `GH_TOKEN` is present. It does not write the token into generated SVG files or README content.

The publishing action receives the same workflow token through its environment. No personal access token is hard-coded into the repository.

## Why generated SVG assets are used

The profile README should remain lightweight and reliable. Generated SVGs let the profile render from static repository assets instead of requiring a third-party stats service to respond every time a recruiter opens the profile.

## Profile phases from the setup specification

### Phase 1 — Banner

The repository includes dark/light terminal-style banner assets. The banner uses a terminal window, a visual map, system information, a live indicator, and theme-specific colors. A personal portrait can be substituted later without changing the README structure.

### Phase 2 — Stats

Profile metrics are generated during Actions and published as `profile-stats.svg`. This avoids dependence on the public GitHub Readme Stats endpoint at page-render time.

### Phase 3 — Contribution snake

`snake.yml` runs on a 12-hour schedule, on push to `main`, and through `workflow_dispatch`. It creates light/dark SVGs and publishes them to the `output` branch.

### Phase 4 — Social badges

The README contains clickable contact badges. Account-specific links should only be added when the real URL is known.

## Design principles

- Keep credentials out of source files.
- Prefer reproducible automation over manual asset editing.
- Keep generated assets separate from source scripts.
- Support both GitHub light and dark themes.
- Make the first screen readable by a technical recruiter in a quick scan.
- Only claim skills, projects, links, and achievements that can be verified from the profile or repository.
