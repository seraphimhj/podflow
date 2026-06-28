import os
from typing import Callable

from podflow.template import LENSES, REDLINES


def assemble(lens_outputs: list[str], source_url: str, transcribed: bool) -> str:
    parts = [o.strip() for o in lens_outputs]
    parts.append("## 主编点评\n\n（待主编填写。切入提示：1) 这集对你的领域意味着什么；2) 哪一点你不同意。）")
    parts.append(f"---\n\n原节目：{source_url}")
    if transcribed:
        parts.append("> 注：本集基于语音转录，可能有误差。")
    return "\n\n".join(parts) + "\n"


def _claude_call(prompt: str) -> str:
    from anthropic import Anthropic  # lazy import: keeps unit tests offline

    client = Anthropic()  # reads ANTHROPIC_API_KEY / ANTHROPIC_BASE_URL
    model = os.environ.get("PODFLOW_MODEL", "claude-opus-4-8")
    msg = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in msg.content if b.type == "text")


def run(transcript: str, source_url: str, transcribed: bool) -> str:
    def call(prompt: str) -> str:
        return _claude_call(prompt)

    outputs = [
        call(tmpl.format(transcript=transcript, redlines=REDLINES))
        for _, tmpl in LENSES
    ]
    return assemble(outputs, source_url, transcribed)


def generate(
    transcript: str,
    source_url: str,
    transcribed: bool,
    llm_call: Callable[[str], str],
) -> str:
    outputs = [llm_call(tmpl.format(transcript=transcript, redlines="")) for _, tmpl in LENSES]
    return assemble(outputs, source_url, transcribed)
