from typing import Any

from .option import Option


class UnwrapError(Exception):
    """
    Exception raised from ``.unwrap_<...>`` and ``.expect_<...>`` calls.

    The original ``Option`` can be accessed via the ``.result`` attribute, but
    this is not intended for regular use, as type information is lost:
    ``UnwrapError`` doesn't know about both ``T`` and ``E``, since it's raised
    from ``Some()`` or ``Maybe()`` which only knows about either ``T`` or ``E``,
    not both.
    """

    _result: Option[object, object]

    def __init__(self, result: Option[object, object], message: str) -> None:
        self._result = result
        super().__init__(message)

    @property
    def result(self) -> Option[Any, Any]:
        """
        Returns the original result.
        """
        return self._result
