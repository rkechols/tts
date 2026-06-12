import logging
import re
from argparse import ArgumentParser
from pathlib import Path

import cmudict
import yaml

from tts.logging_config import set_logging_config

LOGGER = logging.getLogger("tts.clean_text")

DICTIONARY = set(cmudict.words())

REGEX_REPLACEMENTS = {
    re.compile("[‘’]"): "'",  # noqa: RUF001
    re.compile("[“”]"): '"',
    re.compile("[‐—–]"): "-",  # noqa: RUF001
    re.compile("…"): "...",
    re.compile("[\xa0\xad]"): " ",
    re.compile(r"\b(av|exo|ga|ko|le|onu|po|ta)-", re.IGNORECASE): r"\1 ",
    re.compile(r"\ba+(r?)r*(g?)g*h+\b", re.IGNORECASE): r"a\1\2h",
    re.compile("XV-I"): "XV-1",
}


def _load_replacements_yaml() -> dict[str, str]:
    with open(Path(__file__).parent / "replacements.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


MANUAL_REPLACEMENTS = _load_replacements_yaml()


def has_alpha(s: str) -> bool:
    return any(c.isalpha() for c in s)


def clean_text(*, text_files_dir_in: Path, text_files_dir_out: Path):
    for file_in in sorted(text_files_dir_in.rglob("*.txt")):
        file_content = file_in.read_text(encoding="utf-8")
        file_content_original = file_content

        for old_re, new in REGEX_REPLACEMENTS.items():
            file_content = old_re.sub(new, file_content)

        file_content_list: list[str] = []
        cursor = 0
        for match in re.finditer(r"\w(?:\w|'(?=\w))*", file_content):
            file_content_list.append(file_content[cursor : match.start()])

            token = file_content[match.start() : match.end()]
            token_lower = token.lower()

            if token_lower in MANUAL_REPLACEMENTS:
                token = MANUAL_REPLACEMENTS[token_lower]
            file_content_list.append(token)
            cursor = match.end()
        file_content_list.append(file_content[cursor:])
        file_content = "".join(file_content_list)

        file_relative = file_in.relative_to(text_files_dir_in)
        file_out = text_files_dir_out / file_relative
        file_out.parent.mkdir(parents=True, exist_ok=True)
        file_out.write_text(file_content, encoding="utf-8")
        if file_content != file_content_original:
            LOGGER.info(f"Modified {file_in} -> {file_out}")


if __name__ == "__main__":
    set_logging_config()
    arg_parser = ArgumentParser(description="Clean text files")
    arg_parser.add_argument("--text-files-dir-in", "-i", type=Path, required=True)
    arg_parser.add_argument("--text-files-dir-out", "-o", type=Path, required=True)
    args = arg_parser.parse_args()
    clean_text(
        text_files_dir_in=args.text_files_dir_in,
        text_files_dir_out=args.text_files_dir_out,
    )
