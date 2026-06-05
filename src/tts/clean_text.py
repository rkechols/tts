import logging
import re
from argparse import ArgumentParser
from pathlib import Path

from tts.constants import TEXT_DIR_MODIFIED_DEFAULT, TEXT_DIR_ORIGINAL_DEFAULT
from tts.logging_config import set_logging_config

LOGGER = logging.getLogger("tts.clean_text")

BIONICLE_PREFIXES = ["Ga", "Ko", "Le", "Onu", "Po", "Ta"]

REPLACEMENTS = {
    re.compile(r"’"): "'",  # noqa: RUF001
    re.compile(r"\b(ga|ko|le|onu|po|ta)-", re.IGNORECASE): r"\1 ",
}


def clean_text(*, text_files_dir_in: Path, text_files_dir_out: Path):
    for file_in in text_files_dir_in.rglob("*.txt"):
        file_content = file_in.read_text(encoding="utf-8")
        file_content_original = file_content
        for old_re, new in REPLACEMENTS.items():
            file_content = old_re.sub(new, file_content)
        file_relative = file_in.relative_to(text_files_dir_in)
        file_out = text_files_dir_out / file_relative
        file_out.parent.mkdir(parents=True, exist_ok=True)
        file_out.write_text(file_content, encoding="utf-8")
        if file_content != file_content_original:
            LOGGER.info(f"Modified {file_in} -> {file_out}")


if __name__ == "__main__":
    set_logging_config()
    arg_parser = ArgumentParser(description="Clean text files in-place")
    arg_parser.add_argument("--text-files-dir-in", "-i", type=Path, default=TEXT_DIR_ORIGINAL_DEFAULT)
    arg_parser.add_argument("--text-files-dir-out", "-o", type=Path, default=TEXT_DIR_MODIFIED_DEFAULT)
    args = arg_parser.parse_args()
    clean_text(
        text_files_dir_in=args.text_files_dir_in,
        text_files_dir_out=args.text_files_dir_out,
    )
