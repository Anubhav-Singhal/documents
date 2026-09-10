"""Discover category documents at build time, including original root notes."""
from pathlib import Path
import re
from urllib.parse import quote
from mkdocs.structure.files import File

SECTIONS = [
    ("Spark", "spark"), ("Python", "python"), ("Airflow", "airflow"),
    ("Books", "books"), ("Novels", "novels"),
]
LEGACY = {
    "spark/sql-getting-started.md": ("Spark_SQL_Getting_Started.md", "Spark SQL — Getting Started"),
    "airflow/airflow-notes.md": ("AirflowNotes.md", "Airflow Notes"),
    "spark/hbase.md": ("HBASE.md", "HBase — Related Reading"),
}

def label(path):
    return re.sub(r"[-_]+", " ", Path(path).stem).strip().title()

def on_files(files, config):
    root = Path(config.config_file_path).parent
    for target, (source, title) in LEGACY.items():
        if files.get_file_from_path(target):
            raise ValueError(f"{target} is reserved for the original root document")
        original = (root / source).read_text(encoding="utf-8")
        files.append(File.generated(config, target, content=original))
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
            name = LEGACY[page.src_uri][1] if page.src_uri in LEGACY else label(page.src_uri)
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
