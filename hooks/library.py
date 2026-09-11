"""Discover category documents at build time, directly from docs folders."""
from pathlib import Path
import re
from urllib.parse import quote
from mkdocs.structure.files import File

SECTIONS = [
    ("Spark", "spark"), ("Python", "python"), ("Airflow", "airflow"),
    ("Books", "books"), ("Novels", "novels"), ("Others", "others"),
]
TITLES = {
    "spark/Spark_SQL_Getting_Started.md": "Spark SQL — Getting Started",
    "airflow/AirflowNotes.md": "Airflow Notes",
    "others/HBASE.md": "HBase",
}

def label(path):
    return re.sub(r"[-_]+", " ", Path(path).stem).strip().title()

def on_files(files, config):
    nav = [{"Library": "index.md"}]
    for title, folder in SECTIONS:
        index = f"{folder}/index.md"
        pages = sorted(
            (f for f in files.documentation_pages()
             if f.src_uri.startswith(folder + "/") and f.src_uri != index),
            key=lambda f: f.src_uri.casefold(),
        )
        entries = [{"Overview": index}]
        links = []
        for page in pages:
            name = TITLES.get(page.src_uri, label(page.src_uri))
            entries.append({name: page.src_uri})
            relative = page.src_uri[len(folder) + 1:]
            links.append(f"- [{name}]({quote(relative)})")
        downloads = sorted(
            (f for f in files if f.src_uri.startswith(folder + "/")
             and Path(f.src_uri).suffix.lower() in {".pdf", ".epub", ".docx", ".txt"}),
            key=lambda f: f.src_uri.casefold(),
        )
        for file in downloads:
            relative = file.src_uri[len(folder) + 1:]
            links.append(f"- [{label(file.src_uri)} · {Path(file.src_uri).suffix[1:].upper()}]({quote(relative)})")
        overview = files.get_file_from_path(index)
        body = overview.content_string if overview else f"# {title}\n"
        body += "\n\n## In this collection\n\n"
        body += "\n".join(links) if links else "No documents yet. This collection is ready for new additions."
        if overview:
            files.remove(overview)
        files.append(File.generated(config, index, content=body + "\n"))
        nav.append({title: entries})
    config.nav = nav
    return files

def on_post_build(config):
    """Keep previously shared website links working after the file moves."""
    redirects = {
        "spark/sql-getting-started": "../Spark_SQL_Getting_Started/",
        "airflow/airflow-notes": "../AirflowNotes/",
        "spark/hbase": "../../others/HBASE/",
    }
    for old, target in redirects.items():
        output = Path(config.site_dir) / old / "index.html"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta http-equiv="refresh" content="0; url={target}">'
            '<title>Document moved</title></head><body>'
            f'<p>This document has moved. <a href="{target}">Open document</a>.</p>'
            '</body></html>', encoding="utf-8",
        )
