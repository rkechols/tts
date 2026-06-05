import logging
import sys
from argparse import ArgumentParser
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kokoro import KPipeline
from soundfile import SoundFile

from tts.constants import (
    AUDIO_DIR_DEFAULT,
    KOKORO_LANG_CODE,
    KOKORO_OUTPUT_SAMPLERATE,
    KOKORO_VOICE_CODE,
    OUTPUT_FILE_SUFFIX,
    OUTPUT_FORMAT_KOKORO,
    TEXT_DIR_DEFAULT,
)
from tts.logging_config import set_logging_config


@cache
def load_kokoro() -> KPipeline:
    from kokoro import KPipeline  # noqa: PLC0415

    return KPipeline(lang_code=KOKORO_LANG_CODE, repo_id="hexgrad/Kokoro-82M")


def process(*, text_file: Path, audio_file_destination: Path):
    logger = logging.getLogger("tts.main.process")
    text = text_file.read_text(encoding="utf-8")
    pipeline = load_kokoro()
    audio_file_destination.parent.mkdir(parents=True, exist_ok=True)
    with SoundFile(
        str(audio_file_destination),
        "w",
        samplerate=KOKORO_OUTPUT_SAMPLERATE,
        channels=1,
        format=OUTPUT_FORMAT_KOKORO,
    ) as f:
        for result in pipeline(text, voice=KOKORO_VOICE_CODE):
            audio = result.audio
            if audio is None:
                logger.warning("Kokoro pipeline generator yielded element with no audio data")
                continue
            f.write(audio)


def main(*, text_files_dir: Path, audio_files_dir: Path, force_reprocess: bool = False) -> bool:
    logger = logging.getLogger("tts.main.main")
    count_success = 0
    count_skip = 0
    count_failure = 0
    for text_file in text_files_dir.rglob("*.txt"):
        text_file_relative = text_file.relative_to(text_files_dir)
        audio_file_destination = audio_files_dir / text_file_relative.with_suffix(OUTPUT_FILE_SUFFIX)
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
    return count_failure == 0


if __name__ == "__main__":
    set_logging_config()
    arg_parser = ArgumentParser(description="Convert text files to audio files")
    arg_parser.add_argument("--text-files-dir", "-t", type=Path, default=TEXT_DIR_DEFAULT)
    arg_parser.add_argument("--audio-files-dir", "-a", type=Path, default=AUDIO_DIR_DEFAULT)
    arg_parser.add_argument("--force-reprocess", "-f", action="store_true")
    args = arg_parser.parse_args()
    success_ = main(
        text_files_dir=args.text_files_dir,
        audio_files_dir=args.audio_files_dir,
        force_reprocess=args.force_reprocess,
    )
    sys.exit(0 if success_ else 1)
