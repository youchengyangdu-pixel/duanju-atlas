# duanju-atlas · 爆款短剧拆解知识库

> 公开仓库。存放爆款短剧的结构化拆解，用于复盘、写剧本、二创。原始素材（原片、截图）不入库。

## 这个项目是什么

把每一部对标短剧拆成一张**结构化案例卡**（`card.json`），再按题材、结构、钩子、付费卡点四个维度建索引，形成可检索、可调用的知识库。

**不是视频库，是结构库。** 原片与截图只放本地 `evidence/`，卡片只写结构与机制，不复制原台词。

## 目录

```
cases/REF-xxx/     一剧一卡（card.json 机器读 + card.md 人读 + evidence 素材）
schemas/           字段规范
indexes/           四个维度的检索索引
formulas/          一句话公式库
pipeline/          自动拉片：截帧 → ASR → 画面分析 → 提炼出卡
skills/            对接 Seedance 管线的 skill
tools/             可直接打开使用的工具（爆款拆解 SOP 模板）
docs/              方法论文档（skill 库拆解与复用指南）
```

## 自带工具与文档

- **`tools/爆款拆解SOP模板.html`**：可填写的拆解工具。新建案例 → 按 12 组填 → 导出 Markdown 直接贴 Obsidian。数据存本机 localStorage，可导出全库 JSON。双击即用，零依赖。
- **`docs/短剧skill库拆解与复用指南.html`**：两个短剧 skill 库（drama-skills / shuohao-skills）的一手拆解，含 7 步工作流、8 拆解维度、实测基准与质量门清单。

## 快速开始

```bash
# 1. 自动拆解一部剧
python pipeline/run.py <视频路径> --ref REF-001

# 2. 按题材检索案例
python pipeline/query.py --genre 狼人

# 3. 按结构检索
python pipeline/query.py --structure 扮猪吃虎
```

## 卡片字段（核心）

| 字段 | 含义 |
|---|---|
| `structure.arc` | 起承转合（如「压迫→隐忍→掉马→碾压→后悔」） |
| `structure.core_twist_ep` | 核心反转锁在哪一集 |
| `first3` | 前三集：开场 10 秒、首集钩子、升级方式、首次反转类型 |
| `paywall` | 付费卡点位置与所卡悬念 |
| `characters[].contrast` | 人设反差及亮出方式 |
| `rhythm` | 打脸与反转的频率 |
| `formula` | 一句话公式 |
| `reusable / not_reusable` | 可复制与不可复制的部分 |

## 使用边界

- 只拆有权使用的材料；自有或已授权作品才进入下游二创
- 卡片匿名（REF-ID），不写真实剧名、人名
- 原始素材不入公开库

## 许可

项目代码 MIT。案例内容为内部研究资料，不对外发布。
