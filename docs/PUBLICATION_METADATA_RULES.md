# Publication metadata rules

Applies to Research Notes, Working Papers, and Essays. Forecast series and dated forecast editions retain their separate issue-date, edition, and data-cutoff conventions.

## Index cards

- Display the existing content type and original publication date: `Research Note · Published October 15, 2026`.
- Omit author names. Authorship is displayed on the content page.
- When a substantive revision has an established later date, append `· Updated October 20, 2026`.
- Use the same dates as the content page, including featured duplicates.
- Retain titles, excerpts, topics, grouping, and existing ordering. This rule does not reorder the library.

## Content pages

- Preserve all author credits, including coauthors, and their existing order.
- Label the original date `Published`. Never replace it with a revision date.
- Add a separate `Updated` field for the latest substantive revision when that date is known. Do not display an empty field or repeat the publication date as an update.
- Format a known day as `October 15, 2026`. Preserve `October 2026` when only a month is established; do not invent a day.
- Wrap displayed dates in a `time` element with a matching ISO `datetime` attribute.
- Keep existing publication and modification metadata consistent with visible dates and their precision.
- A layout, navigation, analytics, or metadata cleanup does not establish a substantive revision date. Git commit timestamps and filesystem modification times are not publication dates.
- Unknown historical revision dates remain unset until supported by an editorial record.

## Maintenance

The content page is authoritative for the original date and any explicit `Updated` field. An existing, later `article:modified_time` is also recognized by the synchronization tool. Authors remain authoritative on content pages.

After editing a publication or revision date, run from the repository root:

```sh
python3 scripts/sync-publication-metadata.py --write
python3 scripts/sync-publication-metadata.py
```

The first command updates card dates and standardizes page dates. The second is read-only and exits unsuccessfully if synchronization is needed. The tool uses Python 3 and Beautiful Soup (`bs4`). No browser or site-build dependency is introduced.
