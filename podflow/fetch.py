import re

_TS = re.compile(r"\d{1,2}:\d{2}:\d{2}[.,]\d{3}\s*-->.*")
_CUE = re.compile(r"^\d+$")


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
