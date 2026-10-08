# v3 交接（2026-10-08 夜，额度耗尽前写）

> 主 checkout 里 `README.md` / `docs/DONE.md` / `docs/TODO.md` / `lab/zosc-signal/` / `lab/zosc-wordmark/` 有 **Codex 未提交的改动**，
> 不是我的，提交时只 `git add` 指定路径，别把它们一起提上去。

## 已完成、未合并（都基于 main 5ea1709，校验全过）
| 分支 | commit | 内容 | clip |
|---|---|---|---|
| worktree-agent-a898fb00cb6ffed83 | 7f7777d | **G**：删产品条；Code 板块上挂 PRODUCTS 眉题、Motion 上挂 WORK；三张大卡下各一行小字直达链接（Adobe Exchange ↗ / motionrules.com ↗ / App Store · Google Play ↗）；首页 1440 −349px、390 −879px | e0jqkc9ndd / s477s288cr / nc68d3kbm1 |
| worktree-agent-a91d5d5cb2e83976e | 374b15c | **H**：默认 og 图换成 1200×630 纯黑底 og-default.png（+方版），只在默认图时输出 width/height/alt；产品页仍用各自封面 | kwke6n5ct0 / 27s92gybat / db68z71erb / 4t85qkq2ap |

**合并步骤（下一步第一个动作）**：先合 G，再合 H；然后改 `tools/check-home.py` 的
`DEFAULT_OG = f"{SITE}/media/images/common/brand/og-default.png"`（H 报告：不改这一行第 6 项 15 个 FAIL）；
`npm run build` + `check-home.py --online` + `check-motion.mjs` + `check-projects.py --dist --schema --online` + `check-about.mjs` 全过后推 main。
用户已授权：核完直接推，截图推 clip，不要他看预览。

## Google 搜索结果右侧那张「灰边大 Z」缩略图 —— 根因已查实
**不是 og:image，是页头 logo `zosc-logo.png`（672×546，比例 1.231，白 Z 透明底）。** 证据：首页全部 13 个 `<img>` 里，
只有它的比例与截图缩略图（1.227）吻合；其余是 1:1 小图标或 ≥1.78 的宽图。Google 把非方图等比塞进方框补灰条，透明处填黑。
所以 **H 的新 og 图修好了分享卡和旧名残留（旧 og 图上写的是 ZERB），但修不了这个缩略图。**

修法（待做，我倾向 a+b 一起）：
- a. 页头 logo 改成**内联 SVG**（用 `app/public/favicon.svg` 同一条 Z 路径），不再是图片候选；视觉不变、更清晰
- b. 显式声明首选图：`og:image` + 首页 JSON-LD 加 WebPage.`primaryImageOfPage` 指向一张 **1:1 不透明**的图。
  Google 文档原则是首选图不要用 logo/带字图——要查原文确认（WebFetch 因额度中断）。改 b 需同步改 check-home 第 15 项（现要求首页恰好 3 个 JSON-LD）。

## 图标（favicon）—— 根因已查实，站内无遗漏
以 Googlebot UA 经 Cloudflare 取首页与全部图标：200、无 challenge、五条 `<link rel=icon>` 全在，四个入口（http / www / vercel.app / zerb.net）
的 ico md5 全相同 = Z。Google 图标服务 `t1.gstatic.com/faviconV2?url=https://zosc.com` 仍返回 **Astro A**（10-06 旧记录），
而 `?url=https://www.zosc.com` 返回的是 **Z**——同站同文件，新抓的条目就是 Z。结论：等 Google 图标爬虫轮到 zosc.com 这条，无站内动作可加速。
复查命令：`curl -s -o g.png "https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://zosc.com&size=128"`

## 用户其他已定 / 在等的
- logo 动效原型被否（「奇丑无比」），用户说**先别扯 logo**。评审文件 `lab/osc-logo/REVIEW.md` 已写，等用户让 Codex 去读。
- MotionPilot 线上大卡 banner 用户说不好看，**还在等他发实际截图**。
- G 的两个小待定：Code 板块底部 `View all work →` 是否改 `View all products →`；大卡标题到直达行 57px 是否可接受。
- v3-F 已上线（main 5ea1709）。上线记录尚未写进 DONE.md（避开 Codex 未提交的改动），合并 G/H 时一起补。
