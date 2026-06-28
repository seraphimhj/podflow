# Lens prompts adapted from lijigang skills (ljg-book, ljg-learn).
# Each lens outputs ONE markdown block including its own header.
# Iterate prompt wording here — this file is the product's core.

REDLINES = """写作红线：中文白话（汪曾祺/王小波那一路）；反翻译腔（不用"做出选择/在X上/进行讨论"等英式表达，写完默念出声不卡）；禁切痕风（不用"这一刀/锋利/钉死"等自我修辞）；不夸不贬，冷静犀利直白。"""

HEAD = """你在为一集英文播客做中文深度精读的开头。基于逐字稿，输出（只输出 markdown，不要解释）：
# 行（给 3 个备选标题，用 ` / ` 分隔）
一行 `> ` 开头的一句话导读
一行 `**节目 / 嘉宾**：` 加 1–2 句背景
{redlines}

逐字稿：
{transcript}"""

DISSECT = """把这一集当一本书拆，以"问题"为轴。输出一个 markdown 块，以 `## 一、拆解` 为标题，依次写：
- 核心问题：作者/嘉宾真正在答什么？
- 共识基线：这个问题上之前大家默认怎么答（2–4 个立场，标明哪个是共识）。
- 独特洞见 + delta：这集相对常识挪了什么，一句话"之前大家以为 X，这集说 Y"，标修正/倒转/换轴。
- 落点：最锋利的一句核心结论。
- 带走一件：合上 10 年还记得的那一件（取景框/模型/洞见/概念/警句 五选一，三行内）。
- 认知地图：一张纯 ASCII 参考系图（有轴名、两端有极、各立场钉位置、标出 delta），包在 ``` 代码块里，宽度 ≤80 字符，只用基本 ASCII 符号。
{redlines}

逐字稿：
{transcript}"""

CONCEPT = """挑这一集最核心的 1 个概念，做概念解剖。输出一个 markdown 块，以 `## 二、概念解剖` 为标题，写：
- 定锚：这个概念通行定义 + 常见误解。
- 切 4–5 刀（从 历史/辩证/现象/语言/形式/存在/美感 里挑最相关的 4–5 个，各 2–3 句，只留筋骨）。
- 压缩：一个 `概念 = …` 公式 + 一句话最深理解 + 一张纯 ASCII 结构图（包在 ``` 代码块里）。
{redlines}

逐字稿：
{transcript}"""

QUOTES = """从逐字稿里挑 3–5 句最有信息量/最锋利的原话，做金句中英对照。输出一个 markdown 块，以 `## 金句` 为标题，每条格式：
- 英文原句
  中文翻译（地道，反翻译腔）
{redlines}

逐字稿：
{transcript}"""

LENSES = [
    ("head", HEAD),
    ("dissect", DISSECT),
    ("concept", CONCEPT),
    ("quotes", QUOTES),
]
