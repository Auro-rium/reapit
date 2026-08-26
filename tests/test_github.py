from app.tools.github import parse_url

def test_parse_url():
    assert parse_url("https://github.com/acme/demo.git") == ("acme", "demo")

def test_reject_url():
    import pytest
    with pytest.raises(ValueError): parse_url("https://example.com/nope")
