from __future__ import annotations

from option import Maybe, Some


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

    assert value == "nay"
    assert reached
