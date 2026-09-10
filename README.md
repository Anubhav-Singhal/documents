# Anubhav's Library

**[Spark](docs/spark/index.md) · [Python](docs/python/index.md) · [Airflow](docs/airflow/index.md) · [Books](docs/books/index.md) · [Novels](docs/novels/index.md)**

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

Choose **Add file → Upload files** on GitHub, then commit. Use readable names such as `window-functions.md`. New Markdown documents appear automatically in that collection's navigation and index after the next build; no configuration edits are needed. Nested folders work too.

PDF, EPUB, DOCX, and TXT files in these folders automatically receive download links on the collection page. Their contents are not included in full-text search. Put images beside a document and use relative Markdown links.

The original root documents remain the source of truth: edit `Spark_SQL_Getting_Started.md`, `AirflowNotes.md`, or `HBASE.md` as before. The build includes them under Spark and Airflow without maintaining duplicate copies. HBase appears as related reading under Spark. The three generated paths listed in `hooks/library.py` are reserved.

Edit each category's `index.md` for an introduction; the document list is appended automatically.

## Publish with GitHub Pages

1. Merge this documentation change.
2. Open **Settings → Pages → Build and deployment** and select **GitHub Actions**.
3. Open **Actions → Documentation → Run workflow** on `main` if the initial deployment ran before Pages was configured.
4. Open the URL reported by the successful deployment. The expected address is https://Anubhav-Singhal.github.io/documents/.

The repository was private when this setup was prepared. Private-repository Pages availability depends on your GitHub plan; see [GitHub Pages availability](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages). Review the documents you intend to publish before enabling Pages. Repository visibility is not changed by this setup.

Every pull request builds the documentation for validation. Changes merged to `main` publish automatically once Pages is enabled.

## Preview locally

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

Open the local address printed by MkDocs. To check a publishable build, run `mkdocs build --strict`.

Powered by [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).
