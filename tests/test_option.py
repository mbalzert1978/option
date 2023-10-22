from __future__ import annotations

from functools import partial
from typing import Callable

import pytest

from option import Maybe, Option, Some, UnwrapError, as_async_option, as_option


def test_ok_factories() -> None:
    instance: Option = Some(1)
    assert instance._value == 1
    assert instance.is_some() is True
    assert instance.is_none() is False


def test_err_factories() -> None:
    instance: Option = Maybe(2)
    assert instance._value is None
    assert instance.is_none() is True
    assert instance.is_some() is False


def test_eq() -> None:
    assert Some(1) == Some(1)
    assert Maybe(1) == Maybe(1)
    assert Maybe(1) != Some(1)
    assert Some(1) != Maybe(1)
    assert Some(1) != Some(2)
    assert Some(1) != "abc"
    assert Some("0") != Some(0)


def test_hash() -> None:
    assert len({Some(1), Maybe("2"), Some(1), Maybe("2")}) == 2
    assert len({Some(1), Some(2)}) == 2
    assert len({Some("a"), Maybe("a")}) == 2


def test_repr() -> None:
    o: Option = Some(123)
    n: Option = Maybe(-1)

    assert repr(o) == "Some(123)"
    assert o == eval(repr(o))

    assert repr(n) == "Maybe(None)"
    assert n == eval(repr(n))


def test_expect() -> None:
    o: Option = Some("yay")
    n: Option = Maybe("nay")
    assert o.expect("failure") == "yay"
    with pytest.raises(UnwrapError):
        n.expect("failure")


def test_unwrap() -> None:
    o: Option = Some("yay")
    n: Option = Maybe("nay")
    assert o.unwrap() == "yay"
    with pytest.raises(UnwrapError):
        n.unwrap()


def test_unwrap_or() -> None:
    o: Option = Some("yay")
    n: Option = Maybe("nay")
    assert o.unwrap_or("some_default") == "yay"
    assert n.unwrap_or("another_default") == "another_default"


def test_unwrap_or_else() -> None:
    o: Option = Some("yay")
    n: Option = Maybe("nay")
    assert o.unwrap_or_else(str.upper) == "yay"
    assert n.unwrap_or_else(lambda: "yay") == "yay"


def test_unwrap_or_raise() -> None:
    o: Option = Some("yay")
    n: Option = Maybe("nay")
    assert o.unwrap_or_raise(ValueError) == "yay"
    with pytest.raises(ValueError) as exc_info:
        n.unwrap_or_raise(ValueError)
    assert exc_info.value.args == (None,)


def test_map() -> None:
    o: Option = Some("yay")
    n: Option = Maybe("nay")
    assert o.map(str.upper).unwrap() == "YAY"
    assert n.map(str.upper).is_none() is True

    num: Option = Some(3)
    none_num: Option = Maybe(2)
    assert num.map(str).unwrap() == "3"
    assert none_num.map(str).is_none() is True


def test_map_or() -> None:
    o: Option = Some("yay")
    n: Option = Maybe("nay")
    assert o.map_or("hay", str.upper) == "YAY"
    assert n.map_or("hay", str.upper) == "hay"

    num: Option = Some(3)
    none_num: Option = Maybe(2)
    assert num.map_or("-1", str) == "3"
    assert none_num.map_or("-1", str) == "-1"


def test_map_or_else() -> None:
    k = 21
    o: Option = Some("yay")
    n: Option = Maybe("nay")
    assert o.map_or_else(lambda: 2 * k, str.upper) == "YAY"
    assert n.map_or_else(lambda: 2 * k, str.upper) == 42

    num: Option = Some(3)
    none_num: Option = Maybe(2)
    assert num.map_or_else(lambda: 2 * k, str) == "3"
    assert none_num.map_or_else(lambda: 2 * k, str) == 42


def test_and_then() -> None:
    start: Option = Some(2)
    assert start.and_then(sq).and_then(sq).unwrap() == 16
    assert start.and_then(sq).and_then(to_maybe).is_none() is True
    assert start.and_then(to_maybe).and_then(sq).is_none() is True

    assert start.and_then(sq_lambda).and_then(sq_lambda).unwrap() == 16
    assert start.and_then(sq_lambda).and_then(to_err_lambda).is_none() is True
    assert start.and_then(to_err_lambda).and_then(sq_lambda).is_none() is True


def test_or_else() -> None:

    def nobody():
        return Maybe(None)

    def vikings():
        return Some("vikings")

    assert Some("barbarians").or_else(vikings).unwrap() == "barbarians"
    assert Maybe(None).or_else(vikings).unwrap() == "vikings"
    assert Maybe(None).or_else(nobody).is_none() is True





def test_isinstance_result_type() -> None:
    o = Some("yay")
    n = Maybe("nay")
    assert isinstance(o, (Some, Maybe))
    assert isinstance(n, (Some, Maybe))
    assert not isinstance(1, (Some, Maybe))


def test_error_context() -> None:
    n = Maybe("nay")
    with pytest.raises(UnwrapError) as exc_info:
        n.unwrap()
    exc = exc_info.value
    assert exc.result is n


def test_slots() -> None:
    """
    Ok and Err have slots, so assigning arbitrary attributes fails.
    """
    o = Some("yay")
    n = Maybe("nay")
    with pytest.raises(AttributeError):
        o.some_arbitrary_attribute = 1  # type: ignore[attr-defined]
    with pytest.raises(AttributeError):
        n.some_arbitrary_attribute = 1  # type: ignore[attr-defined]


def test_as_option() -> None:
    """
    ``as_option()`` turns functions into ones that return a ``Option``.
    """

    @as_option
    def good(value: int) -> int:
        return value

    @as_option
    def bad(value: int) -> int:
        return None

    good_result: Option = good(123)
    bad_result: Option = bad(123)

    assert isinstance(good_result, Some)
    assert good_result.unwrap() == 123
    assert isinstance(bad_result, Maybe)
    assert bad_result.is_none() is True


def test_as_option_type_checking() -> None:
    """
    The ``as_option()`` is a signature-preserving decorator.
    """

    @as_option
    def f(a: int) -> int:
        return a

    res: Option[int, None]
    res = f(123)  # No mypy error here.
    assert res.unwrap() == 123


@pytest.mark.asyncio()
async def test_as_as_option() -> None:
    """
    ``as_as_option()`` turns functions into ones that return a ``Option``.
    """

    @as_async_option
    async def good(value: int) -> int:
        return value

    @as_async_option
    async def bad(value: int) -> int:
        return None

    good_result: Option = await good(123)
    bad_result: Option = await bad(123)

    assert isinstance(good_result, Some)
    assert good_result.unwrap() == 123
    assert isinstance(bad_result, Maybe)
    assert bad_result.is_none() is True


def sq(i: int) -> Option[int, int]:
    return Some(i**2)


def to_maybe(i: int) -> Option[int, int]:
    return Maybe(i)


# Lambda versions of the same functions, just for test/type coverage
sq_lambda: Callable[[int], Option[int, int]] = lambda i: Some(i * i)
to_err_lambda: Callable[[int], Option[int, int]] = lambda i: Maybe(i)
