from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional


__version__ = "21.0.dev0"


def main(args=None):
    # type: (Optional[List[str]]) -> int
    """This is an internal API only meant for use by pip's own console scripts.

    For additional details, see https://github.com/pypa/pip/issues/7498.
    """
    from pip._internal.utils.entrypoints import _wrapper

    return _wrapper(args)
