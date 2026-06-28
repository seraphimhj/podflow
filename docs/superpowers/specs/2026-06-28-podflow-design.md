# podflow 设计文档

日期：2026-06-28
状态：已确认，待实现计划

## 一句话

`podflow <英文播客单集链接>` → 产出一份中文深度精读 md 初稿，主编改完贴公众号。

## 背景与定位

- 面向"只要观点、不想学英语"的中文知识读者，把海外英文播客做成**中文深度 digest**（一期一集）。
- 第一个垂直：**科技 / 创投 / AI**（a16z、Lex Fridman、Acquired、All-In 等）。
- 模式 D-混合：A 阶段主编亲自选题把关、AI 出初稿；验证后再逐步自动化（本工具就是 A 阶段的生产流水线）。
- 护城河是**主编品味 + digest 模板**，不是技术。模板固化在 prompt 里，单独迭代。
- 规模假设：1–2 期/周，一次处理一集，**无需批量并发**。

## 非目标（YAGNI，明确不做）

- 无 web 界面（D-阶段二验证后再加）
- 无数据库、无任务队列、无并发
- 无自动发布（产出 md，主编手动贴公众号）
- 无 paper-river 递归溯源（对闲聊播客不成立，硬做=编造）
- 不做全网播客索引/发现（那是另一个被巨头占住的赛道）

## 架构

一条直线管道，4 个小文件，各管一职。无服务、无状态。

```
cli.py        podflow <url> → 串联各步 → 写 output/YYYY-MM-DD-<slug>.md
fetch.py      url → 纯文本逐字稿
digest.py     逐字稿 → 跑 2 个 lens（Claude）→ 拼成一篇 md
template.py   存 2 个 lens prompt + 拼装顺序（产品本体）
```

### fetch.py — 取逐字稿

输入口径：**YouTube 链接** 或 **播客单集**（直链 mp3 / RSS 单集音频 / yt-dlp 能解析的播客页面）。
可选 `--transcript <文件或URL>`：主编已知该集有官方逐字稿时，直接指定。

取稿优先级（按"准 + 省力"排，命中即停）：
1. **`--transcript` 手动指定** — 主编知道官网有官方稿时最准。
2. **RSS `<podcast:transcript>` 标签**（Podcasting 2.0）— 部分 feed 直接声明逐字稿 URL，解析 RSS 即得，免费零维护。
3. **YouTube 字幕**（`yt-dlp`）— 顶级播客几乎都发 YouTube 全集，主力来源。
4. **SenseVoice 转录** — 以上都没有时，`yt-dlp -x` 下载音频 → SenseVoice（硅基流动，OpenAI 兼容接口）。纯音频播客走这条。

取到后清洗：去时间戳、广告口播、口水词，合并为纯文本。

输出：纯文本逐字稿（str）+ 来源标记（官方稿 / RSS / 字幕 / 转录）。
- 走转录时记下标记，最终 md 文末注明"本集基于语音转录、可能有误差"。

**明确不接**：官网逐字稿不写 per-site 爬虫（各家页面结构不同、爬虫易腐烂）——用 `--transcript` 手动喂代替。Apple / Spotify 的 App 内自动逐字稿无公开 API、抓不了，不接。

v1 输入范围：单集链接 / 直链音频 / yt-dlp 能解析的页面 + 可选 `--transcript`。**完整 RSS feed 选集**（给 feed URL 自动挑某一集）是后续小增量，v1 让用户直接给单集链接或 feed 内单集。

### digest.py — 生成中文初稿

- 逐字稿 1–2 小时 ≈ 4–5 万 token，**整篇塞进 Claude 上下文，不分块**。
- 跑 2 个 lens prompt（见 template.py），各一次 LLM 调用，再按固定顺序拼成一篇 md。
- LLM：Claude（`anthropic` SDK；如需代理读 `ANTHROPIC_BASE_URL`）。

### template.py — 模板（产品本体）

存放 2 个改造自 lijigang skills 的 lens prompt + 头尾占位 + 拼装顺序。

