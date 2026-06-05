import importlib.util
from pathlib import Path

_NEW_KOKORO_INIT_CONTENTS = """\
__version__ = '0.9.4'

from .model import KModel
from .pipeline import KPipeline
"""


def _fix_kokoro_logging():
    if (kokoro_spec := importlib.util.find_spec("kokoro")) is None:
        raise RuntimeError("Cannot find package 'kokoro'")
    if (kokoro_origin := kokoro_spec.origin) is None:
        raise RuntimeError("Cannot find origin of package 'kokoro'")
    kokoro_init_file = Path(kokoro_origin)
    kokoro_dir = kokoro_init_file.parent

    kokoro_init_file_contents = kokoro_init_file.read_text(encoding="utf-8")
    if not kokoro_init_file_contents.startswith("__version__ = '0.9.4'"):
        raise ValueError("Failed to confirm exact version of kokoro is 0.9.4")

    kokoro_init_file.copy(kokoro_dir / "__init__.py.bak")
    kokoro_init_file.write_text(_NEW_KOKORO_INIT_CONTENTS, encoding="utf-8")

    for kokoro_py_file in kokoro_dir.rglob("*.py"):
        kokoro_py_file_contents = kokoro_py_file.read_text(encoding="utf-8")
        kokoro_py_file_contents_new = kokoro_py_file_contents.replace(
            "from loguru import logger",
            "import logging; logger = logging.getLogger(__name__)",
        )
        if kokoro_py_file_contents_new != kokoro_py_file_contents:
            kokoro_py_file.write_text(kokoro_py_file_contents_new, encoding="utf-8")


_fix_kokoro_logging()
