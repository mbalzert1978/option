from __future__ import annotations

import abc
import functools
import typing

from result import Err, Ok, Result

T = typing.TypeVar("T")
E = typing.TypeVar("E")
N = typing.TypeVar("N")
U = typing.TypeVar("U")
F = typing.TypeVar("F")
P = typing.ParamSpec("P")


class OptionError(Exception):
    """Base result error."""


class UnwrapFailedError(OptionError):
    """Unwrap failed error."""


class TransposeError(OptionError):
    """Transpose failed error."""


class Option(abc.ABC, typing.Generic[T, N]):
    @abc.abstractmethod
    def and_then(self, f: typing.Callable[[T], Option[U, N]]) -> Option[U, N]: ...

    @abc.abstractmethod
    def expect(self, msg: str) -> T: ...

    @abc.abstractmethod
    def filter(self, predicate: typing.Callable[[T], bool]) -> Option[T, N]: ...

    @abc.abstractmethod
    def is_none(self) -> bool: ...

    @abc.abstractmethod
    def is_some(self) -> bool: ...

    @abc.abstractmethod
    def is_some_and(self, f: typing.Callable[[T], bool]) -> bool: ...

    @abc.abstractmethod
    def map(self, f: typing.Callable[[T], U]) -> Option[U, N]: ...

    @abc.abstractmethod
    def map_or(self, default: U, f: typing.Callable[[T], U]) -> U: ...

    @abc.abstractmethod
    def map_or_else(
        self, default: typing.Callable[[], U], f: typing.Callable[[T], U]
    ) -> U: ...

    @abc.abstractmethod
    def ok_or(self, err: E) -> Result[T, E]: ...

    @abc.abstractmethod
    def ok_or_else(self, err: typing.Callable[[], E]) -> Result[T, E]: ...

    @abc.abstractmethod
    def or_(self, optb: Option[T, N]) -> Option[T, N]: ...

    @abc.abstractmethod
    def or_else(self, f: typing.Callable[[], Option[T, N]]) -> Option[T, N]: ...

    @abc.abstractmethod
    def transpose(self) -> Result[Option[T, N], E]: ...

    @abc.abstractmethod
    def unwrap(self) -> T: ...

    @abc.abstractmethod
    def unwrap_or(self, default: T) -> T: ...

    @abc.abstractmethod
    def unwrap_or_else(self, f: typing.Callable[[], T]) -> T: ...

    @staticmethod
    def some(value: T) -> Option[T, typing.Any]:
        return Some(value)

    @staticmethod
    def none(value: N) -> Option[typing.Any, N]:
        return Maybe(value)

    @staticmethod
    def as_maybe(fn: typing.Callable[P, T]) -> typing.Callable[P, Option[T, N]]:
        """Decorates a function so that it returns a `Optional<T>` instead of `T`.
        # Examples:

        >>> @Result.as_maybe
        >>> def div(a: int, b: int) -> float:
        ...     return a / b
        >>> assert div(10, 2) == 5.0
        >>> assert div(10, 0) is None
        """

        @functools.wraps(fn)
        def inner(*args: P.args, **kwargs: P.kwargs) -> Option[T, N]:
            if (option := fn(*args, **kwargs)) is None:
                return Option.none(None)
            return Option.some(option)

        return inner


