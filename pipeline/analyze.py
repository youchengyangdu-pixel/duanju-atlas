#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""duanju-atlas · 画面与内容分析（混合方案）。

本地粗筛：可选（Qwen2.5-VL，需自行部署）
API 精读：Gemini（需 GEMINI_API_KEY 环境变量）
无 key 时输出结构化分析框架，供人工或主 Agent 补全。
"""

import argparse
import json
import os
import sys
import urllib.request


PROMPT = """你是短剧拆解专家。根据下面的转写与帧信息，输出这部短剧的结构化拆解。

要求：
1. 只写结构与机制，不复制原台词
2. 重点：开场 10 秒、每集结尾钩子类型、付费卡点候选、人设反差、情绪节奏
3. 用 JSON 输出，字段：opening_10s / ep1_hook / ep2_escalation / ep3_twist_type / paywall_candidate / characters / rhythm / formula
4. characters 里必须有 tag（单一定位）、contrast（反差）、reveal_how（怎么演出来）

转写内容：
%s

帧信息：共 %d 帧，目录 %s
"""


def call_gemini(api_key, transcript_text, frame_count, frame_dir, model="gemini-2.0-flash"):
    url = ("https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent?key=%s"
           % (model, api_key))
    body = {
        "contents": [{
            "parts": [{"text": PROMPT % (transcript_text[:12000], frame_count, frame_dir)}]
        }],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def main():
    p = argparse.ArgumentParser(description="画面与内容分析")
    p.add_argument("--transcript", required=True, help="transcribe.py 输出的 JSON")
    p.add_argument("--frames", default="", help="截帧目录")
    p.add_argument("--out", required=True, help="分析结果输出 JSON")
    p.add_argument("--model", default="gemini-2.0-flash")
    args = p.parse_args()

    with open(args.transcript, encoding="utf-8") as f:
        tdata = json.load(f)
    text = "\n".join(s["text"] for s in tdata.get("segments", []))
    frame_count = 0
    if args.frames and os.path.isdir(args.frames):
        frame_count = len([x for x in os.listdir(args.frames)
                           if x.lower().endswith((".jpg", ".png"))])

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("[warn] 未设置 GEMINI_API_KEY，输出待补全的分析框架")
        result = {
            "status": "pending_api",
            "note": "设置 GEMINI_API_KEY 后可自动完成画面精读；当前仅生成框架",
            "transcript_chars": len(text),
            "frames": frame_count,
            "opening_10s": "",
            "ep1_hook": "",
            "ep2_escalation": "",
            "ep3_twist_type": "",
            "paywall_candidate": "",
            "characters": [],
            "rhythm": {},
            "formula": "",
        }
    else:
        try:
            raw = call_gemini(key, text, frame_count, args.frames, args.model)
            result = {"status": "ok", "raw": raw}
        except Exception as e:
            print("[error] Gemini 调用失败: %s" % e)
            return 1

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print(json.dumps({"out": args.out, "status": result.get("status")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
