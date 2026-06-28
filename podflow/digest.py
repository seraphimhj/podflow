from typing import Callable

from podflow.template import LENSES


def assemble(lens_outputs: list[str], source_url: str, transcribed: bool) -> str:
    parts = [o.strip() for o in lens_outputs]
    parts.append("## 主编点评\n\n（待主编填写。切入提示：1) 这集对你的领域意味着什么；2) 哪一点你不同意。）")
    parts.append(f"---\n\n原节目：{source_url}")
    if transcribed:
        parts.append("> 注：本集基于语音转录，可能有误差。")
    return "\n\n".join(parts) + "\n"


def generate(
    transcript: str,
    source_url: str,
    transcribed: bool,
    llm_call: Callable[[str], str],
) -> str:
    outputs = [llm_call(tmpl.format(transcript=transcript, redlines="")) for _, tmpl in LENSES]
    return assemble(outputs, source_url, transcribed)
