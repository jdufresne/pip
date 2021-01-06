"""Utilities to lazily create and visit candidates found.

Creating and visiting a candidate is a *very* costly operation. It involves
fetching, extracting, potentially building modules from source, and verifying
distribution metadata. It is therefore crucial for performance to keep
everything here lazy all the way down, so we only touch candidates that we
absolutely need, and not "download the world" when we only need one version of
something.
"""

import functools
import itertools
from typing import Callable, Iterator, Optional, Set

from pip._vendor.packaging.version import _BaseVersion
from pip._vendor.six.moves import collections_abc  # type: ignore

from .base import Candidate


def _deduplicated_by_version(candidates):
    # type: (Iterator[Candidate]) -> Iterator[Candidate]
    returned = set()  # type: Set[_BaseVersion]
    for candidate in candidates:
        if candidate.version in returned:
            continue
        returned.add(candidate.version)
        yield candidate


def _insert_installed(installed, others):
    # type: (Candidate, Iterator[Candidate]) -> Iterator[Candidate]
    """Iterator for ``FoundCandidates``.

    This iterator is used when the resolver prefers to upgrade an
    already-installed package. Candidates from index are returned in their
    normal ordering, except replaced when the version is already installed.

    The implementation iterates through and yields other candidates, inserting
    the installed candidate exactly once before we start yielding older or
    equivalent candidates, or after all other candidates if they are all newer.
    """
    installed_yielded = False
    for candidate in others:
        # If the installed candidate is better, yield it first.
        if not installed_yielded and installed.version >= candidate.version:
            yield installed
            installed_yielded = True
        yield candidate

    # If the installed candidate is older than all other candidates.
    if not installed_yielded:
        yield installed


class FoundCandidates(collections_abc.Sequence):
    """A lazy sequence to provide candidates to the resolver.

    The intended usage is to return this from `find_matches()` so the resolver
    can iterate through the sequence multiple times, but only access the index
    page when remote packages are actually needed. This improve performances
    when suitable candidates are already installed on disk.
    """
    def __init__(
        self,
        get_others,  # type: Callable[[], Iterator[Candidate]]
        installed,  # type: Optional[Candidate]
        prefers_installed,  # type: bool
    ):
        self._get_others = get_others
        self._installed = installed
        self._prefers_installed = prefers_installed

    def __getitem__(self, index):
        # type: (int) -> Candidate
        # Implemented to satisfy the ABC check. This is not needed by the
        # resolver, and should not be used by the provider either (for
        # performance reasons).
        raise NotImplementedError("don't do this")

    def __iter__(self):
        # type: () -> Iterator[Candidate]
        if not self._installed:
            candidates = self._get_others()
        elif self._prefers_installed:
            candidates = itertools.chain([self._installed], self._get_others())
        else:
            candidates = _insert_installed(self._installed, self._get_others())
        return _deduplicated_by_version(candidates)

    def __len__(self):
        # type: () -> int
        # Implemented to satisfy the ABC check. This is not needed by the
        # resolver, and should not be used by the provider either (for
        # performance reasons).
        raise NotImplementedError("don't do this")

    @functools.lru_cache(maxsize=1)
    def __bool__(self):
        # type: () -> bool
        if self._prefers_installed and self._installed:
            return True
        return any(self)

    __nonzero__ = __bool__  # XXX: Python 2.
