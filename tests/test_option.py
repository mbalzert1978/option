from __future__ import annotations

import re

import pytest
from result import Result

from option import Null, Option, Some, UnwrapFailedError


def parse(s: str) -> Option[float, str]:
    try:
        i = float(s)
        return Some(i)
    except ValueError:
        return Null("Invalid format")
    except OverflowError:
        return Null("Number too large or too small")


@Option.as_option
def div(a: int, b: int) -> float | None:
    if b == 0:
        return None
    return a / b


def get100() -> Option[int, int]:
    return Some(100)


def get_nothing() -> Option[int, int]:
    return Null(0)


def is_even(x: int) -> bool:
    return x % 2 == 0


def sq_then_to_string(x: int) -> Option[str, str]:
    try:
        sq = x * x
        return Some(str(sq))
    except Exception:
        return Null("Overflowed")


def test_and_then_when_value_should_call_the_given_function_or_return_none() -> None:
    err = "Not a number"
    assert Some(2).and_then(sq_then_to_string) == Some("4")
    assert Null(err).and_then(sq_then_to_string) == Null(err)


def test_expect_when_value_should_return_the_value_or_throws_an_error_with_the_given_message():
    msg = "Something went wrong"
    assert Some(10).expect(msg) == 10
    with pytest.raises(UnwrapFailedError, match=msg):
        Null("Emergency failure").expect(msg)


def test_option_filter_when_predicate_is_called_should_return_some_if_true_and_null_if_false() -> (
    None
):
    assert Some(10).filter(is_even) == Some(10)
    assert Some(15).filter(is_even) == Null(None)
    assert Null(10).filter(is_even) == Null(10)


def test_is_null_when_null_value_should_return_true() -> None:
    assert Null(10).is_null()
    assert not Some(10).is_null()


def test_is_some_when_value_should_return_true() -> None:
    assert not Null(10).is_some()
    assert Some(10).is_some()


def test_is_some_and_when_some_value_should_match_predicate() -> None:
    assert Some(10).is_some_and(is_even)
    assert not Some(15).is_some_and(is_even)
    assert not Null("Something went wrong").is_some_and(is_even)


def test_map_on_option_should_map_option_te_to_option_ue_by_applying_a_function_to_a_contained_some_value_leaving_an_null_untouched() -> (
    None
):
    assert Some(10).map(lambda i: i * 2) == Some(20)
    assert Null("Nothing here").map(lambda i: i * 2) == Null("Nothing here")


def test_map_or_when_option_should_apply_a_function_to_contained_value_or_default():
    assert Some("foo").map_or(42, lambda v: len(v)) == 3
    assert Null("bar").map_or(42, lambda v: len(v)) == 42


def test_map_or_else_when_option_should_apply_a_function_to_contained_value_or_apply_fallback_function():
    k = 21
    assert Some("foo").map_or_else(lambda: k * 2, lambda v: len(v)) == 3
    assert Null("bar").map_or_else(lambda: k * 2, lambda v: len(v)) == 42


def test_option_ok_or_when_called_should_map_option_to_result() -> None:
    assert Some(10).ok_or("Something went wrong") == Result.Ok(10)
    assert Null(10).ok_or("Something went wrong") == Result.Err("Something went wrong")


def test_option_ok_or_else_when_called_should_map_some_to_ok_and_null_to_err() -> None:
    assert Some(10).ok_or_else(lambda: "Something went wrong") == Result.Ok(10)
    assert Null(10).ok_or_else(lambda: "Something went wrong") == Result.Err(
        "Something went wrong"
    )


def test_option_or_when_called_should_return_option_if_contained_value_otherwise_optb() -> (
    None
):
    assert Some(2).or_(Null(None)) == Some(2)
    assert Null(None).or_(Some(100)) == Some(100)
    assert Some(2).or_(Some(100)) == Some(2)
    assert Null(None).or_(Null(None)) == Null(None)


def test_or_else_when_null_should_call_the_given_function_or_return_the_some_value():
    assert Some(2).or_else(get100).or_else(get100) == Some(2)
    assert Some(2).or_else(get_nothing).or_else(get100) == Some(2)
    assert Null(3).or_else(get100).or_else(get_nothing) == Some(100)
    assert Null(3).or_else(get_nothing).or_else(get_nothing) == Null(0)


