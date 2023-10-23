from __future__ import annotations

from option import Maybe, Option, Some, UnwrapError, as_async_option, as_option


def test_pattern_matching_on_ok_type() -> None:
    o = Some("yay")
    match o:
        case Some(value):
            reached = True

    assert value == "yay"
    assert reached


def test_pattern_matching_on_err_type() -> None:
    n = Maybe("nay")
    match n:
        case Maybe(value):
            reached = True

    assert value is None
    assert reached
