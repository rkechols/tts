import dataclasses
import logging
from collections.abc import Mapping
from typing import Protocol, override

from kokoro import KPipeline
from misaki.token import MToken

LOGGER = logging.getLogger("tts.kokoro.kokoro_specialized")


class _G2P(Protocol):
    # Signature determined from usage in `kokoro.KPipeline`
    def __call__(self, text: str) -> tuple[str, list[MToken]]: ...


class _G2PWrapper(_G2P):
    @staticmethod
    def standardize_token(s: str) -> str:
        return s.lower().replace("'", "")

    def __init__(self, g2p: _G2P, specialized_vocab: Mapping[str, str]) -> None:
        super().__init__()
        self.g2p = g2p
        self.specialized_vocab = {
            self.standardize_token(token): phonemes
            for token, phonemes in specialized_vocab.items()
        }  # fmt: skip

    @override
    def __call__(self, text: str) -> tuple[str, list[MToken]]:
        s, tokens = self.g2p(text)
        for i, token in enumerate(tokens):
            if known_phonemes := self.specialized_vocab.get(self.standardize_token(token.text)):
                tokens[i] = dataclasses.replace(token, phonemes=known_phonemes)
        return s, tokens


class KPipelineSpecialized(KPipeline):
    def __init__(self, specialized_vocab: Mapping[str, str], /, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Initialize original self.g2p
        self.g2p = _G2PWrapper(self.g2p, specialized_vocab)  # Shadows the original