def test_transpose_when_option_of_result_should_return_result_of_option() -> None:
    assert Some(Result.Ok("foo")).transpose() == Result.Ok(Some("foo"))
    assert Some(Result.Err("Nothing here")).transpose() == Result.Err("Nothing here")
    assert Null(Result.Ok("foo")).transpose() == Result.Ok(Some(None))
    assert Null(Result.Err("Nothing here")).transpose() == Result.Ok(Some(None))
    assert Some("Not a Result").transpose() == Result.Ok(Some("Not a Result"))
    assert Null("Not a Result").transpose() == Result.Ok(Some(None))


def test_unwrap_when_some_value_should_returns_the_value_or_throws_an_unwrap_failed_exception():
    expected = re.escape("Called `.unwrap` on an [`Null`] value.")
    assert Some(10).unwrap() == 10
    with pytest.raises(UnwrapFailedError, match=expected):
        Null("Emergency failure").unwrap()


def test_unwrap_or_when_some_value_should_return_value_or_provided_default():
    default_value = 42
    assert Some(2).unwrap_or(default_value) == 2
    assert Null("Something went wrong").unwrap_or(default_value) == 42


def test_unwrap_or_else_when_some_value_should_return_value_or_compute_from_function():
    assert Some(2).unwrap_or_else(lambda: 3) == 2
    assert Null("foo").unwrap_or_else(lambda: 3) == 3


@pytest.mark.parametrize(
    "option, expected",
    [
        (Some(10), 10),
        (Null(None), None),
        (Some("test"), "test"),
        (Null("error"), "error"),
    ],
    ids=[
        "iter when Some with int should yield int",
        "iter when Null with None should yield None",
        "iter when Some with str should yield str",
        "iter when Null with str should yield str",
    ],
)
def test_iter(option, expected):
    assert list(option) == [expected]


@pytest.mark.parametrize(
    "option, expected",
    [
        (Some(10), "Some(10)"),
        (Null(None), "Null(None)"),
        (Some("test"), "Some('test')"),
        (Null("error"), "Null('error')"),
    ],
    ids=[
        "repr when Some with int should return formatted string",
        "repr when Null with None should return formatted string",
        "repr when Some with str should return formatted string",
        "repr when Null with str should return formatted string",
    ],
)
def test_repr(option, expected):
    assert repr(option) == expected


def test_hash() -> None:
    assert len({Some(1), Null("2"), Some(1), Null("2")}) == 2
    assert len({Some(1), Some(2)}) == 2
    assert len({Some("a"), Null("a")}) == 2


@pytest.mark.parametrize(
    "option1, option2, expected",
    [
        (Some(10), Some(10), True),
        (Null(None), Null(None), True),
        (Some("test"), Some("test"), True),
        (Null("error"), Null("error"), True),
        (Some(10), Null(10), False),
        (Some(10), Some(20), False),
        (Null(None), Null("error"), False),
    ],
    ids=[
        "eq when Some with same int should return True",
        "eq when Null with same None should return True",
        "eq when Some with same str should return True",
        "eq when Null with same str should return True",
        "eq when Some and Null with same int should return False",
        "eq when Some with different int should return False",
        "eq when Null with different values should return False",
    ],
)
def test_eq(option1, option2, expected):
    assert (option1 == option2) == expected


@pytest.mark.parametrize(
    "option1, option2, expected",
    [
        (Some(10), Some(10), False),
        (Null(None), Null(None), False),
        (Some("test"), Some("test"), False),
        (Null("error"), Null("error"), False),
        (Some(10), Null(10), True),
        (Some(10), Some(20), True),
        (Null(None), Null("error"), True),
    ],
    ids=[
        "ne when Some with same int should return False",
        "ne when Null with same None should return False",
        "ne when Some with same str should return False",
        "ne when Null with same str should return False",
        "ne when Some and Null with same int should return True",
        "ne when Some with different int should return True",
        "ne when Null with different values should return True",
    ],
)
def test_ne(option1, option2, expected):
    assert (option1 != option2) == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (10, 0, Null(None)),
        (10, 2, Some(5.0)),
        (-10, 2, Some(-5.0)),
        (0, 2, Some(0.0)),
        (1_000_000, 2, Some(500_000.0)),
    ],
    ids=[
        "as_Null when division by zero should return Null(None)",
        "as_Null when valid division should return Some(5.0)",
        "as_Null when negative division should return Some(-5.0)",
        "as_Null when zero dividend should return Some(0.0)",
        "as_Null when large numbers should return Some(500_000.0)",
    ],
)
def test_as_null(a, b, expected) -> None:
    assert div(a, b) == expected
