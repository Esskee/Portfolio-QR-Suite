import pytest
from src.app.main import main


def test_main():
    assert main() is not None
