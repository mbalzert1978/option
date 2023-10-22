from __future__ import annotations

from functools import partial
from typing import Callable

import pytest

from option import Maybe, Option, Some, UnwrapError, as_async_option, as_option


def test_ok_factories() -> None:
    instance: Option = Some(1)
    assert instance._value == 1
    assert instance.is_some() is True


def test_err_factories() -> None:
    instance: Option = Maybe(2)
    assert instance._value is None
    assert instance.is_none() is True


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


def test_value() -> None:
    some: Option = Some("haha")
    maybe: Option = Maybe("haha")

    assert some.value == "haha"
    assert maybe.value is None


def test_some() -> None:
    opt: Option = Some("haha")
    assert opt.is_some() is True
    assert opt.is_none() is False
    assert opt.value == "haha"


def test_maybe() -> None:
    opt: Option = Maybe(":(")
    assert opt.is_some() is False
    assert opt.is_none() is True
    assert opt.value is None


def test_some_method() -> None:
    o: Option = Some("yay")
    n: Option = Maybe("nay")
    assert o.some() == "yay"
    assert n.some() is None


def test_none_method() -> None:
    o: Option = Some("yay")
    n: Option = Maybe("nay")
    assert o.none() is None
    assert n.none() is None


def test_expect() -> None:
    o: Option = Some("yay")
    n: Option = Maybe("nay")
    assert o.expect("failure") == "yay"
    with pytest.raises(UnwrapError):
        n.expect("failure")


def test_expect_none() -> None:
    o: Option = Some("yay")
    n: Option = Maybe("nay")
    assert n.expect_none("hello") is None
    with pytest.raises(UnwrapError):
        o.expect_none("hello")


def test_unwrap() -> None:
    o: Option = Some("yay")
    n: Option = Maybe("nay")
    assert o.unwrap() == "yay"
    with pytest.raises(UnwrapError):
        n.unwrap()
def test_unwrap_none() -> None:
    o: Option = Some("yay")
    n: Option = Maybe("nay")
    assert n.unwrap_none() is None
    with pytest.raises(UnwrapError):
        o.unwrap_none()


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
    assert o.map(str.upper).some() == "YAY"
    assert n.map(str.upper).none() is None

    num: Option = Some(3)
    none_num: Option = Maybe(2)
    assert num.map(str).some() == "3"
    assert none_num.map(str).none() is None


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
    o: Option = Some("yay")
    n: Option = Maybe("nay")
    assert o.map_or_else("hay", str.upper) == "YAY"
    assert n.map_or_else("hay", str) == "None"
    assert n.map_or_else("hay", lambda _: None) == "hay"

    num: Option = Some(3)
    none_num: Option = Maybe(2)
    assert num.map_or_else("-1", str) == "3"
    assert none_num.map_or_else("-1", str) == "None"
    assert none_num.map_or_else("-1", lambda _: None) == "-1"


def test_and_then() -> None:
    start: Option = Some(2)
    assert start.and_then(sq).and_then(sq).some() == 16
    assert start.and_then(sq).and_then(to_maybe).some() is None
    assert start.and_then(to_maybe).and_then(sq).some() is None

    assert start.and_then(sq_lambda).and_then(sq_lambda).some() == 16
    assert start.and_then(sq_lambda).and_then(to_err_lambda).some() is None
    assert start.and_then(to_err_lambda).and_then(sq_lambda).some() is None


def test_or_else() -> None:
    start: Option = Some(2)
    sq2 = partial(sq, i=2)
    assert start.or_else(sq2).or_else(sq2).some() == 2
    assert start.or_else(partial(to_maybe, i=2)).or_else(sq).some() == 2

    assert start.or_else(sq_lambda).or_else(sq).some() == 2
    assert start.or_else(to_err_lambda).or_else(sq_lambda).some() == 2

def test_or_else_maybe() -> None:
    start:Option = Maybe(2)

    assert start.or_else(lambda:"2") == "2"


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


def test_as_result() -> None:
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
    assert bad_result.unwrap_none() is None


def test_as_result_type_checking() -> None:
    """
    The ``as_result()`` is a signature-preserving decorator.
    """

    @as_option
    def f(a: int) -> int:
        return a

    res: Option[int, None]
    res = f(123)  # No mypy error here.
    assert res.some() == 123


@pytest.mark.asyncio()
async def test_as_async_result() -> None:
    """
    ``as_async_result()`` turns functions into ones that return a ``Result``.
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
    assert bad_result.unwrap_none() is None


def sq(i: int) -> Option[int, int]:
    return Some(i**2)


def to_maybe(i: int) -> Option[int, int]:
    return Maybe(i)


# Lambda versions of the same functions, just for test/type coverage
sq_lambda: Callable[[int], Option[int, int]] = lambda i: Some(i * i)
to_err_lambda: Callable[[int], Option[int, int]] = lambda i: Maybe(i)
