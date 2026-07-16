from importlib.metadata import PackageNotFoundError, version

from ninja_search.searching import MAX_SEARCH_TERMS, searching

try:
    __version__ = version("django-ninja-search")
except PackageNotFoundError:  # pragma: no cover - not installed
    __version__ = "0.0.0"

__all__ = ["MAX_SEARCH_TERMS", "__version__", "searching"]
