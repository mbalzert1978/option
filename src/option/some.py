from typing import Callable, Literal, NoReturn, Self
from .exceptions import UnwrapError


class Some[T]:
    __match_args__ = ("some_value",)
    __slots__ = ("_value",)

    def __init__(self, value: T) -> None:
        self._value = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self._value)})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and self._value == other._value

    def __ne__(self, other: object) -> bool:
        return not (self == other)

    def __hash__(self) -> int:
        return hash((True, self._value))

    def is_somee(self) -> Literal[True]:
        return True

    def is_none(self) -> Literal[False]:
        return False

    def some(self) -> T:
        return self._value

    def none(self) -> None:
        return None

    @property
    def some_value(self) -> T:
        return self._value

    def expect(self, _message: str) -> T:
        return self._value

    def expect_none(self, _message: str) -> NoReturn:
        raise UnwrapError(_message)

    def unwrap(self) -> T:
        return self._value

    def unwrap_none(self) -> NoReturn:
        msg = "Called `Some.unwrap_none()` on an `Some` value"
        raise UnwrapError(self, msg)

    def unwrap_or[U](self, _default: U) -> T:
        return self._value

    def unwrap_or_else[U](self, fn: Callable[[], U]) -> T:
        return self._value

    def unwrap_or_raise[E](self, exc: E) -> T:
        return self._value

    def map[U](self, fn: Callable[[T], U]) -> Self[U]:
        return Some(fn(self._value))

    def map_or[U](self, _default: U, fn: Callable[[T], U]) -> U:
        return fn(self._value)

    def map_or_else[U](self, fn: Callable[[T | None], U]) -> U:
        return fn(self._value)

    def and_then[U](self, fn: Callable[[T], Self[U]]) -> Self[U]:
        return fn(self._value)

    def or_else(self, fn: Callable[[], Self[T]]) -> Self[T]:
        return self
