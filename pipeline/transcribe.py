#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""duanju-atlas · 语音转写（faster-whisper）。输出带时间戳的 JSON 与 SRT。"""

import argparse
import json
import os
import sys


def fmt_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return "%02d:%02d:%06.3f" % (h, m, s)


def srt_time(sec):
    return fmt_time(sec).replace(".", ",")


def main():
    p = argparse.ArgumentParser(description="ASR 转写")
    p.add_argument("video", help="视频或音频路径")
    p.add_argument("--out", required=True, help="输出前缀（不含扩展名）")
    p.add_argument("--model", default="large-v3", help="模型名，默认 large-v3")
    p.add_argument("--device", default="cuda", help="cuda 或 cpu")
    p.add_argument("--lang", default=None, help="强制语言，如 zh / en；默认自动")
    p.add_argument("--prompt", default=None, help="initial_prompt，给角色名提升准确率")
    args = p.parse_args()

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("[error] 未安装 faster-whisper。请先运行：")
        print("  pip install faster-whisper")
        return 3

    if not os.path.exists(args.video):
        print("[error] 文件不存在: %s" % args.video)
        return 2

    compute = "int8_float16" if args.device == "cuda" else "int8"
    try:
        model = WhisperModel(args.model, device=args.device, compute_type=compute)
    except Exception as e:
        print("[warn] %s 初始化失败（%s），改用 CPU int8" % (args.device, e))
        model = WhisperModel(args.model, device="cpu", compute_type="int8")

    segments, info = model.transcribe(
        args.video,
        language=args.lang,
        word_timestamps=True,
        vad_filter=True,
        initial_prompt=args.prompt,
    )

    rows = []
    for seg in segments:
        rows.append({
            "start": round(seg.start, 3),
            "end": round(seg.end, 3),
            "text": seg.text.strip(),
        })

    json_path = args.out + ".json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "language": info.language,
            "duration": round(info.duration, 2),
            "segments": rows,
        }, f, ensure_ascii=False, indent=1)

    srt_path = args.out + ".srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, r in enumerate(rows, 1):
            f.write("%d\n%s --> %s\n%s\n\n" % (
                i, srt_time(r["start"]), srt_time(r["end"]), r["text"]))

    print(json.dumps({
        "language": info.language,
        "segments": len(rows),
        "json": json_path,
        "srt": srt_path,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
