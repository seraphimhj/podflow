# podflow

把一集英文播客变成一份中文深度精读的 markdown 初稿，主编改完即可发布。

`podflow <英文播客单集链接>` → `output/YYYY-MM-DD-<slug>.md`

面向"只要观点、不想学英语"的中文知识读者（首个垂直：科技 / 创投 / AI）。AI 出初稿、主编把关——护城河是品味，不是技术。

## 装

需要 Python ≥ 3.11。

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e .
```

## 配

环境变量（按需）：

| 变量 | 用途 | 何时需要 |
|------|------|---------|
| `ANTHROPIC_API_KEY` | 生成 digest 的 Claude | 必需 |
| `ANTHROPIC_BASE_URL` | Claude 代理地址 | 国内走代理时 |
| `PODFLOW_MODEL` | 模型，默认 `claude-opus-4-8` | 想换模型时 |
| `SILICONFLOW_API_KEY` | SenseVoice 语音转录 | 仅当节目抓不到现成字幕、走兜底转录时 |

```bash
export ANTHROPIC_API_KEY=...
export SILICONFLOW_API_KEY=...
```

## 跑

```bash
podflow "https://www.youtube.com/watch?v=..."           # 自动抓字幕，抓不到则转录
podflow "<音频/RSS单集链接>"                              # 纯播客音频
podflow "<链接>" --transcript path/to/official.txt       # 已知官网有逐字稿时直接喂
podflow "<链接>" -o my_drafts                            # 自定义输出目录（默认 output/）
```

产出一个 `.md`，打开删改、贴公众号。

### 取稿优先级（命中即停）

1. `--transcript` 手动指定（官网官方稿，最准）
2. RSS 里的 `<podcast:transcript>` 标签
3. YouTube 字幕（yt-dlp）
4. SenseVoice 转录（兜底，文末会标注"基于语音转录、可能有误差"）

不爬各家官网页面（爬虫易腐烂，用 `--transcript` 代替）；不接 Apple / Spotify 的 App 内逐字稿（无公开接口）。

## 产出结构

```
# 标题（3 备选） / 一句话导读 / 节目·嘉宾背景
## 一、拆解        核心问题 / 共识基线 / 洞见+delta / 落点 / 带走一件 + ASCII 认知地图
## 二、概念解剖     这集核心概念，切 4–5 刀 + 一句话压缩 + ASCII 结构图
## 金句            中英对照
## 主编点评        留空，你来写
---
原节目：<链接>
```

## 改模板（产品本体在这）

四个 lens 的 prompt 都在 [`podflow/template.py`](podflow/template.py)（head / dissect / concept / quotes），改造自 [lijigang/ljg-skills](https://github.com/lijigang/ljg-skills) 的 ljg-book、ljg-learn。**这就是你迭代的地方**——按真实产出调措辞、加减小节。改这里不影响管道其余部分。

## 测试

```bash
. .venv/bin/activate && pytest -q
```

纯逻辑单测（清洗 / 拼装 / 取稿本地路径 / 文件名）。`digest.run` 的真实 LLM 路径不做自动测试——靠主编每篇人工过目。

## 已知边界

- SenseVoice 的 model id（`FunAudioLLM/SenseVoiceSmall`）首次跑请按硅基流动文档确认。
- `clean_transcript` 会丢弃纯数字单行（如孤立的 "1984"），罕见、可接受。
- 设计与计划见 [`docs/superpowers/`](docs/superpowers/)。后续 Phase B（多平台改写+半自动分发）、Phase C（多账号矩阵）各自独立、尚未开工。
