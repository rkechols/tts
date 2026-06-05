import logging
from argparse import ArgumentParser
from pathlib import Path

from tts.constants import TEXT_DIR_DEFAULT
from tts.logging_config import set_logging_config

LOGGER = logging.getLogger("tts.clean_text")

REPLACEMENTS = {
    "’": "'",  # noqa: RUF001
}


def clean_text(text_files_dir: Path):
    for file in text_files_dir.rglob("*.txt"):
        file_content = file.read_text(encoding="utf-8")
        file_content_original = file_content
        for old, new in REPLACEMENTS.items():
            file_content = file_content.replace(old, new)
        file.write_text(file_content, encoding="utf-8")
        if file_content != file_content_original:
            LOGGER.info(f"Modified {file}")


if __name__ == "__main__":
    set_logging_config()
    arg_parser = ArgumentParser(description="Clean text files in-place")
    arg_parser.add_argument("--text-files-dir", "-t", type=Path, default=TEXT_DIR_DEFAULT)
    args = arg_parser.parse_args()
    clean_text(text_files_dir=args.text_files_dir)
