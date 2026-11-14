#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""duanju-atlas · 截帧。优先 PySceneDetect，缺失时回退 ffmpeg 场景滤镜。"""

import argparse
import json
import os
import shutil
import subprocess
import sys


def has(cmd):
    return shutil.which(cmd) is not None


def with_scenedetect(video, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    cmd = ["scenedetect", "-i", video, "save-images", "-o", out_dir]
    subprocess.run(cmd, check=True)
    return "scenedetect"


def with_ffmpeg(video, out_dir, threshold=0.3, fps=1):
    os.makedirs(out_dir, exist_ok=True)
    pattern = os.path.join(out_dir, "scene_%04d.jpg")
    cmd = ["ffmpeg", "-y", "-i", video,
           "-vf", "select='gt(scene,%s)',showinfo" % threshold,
           "-vsync", "vfr", "-q:v", "2", pattern]
    subprocess.run(cmd, check=True, capture_output=True)
    return "ffmpeg"


def main():
    p = argparse.ArgumentParser(description="截帧")
    p.add_argument("video", help="视频路径")
    p.add_argument("--out", required=True, help="输出目录")
    p.add_argument("--threshold", default="0.3", help="场景切分阈值")
    args = p.parse_args()

    if not os.path.exists(args.video):
        print("[error] 视频不存在: %s" % args.video)
        return 2

    try:
        if has("scenedetect"):
            tool = with_scenedetect(args.video, args.out)
        elif has("ffmpeg"):
            tool = with_ffmpeg(args.video, args.out, args.threshold)
        else:
            print("[error] 需要 scenedetect 或 ffmpeg 之一在 PATH 中")
            print("  安装：pip install scenedetect  或  安装 ffmpeg")
            return 3
    except subprocess.CalledProcessError as e:
        print("[error] 截帧失败: %s" % e)
        return 1

    n = len([f for f in os.listdir(args.out) if f.lower().endswith((".jpg", ".png"))])
    print(json.dumps({"tool": tool, "frames": n, "out": args.out}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
