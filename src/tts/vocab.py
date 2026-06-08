from pathlib import Path

import pydantic
import yaml
from yaml.error import YAMLError


class VocabLoadingError(Exception):
    """Raised when specialize vocab cannot be loaded"""


VocabPhonemesAdapter = pydantic.TypeAdapter(dict[str, str])


def load_vocab(vocab_phonemes_file: Path) -> dict[str, str]:
    try:
        with open(vocab_phonemes_file, "r", encoding="utf-8") as f:
            vocab_phonemes_raw = yaml.safe_load(f)
        return VocabPhonemesAdapter.validate_python(vocab_phonemes_raw)
    except (OSError, YAMLError, pydantic.ValidationError) as e:
        raise VocabLoadingError("Failed to load vocabulary file") from e


def standardize_vocab_token(s: str) -> str:
    return s.lower().replace("'", "")
