import typing

from result import Result

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

class Option(typing.Generic[T, N]):
    def and_then(self, f: typing.Callable[[T], Option[U, N]]) -> Option[U, N]:
        """Returns [`Null`] if the option is [`Null`], otherwise calls `f` with the
        wrapped value and returns the result.
        Some languages call this operation flatmap.
        # Examples:

        >>> err = "Not a number"
        >>> assert Some(2).and_then(sq_then_to_string) == Some("4")
        >>> assert Null(err).and_then(sq_then_to_string) == Null(err)
        """
    def expect(self, msg: str) -> T:
        """
        Returns the contained [`Some`] value, consuming the `self` value.

        Raises
        ---
            Panics if the value is a [`Null`] with a custom panic message provided by `msg`.
        # Examples:

        >>> msg = "Something went wrong"
        >>> assert Some(10).expect(msg) == 10
        >>> with pytest.raises(UnwrapFailedError, match=msg):
        ...     Null("Emergency failure").expect(msg)
        """

    def filter(self, predicate: typing.Callable[[T], bool]) -> Option[T, N]:
        """
        Returns [`Null`] if the option is [`Null`], otherwise calls `predicate`
        with the wrapped value and returns:

        - [`Some(t)`] if `predicate` returns `true` (where `t` is the wrapped
          value), and
        - [`Null`] if `predicate` returns `false`.

        This function works similar to [`Iterator`]. You can imagine
        the `Option<T>` being an iterator over one or zero elements. `filter()`
        lets you decide which elements to keep.
        # Examples:

        >>> assert Some(10).filter(is_even) == Some(10)
        >>> assert Some(15).filter(is_even) == Null(None)
        >>> assert Null(10).filter(is_even) == Null(10)
        """
    def is_null(self) -> bool:
        """
        Returns `true` if the option is a [`Null`] value.

        # Examples:

        >>> assert Null(10).is_null()
        >>> assert not Some(10).is_null()
        """
    def is_some(self) -> bool:
        """
        Returns `true` if the option is a [`Some`] value.

        # Examples:

        >>> assert not Null(10).is_some()
        >>> assert Some(10).is_some()
        """
    def is_some_and(self, f: typing.Callable[[T], bool]) -> bool:
        """
        Returns `true` if the option is a [`Some`] and the value inside of it matches a predicate.

        # Examples:

        >>> assert Some(10).is_some_and(is_even)
        >>> assert not Some(15).is_some_and(is_even)
        >>> assert not Null("Something went wrong").is_some_and(is_even)
        """
    def map(self, f: typing.Callable[[T], U]) -> Option[U, N]:
        """
        Maps an `Option<T>` to `Option<U>` by applying a function to a contained value
         (if `Some`) or returns `Null` (if `Null`).

        # Examples:

        >>> assert Some(10).map(lambda i: i * 2) == Some(20)
        >>> assert Null("Nothing here").map(lambda i: i * 2) == Null("Nothing here")
        """
    def map_or(self, default: U, f: typing.Callable[[T], U]) -> U:
        """
        Returns the provided default result (if `Null`), or applies a function to the contained value (if `Some`).

        # Examples:

        >>> assert Some("foo").map_or(42, lambda v: len(v)) == 3
        >>> assert Null("bar").map_or(42, lambda v: len(v)) == 42
        """
    def map_or_else(
        self, default: typing.Callable[[], U], f: typing.Callable[[T], U]
    ) -> U:
        """
        Computes a default function result (if `Null`), or
        applies a different function to the contained value (if `Some`).

        # Examples:

        >>> assert Some("foo").map_or_else(lambda: 42, lambda v: len(v)) == 3
        >>> assert Null("bar").map_or_else(lambda: 42, lambda v: len(v)) == 42
        """
    def ok_or(self, err: E) -> Result[T, E]:
        """
        Transforms the `Option<T>` into a [`Result<T, E>`], mapping [`Some(v)`] to
        [`Ok(v)`] and [`Null`] to [`Err(err)`].

        Examples:

        >>> msg = "Something went wrong"
        >>> assert Some(10).ok_or(msg) == Result.Ok(10)
        >>> assert Null(10).ok_or(msg) == Result.Err(msg)
        """
    def ok_or_else(self, err: typing.Callable[[], E]) -> Result[T, E]:
        """
        Transforms the `Option<T>` into a [`Result<T, E>`], mapping [`Some(v)`] to
        [`Ok(v)`] and [`Null`] to [`Err(err())`].

        # Examples:

        >>> msg = "Something went wrong"
        >>> assert Some(10).ok_or_else(lambda: msg) == Result.Ok(10)
        >>> assert Null(10).ok_or_else(lambda: msg) == Result.Err(msg)
        """
    def or_(self, optb: Option[T, N]) -> Option[T, N]:
        """
        Returns the option if it contains a value, otherwise returns `optb`.

        # Examples

        >>> assert Some(10).or_(Some(20)) == Some(10)
        >>> assert Some(10).or_(Null(10)) == Some(10)
        >>> assert Null(10).or_(Some(20)) == Some(20)
        >>> assert Null(10).or_(Null(20)) == Null(10)
        """
    def or_else(self, f: typing.Callable[[], Option[T, N]]) -> Option[T, N]:
        """
        Returns the option if it contains a value, otherwise calls `f` and
        returns the result.

        # Examples

        >>> assert Some(10).or_else(lambda: Some(20)) == Some(10)
        >>> assert Some(10).or_else(lambda: Null(20)) == Some(10)
        >>> assert Null(10).or_else(lambda: Some(20)) == Some(20)
        """
    def transpose(self) -> Result[Option[T, N], E]:
        """
        Transposes an `Option` of a [`Result`] into a [`Result`] of an `Option`.

        Null will be mapped to:
        #### Ok(Null)
        Some(Ok(_)) and Some(Err(_)) will be mapped to:
        #### Ok(Some(_)) and Err(_).

        # Examples:

        >>> msg = "Something went wrong"
        >>> no_rslt = "No result"
        >>> assert Some(Result.Ok("foo")).transpose() == Result.Ok(Some("foo"))
        >>> assert Some(Result.Err(msg)).transpose() == Result.Err(msg)
        >>> assert Null(Result.Ok("foo")).transpose() == Result.Ok(Some(None))
        >>> assert Null(Result.Err(msg)).transpose() == Result.Ok(Some(None))
        >>> assert Some(no_rslt).transpose() == Result.Ok(Some(no_rslt))
        >>> assert Null(no_rslt).transpose() == Result.Ok(Some(None))
        """
    def unwrap(self) -> T:
        """
        Returns the contained [`Some`] value.

        Because this function may panic, its use is generally discouraged.
        Instead, prefer to use pattern matching and handle the [`Null`]
        case explicitly, or call [`unwrap_or`], [`unwrap_or_else`], or
        [`unwrap_or_default`].

        # Raises
            Raises UnwrapFailedError when the value equals None.

        # Examples

        >>> assert Some(10).unwrap() == 10
        >>> assert Null(10).unwrap() == 10
        Traceback (most recent call last):
            ...
            option.option.UnwrapFailedError: Called `.unwrap` on an [`Null`] value.

        """
    def unwrap_or(self, default: T) -> T:
        """
        Returns the contained [`Some`] value or a provided default.

        # Examples

        >>> assert Some(10).unwrap_or(42) == 10
        >>> assert Null(10).unwrap_or(42) == 42
        """
    def unwrap_or_else(self, f: typing.Callable[[], T]) -> T:
        """
        Returns the contained [`Some`] value or computes it from a closure.

        # Examples

        >>> assert Some(10).unwrap_or_else(lambda: 42) == 10
        >>> assert Null(10).unwrap_or_else(lambda: 42) == 42
        """
    @staticmethod
    def some(value: T) -> Option[T, N]:
        """
        Creates an `Option` instance that contains `Some` value.

        Examples:
        >>> assert Option.some(10) == Some(10)
        """
    @staticmethod
    def null(value: N) -> Option[T, N]:
        """
        Creates an `Option` instance that contains a `Null` value.

        Examples:
        >>> assert Option.null("Error") == Null("Error")
        """
    @staticmethod
    def as_option(fn: typing.Callable[P, T]) -> typing.Callable[P, Option[T, N]]:
        """
        Decorates a function so that it returns a `Optional<T>` instead of `T`.

        # Examples:

        >>> @Option.as_option
        >>> def div(a: int, b: int) -> float:
        ...     return a / b
        >>> assert div(10, 2) == 5.0
        >>> assert div(10, 0) is None
        """

class Some(Option[T, typing.Any]):
    def __iter__(self) -> typing.Iterator[T | None]: ...
    def __repr__(self) -> str: ...
    def __hash__(self) -> int: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __init__(self, inner_value: T) -> None: ...

class Null(Option[typing.Any, N]):
    def __iter__(self) -> typing.Iterator[N | None]: ...
    def __repr__(self) -> str: ...
    def __hash__(self) -> int: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __init__(self, inner_value: N) -> None: ...
