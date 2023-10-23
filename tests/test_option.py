from __future__ import annotations

import pytest

from option import Maybe, Option, Some, UnwrapError, as_async_option, as_option


def test_ok_factories() -> None:
    instance = Some(1)
    assert instance._value == 1
    assert instance.is_some()
    assert instance.is_none() is False


def test_err_factories() -> None:
    instance = Maybe(2)
    assert instance._value is None
    assert instance.is_none()
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
    o = Some(123)
    n = Maybe(-1)

    assert repr(o) == "Some(123)"
    assert o == eval(repr(o))

    assert repr(n) == "Maybe(None)"
    assert n == eval(repr(n))


def test_expect() -> None:
    o = Some("yay")
    n = Maybe("nay")
    assert o.expect("failure") == "yay"
    with pytest.raises(UnwrapError):
        n.expect("failure")


def test_unwrap() -> None:
    o = Some("yay")
    n = Maybe("nay")
    assert o.unwrap() == "yay"
    with pytest.raises(UnwrapError):
        n.unwrap()


def test_unwrap_or() -> None:
    o = Some("yay")
    n = Maybe("nay")
    assert o.unwrap_or("some_default") == "yay"
    assert n.unwrap_or("another_default") == "another_default"


def test_unwrap_or_else() -> None:
    o = Some("yay")
    n = Maybe("nay")
    assert o.unwrap_or_else(str.upper) == "yay"
    assert n.unwrap_or_else(lambda: "yay") == "yay"


def test_unwrap_or_raise() -> None:
    o = Some("yay")
    n = Maybe("nay")
    assert o.unwrap_or_raise(ValueError) == "yay"
    with pytest.raises(ValueError) as exc_info:
        n.unwrap_or_raise(ValueError)
    assert exc_info.value.args == (None,)


def test_map() -> None:
    o = Some("yay")
    n = Maybe("nay")
    assert o.map(str.upper).unwrap() == "YAY"
    assert n.map(str.upper).is_none()

    num = Some(3)
    none_num = Maybe(2)
    assert num.map(str).unwrap() == "3"
    assert none_num.map(str).is_none()


def test_map_or() -> None:
    o = Some("yay")
    n = Maybe("nay")
    assert o.map_or("hay", str.upper) == "YAY"
    assert n.map_or("hay", str.upper) == "hay"

    num = Some(3)
    none_num = Maybe(2)
    assert num.map_or("-1", str) == "3"
    assert none_num.map_or("-1", str) == "-1"


def test_map_or_else() -> None:
    k = 21
    o = Some("yay")
    n = Maybe("nay")
    assert o.map_or_else(lambda: 2 * k, str.upper) == "YAY"
    assert n.map_or_else(lambda: 2 * k, str.upper) == 42

    num = Some(3)
    none_num = Maybe(2)
    assert num.map_or_else(lambda: 2 * k, str) == "3"
    assert none_num.map_or_else(lambda: 2 * k, str) == 42


def test_and_then() -> None:
    def sq_then_to_string(x: int):
        return Some(str(x**2))

    assert Some(2).and_then(sq_then_to_string).unwrap_or("Fail") == "4"
    assert (
        Some(1_000_000).and_then(sq_then_to_string).unwrap_or("Fail") == "1000000000000"
    )
    assert Maybe(2).and_then(sq_then_to_string).is_none()


def test_or_else() -> None:
    def nobody():
        return Maybe(None)

    def vikings():
        return Some("vikings")

    assert Some("barbarians").or_else(vikings).unwrap() == "barbarians"
    assert Maybe(None).or_else(vikings).unwrap() == "vikings"
    assert Maybe(None).or_else(nobody).is_none()


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
    def bad(_: int) -> int:
        return None

    good_result = good(123)
    bad_result = bad(123)

    assert isinstance(good_result, Some)
    assert good_result.unwrap() == 123
    assert isinstance(bad_result, Maybe)
    assert bad_result.is_none()


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

    good_result = await good(123)
    bad_result = await bad(123)

    assert isinstance(good_result, Some)
    assert good_result.unwrap() == 123
    assert isinstance(bad_result, Maybe)
    assert bad_result.is_none()


def sq(i: int) -> Option[int, int]:
    return Some(i**2)


def to_maybe(i: int) -> Option[int, int]:
    return Maybe(i)
