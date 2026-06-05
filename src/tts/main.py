import logging
from argparse import ArgumentParser
from pathlib import Path

# from kokoro import KPipeline
from tts.constants import AUDIO_DIR_DEFAULT, TEXT_DIR_DEFAULT
from tts.logging_config import set_logging_config


def process(*, text_file: Path, audio_file_destination: Path):
    logger = logging.getLogger("tts.main.process")
    logger.warning(f"TODO: process {text_file} -> {audio_file_destination}")


def main(*, text_files_dir: Path, audio_files_dir: Path, force_reprocess: bool = False):
    logger = logging.getLogger("tts.main.main")
    count_success = 0
    count_skip = 0
    count_failure = 0
    for text_file in text_files_dir.rglob("*.txt"):
        text_file_relative = text_file.relative_to(text_files_dir)
        audio_file_destination = audio_files_dir / text_file_relative.with_suffix(".mp3")
        if not force_reprocess and audio_file_destination.is_file():
            count_skip += 1
            continue
        logger.info(f"Processing {text_file} -> {audio_file_destination}")
        try:
            process(text_file=text_file, audio_file_destination=audio_file_destination)
        except Exception:
            count_failure += 1
            logger.exception(f"Failed to process {text_file}")
        else:
            count_success += 1
    logger.info(f"Successfully processed {count_success} file(s), {count_skip} skipped, {count_failure} failed")


if __name__ == "__main__":
    set_logging_config()
    arg_parser = ArgumentParser(description="Convert text files to audio files")
    arg_parser.add_argument("--text-files-dir", "-t", type=Path, default=TEXT_DIR_DEFAULT)
    arg_parser.add_argument("--audio-files-dir", "-a", type=Path, default=AUDIO_DIR_DEFAULT)
    arg_parser.add_argument("--force-reprocess", "-f", action="store_true")
    args = arg_parser.parse_args()
    main(
        text_files_dir=args.text_files_dir,
        audio_files_dir=args.audio_files_dir,
        force_reprocess=args.force_reprocess,
    )
