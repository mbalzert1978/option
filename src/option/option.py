from __future__ import annotations

import functools
from typing import Any, Awaitable, Callable, Literal, NoReturn, Protocol


class Option[T, N](Protocol):
    def __init__(self, value: T | N) -> None:...
    def is_some(self) -> bool:...
    def is_none(self) -> bool:...
    def expect(self, _: str) -> T:...
    def unwrap(self) -> T:...
    def unwrap_or[U](self, _: U) -> T | U:...
    def unwrap_or_else[U](self, _: Callable[[], U]) -> T | U:...
    def unwrap_or_raise[E](self, _: E) -> T:...
    def map[U](self, fn: Callable[[T], U]) -> Option[U, N]:...
    def map_or[U](self, _: U, fn: Callable[[T], U]) -> U:...
    def map_or_else[U](self, _: U, fn: Callable[[T | N], U]) -> U:...
    def and_then[U](self, fn: Callable[[T], Option[U, N]]) -> Option[U, N]:...
    def or_else(self, _: Callable[[T], Option[T, N]]) -> Option[T, N]:...

class Some[T]:
    __match_args__ = ("_value",)
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
        """Returns true if the option is a Some value."""
        return True

    def is_none(self) -> Literal[False]:
        """Returns true if the option is a None value."""
        return False

    def expect(self, _: str) -> T:
        """
        Returns the contained value, consuming the self value.

        Parameters
        ----------
        _message : str
            custom error message.

        Returns
        -------
        T
            raises `ValueError` when the value is None.
        """
        return self._value

    def unwrap(self) -> T:
        """
        Returns the contained value, consuming the self value.

        Because this function may raise, its use is generally discouraged.
        Instead, prefer to use pattern matching and handle the None case explicitly, or call
        [unwrap_or], [unwrap_or_else], or [unwrap_or_default].


        Returns
        -------
        T
            raises `UnwrapError` when the value is None.
        """
        return self._value

    def unwrap_or[U](self, _: U) -> T:
        """
        Returns the contained value, consuming the self value.

        Parameters
        ----------
        _default : U
            default value to return if the value is None.

        Returns
        -------
        T | U
        """
        return self._value

    def unwrap_or_else[U](self, _: Callable[[], U]) -> T:
        """
        Returns the contained value or computes it from a closure.

        Parameters
        ----------
        fn: Callable[[], U]
            callback function that takes to arguments.

        Returns
        -------
        T | U
        """
        return self._value

    def unwrap_or_raise[E](self, _: E) -> T:
        """
        Returns the contained value or raises a given exception.

        Parameters
        ----------
        exc: E
            Exception to raise if the value is None.

        Returns
        -------
        T
        """
        return self._value

    def map[U](self, fn: Callable[[T], U]) -> Option[U, None]:
        """
        Maps an Option[T] to Option[U] by applying a function to a contained value.

        Parameters
        ----------
        fn: Callable[[T], U]
            callback function that takes option[T] as argument.

        Returns
        -------
        Option[U]
        """
        return Some(fn(self._value))

    def map_or[U](self, _: U, fn: Callable[[T], U]) -> U:
        """
        Maps an Option[T] to Option[U] by applying a function to a contained value.

        Parameters
        ----------
        _default : U
            default value to return if the value is None.
        fn: Callable[[T], U]
            callback function that takes T as argument.

        Returns
        -------
        U
        """
        return fn(self._value)

    def map_or_else[U](self, _: U, fn: Callable[[T | None], U]) -> U:
        """
        Computes a default function result (if none), or applies a different function to the contained value (if any).

        Parameters
        ----------
        _default : U
            default value to return if the value is None.
        fn: Callable[[T], U]
            callback function that takes T as argument.

        Returns
        -------
        U
        """
        return fn(self._value)

    def and_then[U](self, fn: Callable[[T], Option[U, None]]) -> Option[U, None]:
        """
        Returns None if the option is None, otherwise calls f with the wrapped value and returns the result.


        Parameters
        ----------
        fn: Callable[[T], Option[T, None]
            callback function that takes T as argument and returns Option[T, None].

        Returns
        -------
        Option[U]
        """
        return fn(self._value)

    def or_else(self, _: Callable[[T], Option[T, None]]) -> Option[T, None]:
        """
        Returns the option if it contains a value, otherwise calls fn and returns the result.



        Parameters
        ----------
        fn: Callable[[], Option[T, None]]
            callback function that takes no arguments and returns Option[T, None].

        Returns
        -------
        Option[U]
        """
        return self


