#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""duanju-atlas · 提炼成卡并更新索引。"""

import argparse
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK_ENUM = ["利益骤变", "身份曝光", "道德突破", "情感背叛", "悬念", "羞辱", "危机", "欲望", "其他"]


def load(path, default=None):
    if not os.path.exists(path):
        return default if default is not None else {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def main():
    p = argparse.ArgumentParser(description="提炼成卡")
    p.add_argument("--ref", required=True)
    p.add_argument("--analysis", required=True, help="analyze.py 输出")
    p.add_argument("--alias", default="")
    p.add_argument("--genre", default="", help="题材，逗号分隔")
    p.add_argument("--frame", default="")
    p.add_argument("--formula", default="")
    args = p.parse_args()

    ana = load(args.analysis, {})
    case_dir = os.path.join(BASE, "cases", args.ref)
    os.makedirs(os.path.join(case_dir, "evidence"), exist_ok=True)

    card = {
        "id": args.ref,
        "title_alias": args.alias or "未命名（匿名）",
        "genre": [g.strip() for g in args.genre.split(",") if g.strip()],
        "frame": args.frame,
        "structure": {"logline": "", "arc": "", "core_twist_ep": ""},
        "first3": {
            "opening_10s": ana.get("opening_10s", ""),
            "ep1_hook": ana.get("ep1_hook", ""),
            "ep2_escalation": ana.get("ep2_escalation", ""),
            "ep3_twist_type": ana.get("ep3_twist_type", ""),
            "paywall_candidate": ana.get("paywall_candidate", ""),
        },
        "paywall": {"ep": "", "on_what": ana.get("paywall_candidate", "")},
        "characters": ana.get("characters", []),
        "hooks": [],
        "rhythm": ana.get("rhythm", {}),
        "data": {"note": ana.get("status", "")},
        "formula": args.formula or ana.get("formula", ""),
        "reusable": [],
        "not_reusable": [],
        "tags": [g.strip() for g in args.genre.split(",") if g.strip()],
    }

    save(os.path.join(case_dir, "card.json"), card)

    md = ["# %s · %s" % (args.ref, card["title_alias"]), "",
          "> 题材：%s　框架：%s" % (" / ".join(card["genre"]) or "—", args.frame or "—"), "",
          "## 一句话公式", card["formula"] or "（待补）", "",
          "## 前三集", ""]
    for k, label in [("opening_10s", "开场 10 秒"), ("ep1_hook", "首集钩子"),
                     ("ep2_escalation", "第 2 集升级"), ("ep3_twist_type", "第 3 集反转"),
                     ("paywall_candidate", "首次付费卡点")]:
        md.append("- **%s**：%s" % (label, card["first3"].get(k) or "（待补）"))
    with open(os.path.join(case_dir, "card.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    # 更新索引
    idx_dir = os.path.join(BASE, "indexes")
    for g in card["genre"]:
        idx = load(os.path.join(idx_dir, "by-genre.json"), {})
        idx.setdefault(g, [])
        if args.ref not in idx[g]:
            idx[g].append(args.ref)
        save(os.path.join(idx_dir, "by-genre.json"), idx)
    if args.frame:
        idx = load(os.path.join(idx_dir, "by-structure.json"), {})
        idx.setdefault(args.frame, [])
        if args.ref not in idx[args.frame]:
            idx[args.frame].append(args.ref)
        save(os.path.join(idx_dir, "by-structure.json"), idx)

    print(json.dumps({"ref": args.ref, "card": os.path.join(case_dir, "card.json")},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
