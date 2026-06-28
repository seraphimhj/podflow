from podflow.fetch import get_transcript


def test_get_transcript_from_local_file(tmp_path):
    f = tmp_path / "t.vtt"
    f.write_text("WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nHello there\n", encoding="utf-8")
    text, transcribed = get_transcript("https://example.com/ep", transcript=str(f))
    assert "Hello there" in text
    assert "00:00:01" not in text
    assert transcribed is False
