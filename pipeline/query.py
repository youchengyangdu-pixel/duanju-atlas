#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""duanju-atlas · 案例检索。零第三方依赖，直接可用。"""

import argparse
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_json(path, default=None):
    if not os.path.exists(path):
        return default if default is not None else {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def find_cases(index_name, key):
    idx = load_json(os.path.join(BASE, "indexes", index_name + ".json"), {})
    return idx.get(key, [])


def show_case(ref_id, full=False):
    path = os.path.join(BASE, "cases", ref_id, "card.json")
    if not os.path.exists(path):
        print("  %s: 卡片不存在" % ref_id)
        return
    card = load_json(path, {})
    print("\n[%s] %s" % (ref_id, card.get("title_alias", "")))
    print("  题材: %s" % " / ".join(card.get("genre", [])))
    print("  框架: %s" % card.get("frame", "—"))
    print("  公式: %s" % card.get("formula", "—"))
    st = card.get("structure", {})
    if st.get("arc"):
        print("  起承转合: %s" % st["arc"])
    if st.get("core_twist_ep"):
        print("  核心反转: 第 %s 集" % st["core_twist_ep"])
    pw = card.get("paywall", {})
    if pw.get("ep"):
        print("  付费卡点: 第 %s 集（%s）" % (pw["ep"], pw.get("on_what", "")))
    if full:
        f3 = card.get("first3", {})
        if f3:
            print("  前三集:")
            for k, label in [("opening_10s", "开场10秒"), ("ep1_hook", "首集钩子"),
                             ("ep2_escalation", "第2集升级"), ("ep3_twist_type", "第3集反转")]:
                if f3.get(k):
                    print("    %s: %s" % (label, f3[k]))
        for ch in card.get("characters", []):
            print("  人设·%s: %s | 反差: %s" % (
                ch.get("role", ""), ch.get("tag", ""), ch.get("contrast", "—")))
        if card.get("reusable"):
            print("  可复制: %s" % "；".join(card["reusable"]))


def main():
    p = argparse.ArgumentParser(description="duanju-atlas 案例检索")
    p.add_argument("--genre", help="按题材，如 狼人")
    p.add_argument("--structure", help="按结构框架，如 被放逐觉醒")
    p.add_argument("--hook", help="按钩子类型，如 身份曝光")
    p.add_argument("--paywall", help="按付费卡点，如 第8集")
    p.add_argument("--ref", help="直接查看某张卡，如 REF-001")
    p.add_argument("--full", action="store_true", help="显示完整字段")
    p.add_argument("--formula", action="store_true", help="只看一句话公式库")
    args = p.parse_args()

    if args.formula:
        data = load_json(os.path.join(BASE, "formulas", "formulas.json"), {})
        for f in data.get("formulas", []):
            print("[%s] %s" % (f["id"], f["formula"]))
            if f.get("note"):
                print("      %s" % f["note"])
        return 0

    if args.ref:
        show_case(args.ref, full=True)
        return 0

    queries = [("by-genre", args.genre), ("by-structure", args.structure),
               ("by-hook", args.hook), ("by-paywall", args.paywall)]
    hits = None
    for name, key in queries:
        if key:
            r = set(find_cases(name, key))
            hits = r if hits is None else (hits & r)

    if hits is None:
        # 无参数：列出全部案例
        cdir = os.path.join(BASE, "cases")
        hits = set(d for d in os.listdir(cdir)
                   if os.path.isdir(os.path.join(cdir, d))) if os.path.isdir(cdir) else set()

    if not hits:
        print("没有匹配的案例。可先运行 pipeline/run.py 拆解入库。")
        return 1

    for ref in sorted(hits):
        show_case(ref, full=args.full)
    return 0


if __name__ == "__main__":
    sys.exit(main())
