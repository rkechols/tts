from argparse import ArgumentParser
from pathlib import Path

from src.tts.constants import DATA_DIR_DEFAULT


REPLACEMENTS = {
    "’": "'",
}


def clean_text(data_dir: Path):
    for file in data_dir.rglob("*.txt"):
        file_content = file.read_text(encoding="utf-8")
        file_content_original = file_content
        for old, new in REPLACEMENTS.items():
            file_content = file_content.replace(old, new)
        file.write_text(file_content, encoding="utf-8")
        if file_content != file_content_original:
            print(f"Modified {file}")


if __name__ == "__main__":
    arg_parser = ArgumentParser(description="Clean text files in-place")
    arg_parser.add_argument("--data-dir", "-d", type=Path, default=DATA_DIR_DEFAULT)
    args = arg_parser.parse_args()
    clean_text(args.data_dir)
