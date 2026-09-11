# Anubhav's Library

**[Spark](docs/spark/index.md) · [Python](docs/python/index.md) · [Airflow](docs/airflow/index.md) · [Books](docs/books/index.md) · [Novels](docs/novels/index.md) · [Others](docs/others/index.md)**

A document library with category tabs, full-text Markdown search, light and dark themes, syntax highlighting, copyable code, and mobile navigation.

## Add documents

Upload Markdown files into the matching folder:

| Collection | Folder |
| --- | --- |
| Spark | `docs/spark/` |
| Python | `docs/python/` |
| Airflow | `docs/airflow/` |
| Books | `docs/books/` |
| Novels | `docs/novels/` |
| Others | `docs/others/` |

Choose **Add file → Upload files** on GitHub, then commit. Use readable names such as `window-functions.md`. New Markdown documents appear automatically in that collection's navigation and index after the next build; no configuration edits are needed. Nested folders work too.

PDF, EPUB, DOCX, and TXT files in these folders automatically receive download links on the collection page. Their contents are not included in full-text search. Put images beside a document and use relative Markdown links.

All documents are published directly from `docs/`. The existing notes now live at:

- [Airflow Notes](docs/airflow/AirflowNotes.md)
- [HBase](docs/others/HBASE.md)
- [Spark SQL — Getting Started](docs/spark/Spark_SQL_Getting_Started.md)

The old website URLs redirect to the new pages. Old GitHub file links at the repository root no longer point to files on `main`.

Edit each category's `index.md` for an introduction; the document list is appended automatically.

## Update an existing document on GitHub

1. Open the document under its `docs/` folder.
2. Click the pencil icon (**Edit this file**).
3. Edit the Markdown and use **Preview** to check formatting.
4. Click **Commit changes**, enter a short description, and commit to `main`. If you choose a new branch, merge its pull request to publish.
5. Open **Actions → Documentation** and wait for the build and deploy jobs to succeed.
6. Refresh the [live library](https://anubhav-singhal.github.io/documents/).

## Create or upload a new document

1. Open the relevant folder from the table above.
2. Choose **Add file → Create new file**, enter a name ending in `.md` (for example `window-functions.md`), and write your notes. Begin with a heading such as `# Window functions`.
3. Alternatively choose **Add file → Upload files** to upload an existing document.
4. Commit to `main` and wait for **Actions → Documentation** to finish. The collection page, navigation, and Markdown search index update automatically.

To move a file, open it, click the pencil, and change its path in the filename field (use `../` to navigate up a folder). Check relative image and document links after moving it, then commit. Moving or renaming a file changes its website URL; the three original migrations have redirects, but future moves need their own redirects if old links must remain valid.

## Publish with GitHub Pages

The public repository is configured to publish using **GitHub Actions**. Every change pushed or merged to `main` rebuilds and deploys the library. Pull requests only validate the build.

If a deployment fails, open the failed job under **Actions → Documentation** to see the error. After fixing the issue, commit again. No manual navigation edits are needed for documents in the six existing categories. For an entirely new category, add its name and folder to `SECTIONS` in `hooks/library.py` and create `docs/<folder>/index.md`.

## Preview locally

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

Open the local address printed by MkDocs. To check a publishable build, run `mkdocs build --strict`.

Powered by [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).
