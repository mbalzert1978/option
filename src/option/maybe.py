from typing import Callable, Literal, NoReturn, Self
from .exceptions import UnwrapError


class Maybe[T]:
    __match_args__ = ("some_value",)
    __slots__ = ("_value",)

    def __init__(self, _: T) -> None:
        self._value = None

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self._value)})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and self._value == other._value

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
    def some_value(self) -> None:
        return self._value

    def expect(self, _message: str) -> NoReturn:
        raise UnwrapError(self, _message)

    def expect_none(self, _message: str) -> None:
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

    def map[U](self, fn: Callable[[T], U]) -> Self[T]:
        return self

    def map_or[U](self, _default: U, fn: Callable[[T], U]) -> U:
        return _default

    def map_or_else[U](self, fn: Callable[[T | None], U]) -> U:
        return fn()

    def and_then[U](self, fn: Callable[[T], Self[U]]) -> Self[T]:
        return self

    def or_else(self, fn: Callable[[], Self[T]]) -> Self[T]:
        return fn()