class Maybe[T]:
    __match_args__ = ("_value",)
    __slots__ = ("_value",)

    def __init__(self, _: T) -> None:
        self._value = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._value!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self._value == other._value

    def __ne__(self, other: object) -> bool:
        return not (self == other)

    def __hash__(self) -> int:
        """Just a big number to avoid hash collisions."""
        return hash((False, 65416518451651652132746854651513))

    def is_some(self) -> Literal[False]:
        """Returns true if the option is a Some value."""
        return False

    def is_none(self) -> Literal[True]:
        """Returns true if the option is a None value."""
        return True

    def expect(self, _message: str) -> NoReturn:
        """
        Returns the contained value, consuming the self value.

        Parameters
        ----------
        _message : str
            custom error message.

        Returns
        -------
        T
            raises `ValueError` when the value is None.
        """
        raise UnwrapError(self, _message)

    def unwrap(self) -> NoReturn:
        """
        Returns the contained value, consuming the self value.

        Because this function may raise, its use is generally discouraged.
        Instead, prefer to use pattern matching and handle the None case explicitly, or call
        [unwrap_or], [unwrap_or_else], or [unwrap_or_default].


        Returns
        -------
        T
            raises `UnwrapError` when the value is None.
        """
        msg = f"Called `Option.unwrap()` on an `None` value: {self._value!r}"
        raise UnwrapError(self, msg)

    def unwrap_or[U](self, _default: U) -> U:
        """
        Returns the contained value, consuming the self value.

        Parameters
        ----------
        _default : U
            default value to return if the value is None.

        Returns
        -------
        T | U
        """
        return _default

    def unwrap_or_else[U](self, fn: Callable[[], U]) -> U:
        """
        Returns the contained value or computes it from a closure.

        Parameters
        ----------
        fn: Callable[[], U]
            callback function that takes to arguments.

        Returns
        -------
        T | U
        """
        return fn()

    def unwrap_or_raise[E](self, exc: E) -> NoReturn:
        """
        Returns the contained value or raises a given exception.

        Parameters
        ----------
        exc: E
            Exception to raise if the value is None.

        Returns
        -------
        T
        """
        raise exc(self._value)

    def map[U](self, _: Callable[[T], U]) -> Option[U, None]:
        """
        Maps an Option[T] to Option[U] by applying a function to a contained value.

        Parameters
        ----------
        fn: Callable[[T], U]
            callback function that takes option[T] as argument.

        Returns
        -------
        Option[U]
        """
        return self

    def map_or[U](self, _default: U, _: Callable[[T], U]) -> U:
        """
        Maps an Option[T] to Option[U] by applying a function to a contained value.

        Parameters
        ----------
        _default : U
            default value to return if the value is None.
        fn: Callable[[T], U]
            callback function that takes T as argument.

        Returns
        -------
        U
        """
        return _default

    def map_or_else[
        U
    ](self, _default: Callable[[], U], _: Callable[[T | None], U]) -> U:
        """
        Computes a default function result (if none), or applies a different function to the contained value (if any).

        Parameters
        ----------
        _default : U
            default value to return if the value is None.
        fn: Callable[[T], U]
            callback function that takes T as argument.

        Returns
        -------
        U
        """
        return _default()

    def and_then[U](self, _: Callable[[T], Option[U, None]]) -> Option[U, None]:
        """
        Returns None if the option is None, otherwise calls f with the wrapped value and returns the result.


        Parameters
        ----------
        fn: Callable[[T], Option[T, None]
            callback function that takes T as argument and returns Option[T, None].

        Returns
        -------
        Option[U]
        """
        return self

    def or_else(self, fn: Callable[[], Option[T, None]]) -> Option[T, None]:
        """
        Returns the option if it contains a value, otherwise calls fn and returns the result.



        Parameters
        ----------
        fn: Callable[[], Option[T, None]]
            callback function that takes no arguments and returns Option[T, None].

        Returns
        -------
        Option[U]
        """
        return fn()


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
