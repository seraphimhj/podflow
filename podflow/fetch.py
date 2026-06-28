import os
import re
import tempfile
import urllib.request

_TS = re.compile(r"\d{1,2}:\d{2}:\d{2}[.,]\d{3}\s*-->.*")
_CUE = re.compile(r"^\d+$")


def _pick_audio(filenames: list[str]) -> str:
    """Pick the finished audio file from a temp dir listing.

    Ignores partial/incomplete downloads; raises if none remain.
    """
    finished = [f for f in filenames if not f.endswith((".part", ".ytdl", ".tmp"))]
    if not finished:
        raise RuntimeError("no audio file was downloaded")
    return sorted(finished)[0]


def clean_transcript(raw: str) -> str:
    """Strip VTT/SRT timestamps, cue numbers, blank runs, consecutive dupes."""
    lines = []
    for line in raw.splitlines():
        s = line.strip()
        if not s or s == "WEBVTT" or _TS.match(s) or _CUE.match(s):
            continue
        if lines and lines[-1] == s:  # ponytail: collapse adjacent dupes only
            continue
        lines.append(s)
    return "\n".join(lines)


def _read_source(path_or_url: str) -> str:
    if path_or_url.startswith(("http://", "https://")):
        with urllib.request.urlopen(path_or_url, timeout=30) as r:
            return r.read().decode("utf-8", "replace")
    with open(path_or_url, encoding="utf-8") as fh:
        return fh.read()


def _rss_transcript(url: str) -> str | None:
    """If the URL is an RSS feed exposing a <podcast:transcript>, fetch it."""
    import feedparser

    feed = feedparser.parse(url)
    if not feed.entries:
        return None
    for entry in feed.entries:
        # feedparser maps namespaced <podcast:transcript> to 'podcast_transcript'
        href = None
        t = entry.get("podcast_transcript")
        if isinstance(t, dict):
            href = t.get("url") or t.get("href")
        for link in entry.get("links", []):
            if "transcript" in (link.get("rel", "") + link.get("type", "")):
                href = link.get("href")
        if href:
            return _read_source(href)
    return None


def _youtube_subs(url: str) -> str | None:
    """Download captions via yt-dlp if available; return raw VTT or None."""
    import yt_dlp

    with tempfile.TemporaryDirectory() as d:
        opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en", "en-US"],
            "subtitlesformat": "vtt",
            "outtmpl": os.path.join(d, "%(id)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        vtts = [f for f in os.listdir(d) if f.endswith(".vtt")]
        if not vtts:
            return None
        with open(os.path.join(d, vtts[0]), encoding="utf-8") as fh:
            return fh.read()


def _transcribe(url: str) -> str:
    """Download audio via yt-dlp, transcribe with SenseVoice (SiliconFlow)."""
    from openai import OpenAI
    import yt_dlp

    with tempfile.TemporaryDirectory() as d:
        opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(d, "audio.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        audio = os.path.join(d, _pick_audio(os.listdir(d)))
        client = OpenAI(
            api_key=os.environ["SILICONFLOW_API_KEY"],
            base_url="https://api.siliconflow.cn/v1",
        )
        with open(audio, "rb") as fh:
            # NOTE: confirm exact SenseVoice model id against SiliconFlow docs at run time.
            resp = client.audio.transcriptions.create(
                model="FunAudioLLM/SenseVoiceSmall", file=fh
            )
        return resp.text


def get_transcript(url: str, transcript: str | None = None) -> tuple[str, bool]:
    if transcript:
        return clean_transcript(_read_source(transcript)), False

    rss = _rss_transcript(url)
    if rss:
        return clean_transcript(rss), False

    subs = _youtube_subs(url)
    if subs:
        return clean_transcript(subs), False

    text = _transcribe(url)  # raises if SenseVoice/key/audio fails
    if not text.strip():
        raise RuntimeError(f"no transcript obtainable for {url}")
    return clean_transcript(text), True
