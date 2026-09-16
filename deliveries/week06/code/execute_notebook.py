"""Execute EDA_Week06.ipynb in-place using the Week 6 environment."""
from pathlib import Path

import nbformat
from nbclient import NotebookClient


HERE = Path(__file__).resolve().parent
PATH = HERE / "EDA_Week06.ipynb"


def main():
    notebook = nbformat.read(PATH, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=300,
        kernel_name="python3",
        resources={"metadata": {"path": str(HERE)}},
    )
    client.execute()
    nbformat.write(notebook, PATH)
    print(f"Notebook executed -> {PATH}")


if __name__ == "__main__":
    main()
