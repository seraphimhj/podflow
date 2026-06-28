from podflow.cli import slug, write_output


def test_slug_is_filesystem_safe():
    s = slug("https://www.youtube.com/watch?v=abc123&t=10")
    assert "/" not in s and "?" not in s and "&" not in s
    assert s  # non-empty


def test_write_output_creates_dated_file(tmp_path):
    path = write_output("# hi\n", "https://x/ep", str(tmp_path), "2026-06-28")
    assert path.endswith(".md")
    assert "2026-06-28" in path
    with open(path, encoding="utf-8") as fh:
        assert fh.read() == "# hi\n"
