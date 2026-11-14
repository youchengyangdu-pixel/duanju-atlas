#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""duanju-atlas · 拉片主编排：截帧 → 转写 → 分析 → 出卡 → 更新索引。"""

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(script, args, allow_fail=False):
    cmd = [sys.executable, os.path.join(HERE, script)] + args
    print("\n>>> %s %s" % (script, " ".join(args)))
    r = subprocess.run(cmd)
    if r.returncode != 0 and not allow_fail:
        raise SystemExit(r.returncode)
    return r.returncode


def main():
    p = argparse.ArgumentParser(description="自动拉片")
    p.add_argument("video", help="视频路径")
    p.add_argument("--ref", required=True, help="案例编号，如 REF-001")
    p.add_argument("--alias", default="")
    p.add_argument("--genre", default="", help="题材，逗号分隔")
    p.add_argument("--frame", default="")
    p.add_argument("--formula", default="")
    p.add_argument("--prompt", default=None, help="ASR initial_prompt，给角色名")
    p.add_argument("--device", default="cuda")
    p.add_argument("--skip-frames", action="store_true")
    args = p.parse_args()

    workdir = os.path.join(HERE, "..", "cases", args.ref, "evidence")
    frames = os.path.join(workdir, "frames")
    os.makedirs(workdir, exist_ok=True)

    if not args.skip_frames:
        run("ingest.py", [args.video, "--out", frames], allow_fail=True)

    run("transcribe.py", [args.video, "--out", os.path.join(workdir, "transcript"),
                          "--device", args.device] +
        (["--prompt", args.prompt] if args.prompt else []), allow_fail=True)

    analysis = os.path.join(workdir, "analysis.json")
    run("analyze.py", ["--transcript", os.path.join(workdir, "transcript.json"),
                       "--frames", frames, "--out", analysis], allow_fail=True)

    run("distill.py", ["--ref", args.ref, "--analysis", analysis,
                       "--alias", args.alias, "--genre", args.genre,
                       "--frame", args.frame, "--formula", args.formula])

    print("\n完成。查看：python pipeline/query.py --ref %s --full" % args.ref)
    return 0


if __name__ == "__main__":
    sys.exit(main())
