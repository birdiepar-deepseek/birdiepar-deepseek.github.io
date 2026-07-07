# Precision Analytica Static Site

Simple static website intended for GitHub Pages.

## Codex Workflow

Windows is the user-interface and file-exchange layer only. Active website work should happen on the Debian LXC, with WSL used as the local control shell:

```text
Windows Codex UI
  -> WSL Debian control shell
    -> ssh ai-debian
      -> work directly in /root/work/precision-analytica-site
```

For site changes, copy task memos into the LXC when useful, inspect and edit files in `/root/work/precision-analytica-site`, run validation there, then commit and push from the LXC repo. Do not treat Windows task folders as the source of truth for this site.

## Files

- `index.html`: home page
- `styles.css`: site styles
- `404.html`: GitHub Pages custom not-found page
- `.nojekyll`: disables Jekyll processing

## GitHub Pages Setup

Create a GitHub repository, then push these files to the `main` branch.

In GitHub:

```text
Settings -> Pages -> Build and deployment -> Source: Deploy from a branch
Branch: main
Folder: / root
```

For a user site, the repo name should normally be:

```text
<github-username>.github.io
```

For a project site, any repo name works and the site URL will usually be:

```text
https://<github-username>.github.io/<repo-name>/
```
