"""xmlrpclib.Transport implementation
"""

import logging
import xmlrpc.client
from urllib import parse as urllib_parse

from pip._internal.exceptions import NetworkConnectionError
from pip._internal.network.utils import raise_for_status
from pip._internal.utils.typing import MYPY_CHECK_RUNNING

if MYPY_CHECK_RUNNING:
    from datetime import datetime
    from typing import Dict, Tuple, Union

    from pip._internal.network.session import PipSession

    _Marshallable = Union[None, bool, int, float, str, bytes, tuple, list, dict, datetime, DateTime, Binary]


logger = logging.getLogger(__name__)


class PipXmlrpcTransport(xmlrpc.client.Transport):
    """Provide a `xmlrpclib.Transport` implementation via a `PipSession`
    object.
    """

    def __init__(self, index_url, session, use_datetime=False):
        # type: (str, PipSession, bool) -> None
        super().__init__(use_datetime)
        index_parts = urllib_parse.urlparse(index_url)
        self._scheme = index_parts.scheme
        self._session = session

    def request(
        self,
        host,  # type: Union[Tuple[str, Dict[str, str]], str]
        handler,  # type: str
        request_body,  # type: bytes
        verbose=False,  # type: bool
    ):
        # type: (...) -> Tuple[Union[None, bool, int, float, str, bytes, Tuple[Any, ...], List[Any], Dict[Any, Any], datetime, DateTime, Binary], ...]
        parts = (self._scheme, host, handler, None, None, None)
        url = urllib_parse.urlunparse(parts)
        try:
            headers = {'Content-Type': 'text/xml'}
            response = self._session.post(url, data=request_body,
                                          headers=headers, stream=True)
            raise_for_status(response)
            self.verbose = verbose
            return self.parse_response(response.raw)
        except NetworkConnectionError as exc:
            assert exc.response
            logger.critical(
                "HTTP error %s while getting %s",
                exc.response.status_code, url,
            )
            raise
