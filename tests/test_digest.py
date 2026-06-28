from podflow.digest import generate


def fake_llm(prompt: str) -> str:
    if "金句" in prompt:
        return "## 金句\n- Hello\n  你好"
    if "拆解" in prompt:
        return "## 一、拆解\n核心问题..."
    if "概念解剖" in prompt:
        return "## 二、概念解剖\n定锚..."
    return "# A / B / C\n> 导读\n**节目 / 嘉宾**：背景"


def test_generate_assembles_all_sections():
    md = generate("some transcript", "https://example.com/ep1", False, fake_llm)
    assert "## 一、拆解" in md
    assert "## 二、概念解剖" in md
    assert "## 金句" in md
    assert "## 主编点评" in md
    assert "原节目：https://example.com/ep1" in md
    assert "语音转录" not in md  # transcribed=False


def test_generate_adds_transcription_note():
    md = generate("t", "https://x", True, fake_llm)
    assert "语音转录" in md
