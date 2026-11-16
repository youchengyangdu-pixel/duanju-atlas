---
name: duanju-atlas
description: 爆款短剧拆解知识库。写剧本前检索同题材爆款的结构与公式；剧本终审时对照钩子密度与付费卡点；二创时返回可复用结构。用户说「有没有类似爆款参考」「这个题材怎么写」「帮我看看结构」「二创怎么改」时使用。
license: MIT
---

# duanju-atlas · 爆款拆解知识库

知识库位置：`duanju-atlas/`（公开仓库）。

一剧一卡（`cases/<REF-ID>/card.json`），四维索引（题材 / 结构 / 钩子 / 付费卡点）。

## 三个使用场景

### 场景一 · 写新剧本前

按题材或框架检索，返回可复用结构。

```bash
python duanju-atlas/pipeline/query.py --genre 狼人
python duanju-atlas/pipeline/query.py --structure 被放逐觉醒 --full
python duanju-atlas/pipeline/query.py --formula
```

返回重点：
- `structure.arc`：起承转合
- `first3`：前三集设计
- `paywall`：付费卡点位置与所卡悬念
- `characters[].contrast`：人设反差与亮出方式
- `formula`：一句话公式

**用法**：把这些当作结构起点，不要照抄情节。

### 场景二 · 剧本终审

对照同题材爆款，检查当前剧本：

| 检查项 | 对照字段 |
|---|---|
| 首集是否有钩子 | `first3.ep1_hook` |
| 前三集是否有反转 | `first3.ep3_twist_type` |
| 付费卡点位置是否合理 | `paywall.ep` 与 `on_what` |
| 打脸与反转频率 | `rhythm.slap_every` / `twist_every` |
| 人设反差是否亮出 | `characters[].reveal_ep` 与 `reveal_how` |

参考线：每 3 集一个打脸名场面、每 5 集一次身份或关系反转。

### 场景三 · 二创

输入对标 REF-ID，返回：

```bash
python duanju-atlas/pipeline/query.py --ref REF-001 --full
```

重点读：
- `reusable`：可复制的结构与人设
- `not_reusable`：不要改的部分（时机、渠道、运气类因素）

**只复用结构，不复制台词与具体桥段。**

## 新增案例

```bash
python duanju-atlas/pipeline/run.py <视频路径> --ref REF-002 --genre 狼人,复仇 --frame 被放逐觉醒
```

流程：截帧 → ASR → 画面分析（本地粗筛 + Gemini 精读）→ 出卡 → 自动更新索引。

## 边界

- 只拆有权使用的材料；自有或已授权作品才进入下游二创
- 卡片匿名（REF-ID），不写真实剧名、人名
- 原始素材只放本地 `evidence/`，不入库、不公开
- **机制候选只收多部剧共有的做法**；单一来源的标为个案，不进复用库
