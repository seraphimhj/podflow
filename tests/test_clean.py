from podflow.fetch import clean_transcript


def test_clean_strips_vtt_timestamps_and_dupes():
    raw = """WEBVTT

1
00:00:01.000 --> 00:00:03.000
Hello world

2
00:00:03.000 --> 00:00:05.000
Hello world

3
00:00:05.000 --> 00:00:07.000
This is a test
"""
    out = clean_transcript(raw)
    assert "00:00:01" not in out
    assert "WEBVTT" not in out
    assert out.count("Hello world") == 1
    assert "This is a test" in out
