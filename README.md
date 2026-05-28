# Precision Analytica Static Site

Simple static website intended for GitHub Pages.

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
