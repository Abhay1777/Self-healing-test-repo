from app import (
    calculate_average,
    get_second_largest,
    reverse_string
)


def test_average():
    assert calculate_average([10, 20, 30]) == 20


def test_second_largest():
    assert get_second_largest([10, 50, 30, 20]) == 30


def test_reverse():
    assert reverse_string("hello") == "olleh"
