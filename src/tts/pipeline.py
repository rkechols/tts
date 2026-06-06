import logging
import sys
from argparse import ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory

from tts.clean_text.main import clean_text
from tts.kokoro.main import run_kokoro_many
from tts.logging_config import set_logging_config

LOGGER = logging.getLogger("tts.pipeline")


def run_pipeline(*, text_files_dir: Path, audio_files_dir: Path, vocab_phonemes_file: Path | None = None) -> bool:
    with TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        clean_text(
            text_files_dir_in=text_files_dir,
            text_files_dir_out=temp_dir_path,
        )
        return run_kokoro_many(
            text_files_dir=temp_dir_path,
            audio_files_dir=audio_files_dir,
            vocab_phonemes_file=vocab_phonemes_file,
            force_reprocess=True,
        )


if __name__ == "__main__":
    set_logging_config()
    arg_parser = ArgumentParser(description="Convert text files to audio files")
    arg_parser.add_argument("--text-files-dir", "-i", type=Path, required=True)
    arg_parser.add_argument("--audio-files-dir", "-o", type=Path, required=True)
    arg_parser.add_argument("--vocab", "-v", type=Path, default=None)
    args = arg_parser.parse_args()
    success_ = run_pipeline(
        text_files_dir=args.text_files_dir,
        audio_files_dir=args.audio_files_dir,
        vocab_phonemes_file=args.vocab,
    )
    sys.exit(0 if success_ else 1)
