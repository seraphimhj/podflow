import argparse
import os
import re
from datetime import date

from podflow import digest, fetch


def slug(url: str) -> str:
    base = re.sub(r"^https?://", "", url)
    base = re.sub(r"[^A-Za-z0-9]+", "-", base).strip("-")
    return (base[:60] or "episode").lower()


def write_output(md: str, url: str, outdir: str, today: str) -> str:
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f"{today}-{slug(url)}.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(md)
    return path


def main() -> None:
    ap = argparse.ArgumentParser(prog="podflow", description="英文播客 → 中文深度精读初稿")
    ap.add_argument("url", help="播客单集链接 / YouTube 链接 / 直链音频")
    ap.add_argument("--transcript", help="已知官方逐字稿的文件路径或 URL")
    ap.add_argument("-o", "--outdir", default="output", help="输出目录（默认 output/）")
    args = ap.parse_args()

    text, transcribed = fetch.get_transcript(args.url, args.transcript)
    md = digest.run(text, args.url, transcribed)
    path = write_output(md, args.url, args.outdir, date.today().isoformat())
    print(path)


if __name__ == "__main__":
    main()
