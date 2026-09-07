from clipvein.scraper.parse import canonical_url, parse_count, parse_status_url


def test_parse_count_suffixes():
    assert parse_count("12.3K") == 12_300
    assert parse_count("1.2M") == 1_200_000
    assert parse_count("2B") == 2_000_000_000
    assert parse_count("834") == 834
    assert parse_count("12,345") == 12_345
    assert parse_count("") == 0
    assert parse_count(None) == 0


def test_parse_status_url():
    assert parse_status_url("https://x.com/KaiCenat/status/123") == ("KaiCenat", "123")
    assert parse_status_url("https://twitter.com/N3on/status/9") == ("N3on", "9")
    assert parse_status_url("https://x.com/home") is None
    assert parse_status_url(None) is None


def test_canonical_url():
    assert canonical_url("N3on", "9") == "https://x.com/N3on/status/9"
