import os
import tempfile
import threading
from pathlib import Path

DEFAULT_CACHE_SUBDIRECTORY = "musicdl"


class SimpleFileLock:
    """
    Cross-platform file lock.
    """

    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.Lock()

    def __enter__(self):
        self._lock.acquire()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(f"pid:{os.getpid()}\n")
        return self

    def __exit__(self, execution_type, execution_value, execution_traceback):
        try:
            if self.path.exists():
                try:
                    self.path.unlink()
                except Exception:
                    pass
        finally:
            self._lock.release()


def resolve_output_directory(output_directory: str | None = None) -> Path:
    """
    Figures out where to place the output files.
    """

    if output_directory:
        return Path(output_directory)
    user_override = os.environ["OUTPUT_DIRECTORY"]
    if user_override:
        return Path(user_override).expanduser().resolve()
    return Path().home() / "Downloads"


def resolve_cache_directory(cache_directory: str | None = None) -> Path:
    """
    Figures out where to place the cache files.
    """

    if cache_directory:
        return Path(cache_directory)
    user_override = os.environ["CACHE_DIRECTORY"]
    if user_override:
        return Path(user_override).expanduser().resolve()
    xdg = os.getenv("XDG_CACHE_HOME")
    if xdg:
        return Path(xdg).expanduser() / DEFAULT_CACHE_SUBDIRECTORY
    return Path().home() / ".cache" / DEFAULT_CACHE_SUBDIRECTORY
