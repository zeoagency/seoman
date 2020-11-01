from pathlib import Path
from typing import List, Union

import typer  # type: ignore


def create_toml_list() -> List[str]:
    """Create a list from all the files that ends with .toml"""
    path = Path(Path.home() / ".queries").glob("*.toml")
    files: Union[List[Path], List[str]] = [file for file in path if file.is_file()]

    # Files comes like PosixPath("/some/path.toml") we are converting it to just filename without extension
    files = [str(file).split("/")[-1].split(".")[0] for file in files]

    if len(files) >= 1:
        return files

    typer.secho("0 query found, add some.", bold=True, fg=typer.colors.BRIGHT_RED)
    exit()
