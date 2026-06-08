import logging
import sys
from argparse import ArgumentParser
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

import pydantic
import yaml
from yaml.error import YAMLError

if TYPE_CHECKING:
    from kokoro import KPipeline
from soundfile import SoundFile

from tts.kokoro.constants import (
    KOKORO_LANG_CODE,
    KOKORO_OUTPUT_SAMPLERATE,
    KOKORO_REPO_ID,
    KOKORO_VOICE_CODE,
    OUTPUT_FILE_SUFFIX,
    OUTPUT_FORMAT_KOKORO,
)
from tts.logging_config import set_logging_config

LOGGER = logging.getLogger("tts.kokoro")


class VocabLoadingError(Exception):
    """Raised when specialize vocab cannot be loaded"""


VocabPhonemesAdapter = pydantic.TypeAdapter(dict[str, str])


@cache
def load_kokoro(vocab_phonemes_file: Path | None = None) -> KPipeline:
    if vocab_phonemes_file is None:
        from kokoro import KPipeline  # noqa: PLC0415

        return KPipeline(lang_code=KOKORO_LANG_CODE, repo_id=KOKORO_REPO_ID)

    try:
        with open(vocab_phonemes_file, "r", encoding="utf-8") as f:
            vocab_phonemes_raw = yaml.safe_load(f)
        vocab_phonemes = VocabPhonemesAdapter.validate_python(vocab_phonemes_raw)
    except (OSError, YAMLError, pydantic.ValidationError) as e:
        raise VocabLoadingError("Failed to load vocabulary file") from e

    from tts.kokoro.kokoro_specialized import KPipelineSpecialized  # noqa: PLC0415

    return KPipelineSpecialized(vocab_phonemes, lang_code=KOKORO_LANG_CODE, repo_id=KOKORO_REPO_ID)


def run_kokoro(*, text_file: Path, audio_file_destination: Path, vocab_phonemes_file: Path | None = None):
    # https://huggingface.co/hexgrad/Kokoro-82M
    text = text_file.read_text(encoding="utf-8")
    pipeline = load_kokoro(vocab_phonemes_file=vocab_phonemes_file)
    audio_file_destination.parent.mkdir(parents=True, exist_ok=True)
    with SoundFile(
        str(audio_file_destination),
        "w",
        samplerate=KOKORO_OUTPUT_SAMPLERATE,
        channels=1,
        format=OUTPUT_FORMAT_KOKORO,
    ) as f:
        for result in pipeline(text, voice=KOKORO_VOICE_CODE, speed=0.9):
            audio = result.audio
            if audio is None:
                LOGGER.warning("Kokoro pipeline generator yielded element with no audio data")
                continue
            f.write(audio)


def run_kokoro_many(
    *,
    text_files_dir: Path,
    audio_files_dir: Path,
    vocab_phonemes_file: Path | None = None,
    force_reprocess: bool = False,
) -> bool:
    count_success = 0
    count_skip = 0
    count_failure = 0
    try:
        for text_file in sorted(text_files_dir.rglob("*.txt")):
            text_file_relative = text_file.relative_to(text_files_dir)
            audio_file_destination = audio_files_dir / text_file_relative.with_suffix(OUTPUT_FILE_SUFFIX)
            if not force_reprocess and audio_file_destination.is_file():
                count_skip += 1
                continue
            LOGGER.info(f"Processing {text_file} -> {audio_file_destination}")
            try:
                run_kokoro(
                    text_file=text_file,
                    audio_file_destination=audio_file_destination,
                    vocab_phonemes_file=vocab_phonemes_file,
                )
            except VocabLoadingError:
                raise  # Let this exception type propogate unchanged
            except Exception:
                count_failure += 1
                LOGGER.exception(f"Failed to process {text_file}")
            else:
                count_success += 1

    finally:
        with open("data/unknown-tokens.txt", "w", encoding="utf-8") as f:
            for token in sorted(load_kokoro(vocab_phonemes_file=vocab_phonemes_file).g2p.unknown_tokens):
                print(token, file=f)

    LOGGER.info(f"Successfully processed {count_success} file(s), {count_skip} skipped, {count_failure} failed")
    return count_failure == 0


if __name__ == "__main__":
    set_logging_config()
    arg_parser = ArgumentParser(description="Convert text files to audio files")
    arg_parser.add_argument("--text-files-dir", "-i", type=Path, required=True)
    arg_parser.add_argument("--audio-files-dir", "-o", type=Path, required=True)
    arg_parser.add_argument("--vocab", "-v", type=Path, default=None)
    arg_parser.add_argument("--force-reprocess", "-f", action="store_true")
    args = arg_parser.parse_args()
    success_ = run_kokoro_many(
        text_files_dir=args.text_files_dir,
        audio_files_dir=args.audio_files_dir,
        vocab_phonemes_file=args.vocab,
        force_reprocess=args.force_reprocess,
    )
    sys.exit(0 if success_ else 1)
