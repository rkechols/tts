from pathlib import Path

TEXT_DIR_DEFAULT = Path("data/text")
AUDIO_DIR_DEFAULT = Path("data/audio")

# See docs for language and voice codes here: https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md
KOKORO_LANG_CODE = "a"
KOKORO_VOICE_CODE = "af_heart"

KOKORO_OUTPUT_SAMPLERATE = 24000

OUTPUT_FILE_SUFFIX = ".mp3"
OUTPUT_FORMAT_KOKORO = "MP3"
