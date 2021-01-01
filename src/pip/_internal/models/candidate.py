from typing import TYPE_CHECKING

from pip._vendor.packaging.version import parse as parse_version

from pip._internal.utils.models import KeyBasedCompareMixin

if TYPE_CHECKING:
    from pip._vendor.packaging.version import _BaseVersion

    from pip._internal.models.link import Link


class InstallationCandidate(KeyBasedCompareMixin):
    """Represents a potential "candidate" for installation.
    """

    __slots__ = ["name", "version", "link"]

    def __init__(self, name, version, link):
        # type: (str, str, Link) -> None
        self.name = name
        self.version = parse_version(version)  # type: _BaseVersion
        self.link = link

        super().__init__(
            key=(self.name, self.version, self.link),
            defining_class=InstallationCandidate
        )

    def __repr__(self):
        # type: () -> str
        return "<InstallationCandidate({!r}, {!r}, {!r})>".format(
            self.name, self.version, self.link,
        )

    def __str__(self):
        # type: () -> str
        return '{!r} candidate (version {} at {})'.format(
            self.name, self.version, self.link,
        )
