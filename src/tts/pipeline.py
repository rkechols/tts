import logging
import sys
from argparse import ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory

from tts.clean_text import clean_text
from tts.constants import AUDIO_DIR_DEFAULT, DATA_DIR_ROOT, TEXT_DIR_ORIGINAL_DEFAULT
from tts.logging_config import set_logging_config
from tts.run_tts import run_tts_many

LOGGER = logging.getLogger("tts.pipeline")


def run_pipeline(*, text_files_dir: Path, audio_files_dir: Path, vocab_phonemes_file: Path | None = None) -> bool:
    with TemporaryDirectory(dir=DATA_DIR_ROOT) as temp_dir:
        temp_dir_path = Path(temp_dir)
        clean_text(
            text_files_dir_in=text_files_dir,
            text_files_dir_out=temp_dir_path,
        )
        return run_tts_many(
            text_files_dir=temp_dir_path,
            audio_files_dir=audio_files_dir,
            vocab_phonemes_file=vocab_phonemes_file,
            force_reprocess=True,
        )


if __name__ == "__main__":
    set_logging_config()
    arg_parser = ArgumentParser(description="Convert text files to audio files")
    arg_parser.add_argument("--text-files-dir", "-t", type=Path, default=TEXT_DIR_ORIGINAL_DEFAULT)
    arg_parser.add_argument("--audio-files-dir", "-a", type=Path, default=AUDIO_DIR_DEFAULT)
    arg_parser.add_argument("--vocab", "-v", type=Path, default=None)
    args = arg_parser.parse_args()
    success_ = run_pipeline(
        text_files_dir=args.text_files_dir,
        audio_files_dir=args.audio_files_dir,
        vocab_phonemes_file=args.vocab,
    )
    sys.exit(0 if success_ else 1)
