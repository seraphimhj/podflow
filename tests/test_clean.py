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


def test_clean_handles_youtube_auto_captions():
    raw = """WEBVTT
Kind: captions
Language: en

00:00:00.000 --> 00:00:02.159 align:start position:0%
old<00:00:00.480><c> media,</c><00:00:01.120><c> you</c>

00:00:02.159 --> 00:00:02.169 align:start position:0%
old media, you
had restricted channels
"""
    out = clean_transcript(raw)
    assert "<c>" not in out and "<00:" not in out  # inline tags stripped
    assert "Kind:" not in out and "Language:" not in out  # header stripped
    assert "align:start" not in out  # timing line stripped
    assert out.count("old media, you") == 1  # rolling dupe collapsed
    assert "had restricted channels" in out


def test_clean_decodes_html_entities():
    raw = "WEBVTT\n\n&gt;&gt; tom &amp; jerry\n"
    out = clean_transcript(raw)
    assert ">> tom & jerry" in out
    assert "&gt;" not in out and "&amp;" not in out
