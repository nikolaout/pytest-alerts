"""Example test suite for calculator functions"""
import pytest


def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def test_add_positive():
    """This test will pass"""
    assert add(2, 3) == 5

def test_subtract_negative():
    """This test will pass"""
    assert subtract(5, 3) == 2  # Corrected expectation

def test_multiply_zero():
    """This test will pass"""
    assert multiply(5, 0) == 0

@pytest.mark.skip(reason="Not implemented yet")
def test_complex_calculation():
    """This test will be skipped"""
    pass

def test_divide_by_zero():
    """This test will pass"""
    with pytest.raises(ValueError):  # Correct exception type
        divide(10, 0)