**lens 1 — 拆解（改造自 ljg-book，问题轴）**：把这一集当一本书拆。
核心问题 / 共识基线 / 独特洞见 + delta（这集相对常识挪了什么）/ 落点（核心结论）/ 精神内核（带走一件）+ ASCII 认知地图。保留 ljg-book 的"反翻译腔自查""禁切痕风"等写作红线。

**lens 2 — 概念解剖（改造自 ljg-learn）**：挑这集最核心的 1 个概念，切 4–5 刀（不必八刀全上——播客不是纯概念）+ 一句话压缩 + ASCII 结构图。

### cli.py — 入口

`podflow <url>`：调 fetch → digest → 写 `output/YYYY-MM-DD-<slug>.md`，打印路径。CLI 用 stdlib `argparse`。

## 产出 md 结构

```
# 标题（AI 给 3 个备选）
> 一句话导读
**节目 / 嘉宾**：背景 1–2 句

## 一、拆解
核心问题 / 共识基线 / 洞见 + delta / 落点 / 带走一件 + ASCII 认知地图

## 二、概念解剖
这集核心 1 个概念，切 4–5 刀 + 一句话压缩 + ASCII 结构图

## 金句
中英对照 3–5 条

## 主编点评
（留空 + 2 个切入提示，主编自己写）

---
原节目：<链接>
（如走转录：本集基于语音转录，可能有误差）
```

## 技术选型

| 项 | 选择 | 理由 |
|----|------|------|
| 语言 | Python | yt-dlp / SDK 生态 |
| 取字幕/音频 | yt-dlp | 覆盖 YouTube + 直链 + 多数播客页 |
| ASR 兜底 | SenseVoice（硅基流动，OpenAI 兼容） | 国内直连、近免费、英文不输 Whisper |
| digest LLM | Claude（`anthropic`） | 主编指定；如需代理用 `ANTHROPIC_BASE_URL` |
| CLI | stdlib `argparse` | 够用，不引依赖 |

依赖：`yt-dlp`、`anthropic`、`openai`（调 SenseVoice 兼容接口）、`feedparser`（解析 RSS `<podcast:transcript>` 标签）。

配置：env 读 `SILICONFLOW_API_KEY`、`ANTHROPIC_API_KEY`、可选 `ANTHROPIC_BASE_URL`。

## 错误处理

- 抓不到字幕 → 自动转 SenseVoice，并在 md 文末标注转录来源。
- url 不支持 / 取文本失败 → 明确报错退出，**不产出半成品**。
- 长音频 → SenseVoice / yt-dlp 自行分段，本工具不处理。

## 测试

放一段固定逐字稿样本 fixture，跑一遍 digest，断言产出 md 含【拆解 / 概念解剖 / 金句】三个小节。一个能跑的自检即可（不做框架化测试套件）。

## 后续阶段（不在本次范围，各自独立 spec）

本 MVP 是 **Phase A：生成器**——一份高质量中文 digest。后续按顺序、各开独立 spec：

- **Phase B — 多平台改写 + 半自动分发**（验证 Phase A 品味后再做）
  - 一份 digest → 自动改写成各平台格式：公众号长文 / 小红书图文卡片脚本等。
  - 推送到草稿箱（公众号官方 `draft` API；小红书无开放发布 API → 仅生成待发素材）→ **人工一键发**。
  - 明确半自动：不做全自动群发。
- **Phase C — 全自动 + 多账号矩阵**（先搁置，验证后再评估）
  - 多账号、每号一个细分领域。
  - 已知风险：平台对矩阵营销号限流/封号（尤其小红书无 API、自动发布违反 ToS）；量产与"主编品味"护城河对冲。先用单号单领域跑通再谈。

其他后续小项：
- D-阶段二：本地单页 web 界面做中英对照编辑。
- 完整 RSS feed 选集输入（给 feed URL 自动挑某一集）。
- 第二个垂直：健康 / 长寿。