class Some(Option[T, typing.Any]):
    __slots__ = ("_inner_value",)
    __match_args__ = ("_inner_value",)

    UNWRAP_ERROR_MESSAGE = "Called `.%s` on an [`Some`] value: %s"
    TRANSPOSE_ERROR_MESSAGE = "Inner value: %s is not a Result."

    def __iter__(self) -> typing.Iterator[T]:
        yield self._inner_value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._inner_value!r})"

    def __hash__(self) -> int:
        return hash(self._inner_value) * 41

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and self._inner_value == other._inner_value

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __init__(self, inner_value: T) -> None:
        self._inner_value = inner_value

    def and_then(self, f: typing.Callable[[T], Option[U, N]]) -> Option[U, N]:
        return f(self._inner_value)

    def expect(self, msg: str) -> T:
        return self._inner_value

    def filter(self, predicate: typing.Callable[[T], bool]) -> Option[T, N]:
        if predicate(self._inner_value):
            return self
        return Option.none(typing.cast(N, None))

    def is_none(self) -> typing.Literal[False]:
        return False

    def is_some(self) -> typing.Literal[True]:
        return True

    def is_some_and(self, f: typing.Callable[[T], bool]) -> bool:
        return f(self._inner_value)

    def map(self, f: typing.Callable[[T], U]) -> Option[U, N]:
        return Option.some(f(self._inner_value))

    def map_or(self, default: U, f: typing.Callable[[T], U]) -> U:
        return f(self._inner_value)

    def map_or_else(
        self, default: typing.Callable[[], U], f: typing.Callable[[T], U]
    ) -> U:
        return f(self._inner_value)

    def ok_or(self, err: E) -> Result[T, E]:
        return Result.Ok(self._inner_value)

    def ok_or_else(self, f: typing.Callable[[], E]) -> Result[T, E]:
        return Result.Ok(self._inner_value)

    def or_(self, optb: Option[T, N]) -> Option[T, N]:
        return self

    def or_else(self, f: typing.Callable[[], Option[T, N]]) -> Option[T, N]:
        return self

    def transpose(self) -> Result[Option[T, N], E]:
        match self._inner_value:
            case Ok(x):
                return Result.Ok(Option.some(x))
            case Err(e):
                return Result.Err(e)
            case _:
                return Result.Ok(self)

    def unwrap(self) -> T:
        return self._inner_value

    def unwrap_or(self, default: T) -> T:
        return self._inner_value

    def unwrap_or_else(self, f: typing.Callable[[], T]) -> T:
        return self._inner_value


class Maybe(Option[typing.Any, N]):
    __slots__ = ("_inner_value",)
    __match_args__ = ("_inner_value",)

    UNWRAP_ERROR_MESSAGE = "Called `.%s` on an [`Maybe`] value."

    def __iter__(self) -> typing.Iterator[N]:
        yield self._inner_value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._inner_value!r})"

    def __hash__(self) -> int:
        return hash(self._inner_value) * 41

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and self._inner_value == other._inner_value

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __init__(self, inner_value: N) -> None:
        self._inner_value = inner_value

    def and_then(self, f: typing.Callable[[T], Option[U, N]]) -> Option[U, N]:
        return self

    def expect(self, msg: str) -> typing.NoReturn:
        raise UnwrapFailedError(msg)

    def filter(self, predicate: typing.Callable[[T], bool]) -> Option[T, N]:
        return self

    def is_none(self) -> typing.Literal[True]:
        return True

    def is_some(self) -> typing.Literal[False]:
        return False

    def is_some_and(self, f: typing.Callable[[T], bool]) -> typing.Literal[False]:
        return False

    def map(self, f: typing.Callable[[T], U]) -> Option[U, N]:
        return self

    def map_or(self, default: U, f: typing.Callable[[T], U]) -> U:
        return default

    def map_or_else(
        self, default: typing.Callable[[], U], f: typing.Callable[[T], U]
    ) -> U:
        return default()

    def ok_or(self, err: E) -> Result[T, E]:
        return Result.Err(err)

    def ok_or_else(self, err: typing.Callable[[], E]) -> Result[T, E]:
        return Result.Err(err())

    def or_(self, optb: Option[T, N]) -> Option[T, N]:
        return optb

    def or_else(self, f: typing.Callable[[], Option[T, N]]) -> Option[T, N]:
        return f()

    def transpose(self) -> Result[Option[T, N], E]:
        return Result.Ok(Option.some(typing.cast(T, None)))

    def unwrap(self) -> typing.NoReturn:
        raise UnwrapFailedError(self.UNWRAP_ERROR_MESSAGE % "unwrap")

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, f: typing.Callable[[], T]) -> T:
        return f()
