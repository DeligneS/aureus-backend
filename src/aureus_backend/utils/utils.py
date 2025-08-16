from pathlib import Path
from typing import Union


def read_file(file_path: Union[str, Path]) -> str:
    """
    Read contents from a file.

    Args:
        file_path (Union[str, Path]): Path to the file to read

    Returns:
        str: Contents of the file
    """
    path = Path(file_path)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
