from __future__ import annotations

# from src.option import Maybe, Option, Some
# from src.option.option import Maybe, Option, Some, UnwrapError, as_async_option, as_option
from src.option import Option, Some, UnwrapError, as_async_option, as_option, Maybe
def test_pattern_matching_on_ok_type() -> None:
    o: Option[str, int] = Some("yay")
    match o:
        case Some(value):
            reached = True

    assert value == "yay"
    assert reached


def test_pattern_matching_on_err_type() -> None:
    n: Option[int, str] = Maybe("nay")
    match n:
        case Maybe(value):
            reached = True

    assert value is None
    assert reached
