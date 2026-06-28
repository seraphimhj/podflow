import pytest
from podflow.fetch import get_transcript, _pick_audio


def test_get_transcript_from_local_file(tmp_path):
    f = tmp_path / "t.vtt"
    f.write_text("WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nHello there\n", encoding="utf-8")
    text, transcribed = get_transcript("https://example.com/ep", transcript=str(f))
    assert "Hello there" in text
    assert "00:00:01" not in text
    assert transcribed is False


def test_pick_audio_ignores_partials_and_is_deterministic():
    assert _pick_audio(["audio.m4a"]) == "audio.m4a"
    assert _pick_audio(["audio.webm.part", "audio.m4a"]) == "audio.m4a"


def test_pick_audio_raises_when_no_finished_file():
    with pytest.raises(RuntimeError):
        _pick_audio(["audio.webm.part"])
