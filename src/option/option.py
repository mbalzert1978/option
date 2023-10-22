from __future__ import annotations

import functools
from typing import Any, Awaitable, Callable, Literal, NoReturn, Self


class Some[T]:
    __match_args__ = ("value",)
    __slots__ = ("_value",)

    def __init__(self, value: T) -> None:
        self._value = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._value!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self._value == other._value

    def __ne__(self, other: object) -> bool:
        return not (self == other)

    def __hash__(self) -> int:
        return hash((True, self._value))

    def is_some(self) -> Literal[True]:
        return True

    def is_none(self) -> Literal[False]:
        return False

    def some(self) -> T:
        return self._value

    def none(self) -> None:
        return None

    @property
    def value(self) -> T:
        return self._value

    def expect(self, _message: str) -> T:
        return self._value

    def expect_none(self, _message: str) -> NoReturn:
        raise UnwrapError(self, _message)

    def unwrap(self) -> T:
        return self._value

    def unwrap_none(self) -> NoReturn:
        msg = "Called `Some.unwrap_none()` on an `Some` value"
        raise UnwrapError(self, msg)

    def unwrap_or[U](self, _: U) -> T:
        return self._value

    def unwrap_or_else[U](self, _: Callable[[], U]) -> T:
        return self._value

    def unwrap_or_raise[E](self, _: E) -> T:
        return self._value

    def map[U](self, fn: Callable[[T], U]) -> Self:
        return Some(fn(self._value))

    def map_or[U](self, _: U, fn: Callable[[T], U]) -> U:
        return fn(self._value)

    def map_or_else[U](self, _: U, fn: Callable[[T | None], U]) -> U:
        return fn(self._value)

    def and_then(self, fn: Callable[[T], Option]) -> Self:
        return fn(self._value)

    def or_else(self, _: Callable[[], Option]) -> Self:
        return self


class Maybe[N]:
    __match_args__ = ("value",)
    __slots__ = ("_value",)

    def __init__(self, _: N) -> None:
        self._value = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._value!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self._value == other._value

    def __ne__(self, other: object) -> bool:
        return not (self == other)

    def __hash__(self) -> int:
        return hash((False, self._value))

    def is_some(self) -> Literal[False]:
        return False

    def is_none(self) -> Literal[True]:
        return True

    def some(self) -> None:
        return self._value

    def none(self) -> None:
        return self._value

    @property
    def value(self) -> None:
        return self._value

    def expect(self, _message: str) -> NoReturn:
        raise UnwrapError(self, _message)

    def expect_none(self, _: str) -> None:
        return self._value

    def unwrap(self) -> NoReturn:
        msg = f"Called `Option.unwrap()` on an `Maybe` value: {self._value!r}"
        raise UnwrapError(self, msg)

    def unwrap_none(self) -> None:
        return self._value

    def unwrap_or[U](self, _default: U) -> U:
        return _default

    def unwrap_or_else[U](self, fn: Callable[[], U]) -> U:
        return fn()

    def unwrap_or_raise[E](self, exc: E) -> NoReturn:
        raise exc(self._value)

    def map[U](self, _: Callable[[N], U]) -> Self:
        return self

    def map_or[U](self, _default: U, _: Callable[[N], U]) -> U:
        return _default

    def map_or_else[U](self, _default: U, fn: Callable[[N | None], U]) -> U:
        return fn(self._value) or _default

    def and_then[U](self, _: Callable[[N], Option]) -> Self:
        return self

    def or_else(self, fn: Callable[[], Option]) -> Self:
        return fn()


type Option[T, N] = Some[T] | Maybe[N]


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


def as_option[P, R](f: Callable[[P], R]) -> Callable[[P], Option[R, None]]:
    """
    Make a decorator to turn a function into one that returns a ``Option``.

    Regular return values are turned into ``Some(return_value)``.
    None are turned into ``Maybe(return_value)``.
    """

    @functools.wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Option[R, None]:
        if (result := f(*args, **kwargs)) is None:
            return Maybe(result)
        return Some(result)

    return wrapper


def as_async_option[
    P,
    R,
](f: Callable[[P], Awaitable[R]]) -> Callable[[P], Awaitable[Option[R, None]]]:
    """
    Make a decorator to turn an async function into one that returns a ``Option``.

    Regular return values are turned into ``Some(return_value)``.
    None are turned into ``Maybe(return_value)``.
    """

    @functools.wraps(f)
    async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Option[R, None]:
        if (result := await f(*args, **kwargs)) is None:
            return Maybe(result)
        return Some(result)

    return async_wrapper
