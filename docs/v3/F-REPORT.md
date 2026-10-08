# v3 子任务 F「品牌带作品集」报告（2026-10-08）

分支 `worktree-agent-a8999b851739cec3d`，基于 `origin/main` @ `55ee1dc`（含 73b9a65：每板块 3 张；Hero 为 Motion / Visual / Code）。
未合并、未碰 `main`。按要求**没有改** `docs/TODO.md` / `docs/DONE.md`。事实源：`docs/TODO.md`「v3 方向」一节。

**过程中用户改了三处（经主会话转达），本报告写的是最终状态：**
1. **博客块整项取消**（「没什么收益」）。已写好的构建时抓取、页面块、校验断言全部删掉；实测构建过程对 blog.zosc.com **0 次请求**（见校验）。
2. **页脚不要大字站点行**（「就加个超链接都够了」）。改为在原来那行小字链接里加三个普通链接。
3. **MotionPilot 与 MotionRules 图标太像**。MotionRules 改成「尺」，两者都改成统一风格的 SVG。

## 结论

| 项 | 改前（main @ 55ee1dc） | 改后 |
|---|---|---|
| Hero 三行大字与动效 | Motion / Visual / Code | **一字未动**（`index.astro` 的 diff 里删除的只有旧副标那 3 行；check-motion 实测时序与改前一致） |
| Hero 副标 | zosc is a motion designer, visual artist & creative developer. Ask the AI anything. | **`HERO_TAGLINE` 常量**：Design that runs. Code that moves. Things that ship. |
| Hero 动作 | 无 | **Get MotionPilot**（Adobe Exchange）· **Open MotionRules**（motionrules.com），新标签页打开，只淡入、不位移 |
| 产品条 | 无 | Hero 之下：MotionPilot · MotionRules · Cubby，图标 + 名称 + 一句话 + 直达按钮 + `Details →` |
| 三板块 | Hero 后直接 Code | 上方加 **Work** 眉题；板块本身、id、卡片规则零改动 |
| 博客块 | 无 | **无（用户取消）** |
| 页脚 | X · GitHub · Steam · Blog · Email | X · GitHub · Steam · Blog · **MotionRules · Cubby · MakerLion** · Email，同一行、同一样式 |
| JSON-LD（每页） | Person + WebSite | **Organization + Person + WebSite**，`@id` 互引；产品页 SoftwareApplication 加 `publisher` |
| about | 标题后直接正文 | 标题下一行 `zosc — z · oscillator. The clock behind the motion.`；正文与 AI prompt 字词零改动 |
| README | — | 标题下同一句（斜体） |
| 首页长度（1440 / 390） | — | 6246 / 6506 px；横向溢出 0、坏图 0 |
| 构建 | 通过 | 通过，warn/error 0 行；构建期唯一的外部请求是 Astro 自带遥测 |

截图（clip，最终版）：`v3-hero-products-1440-r2.png` id `66z591wx0z` · `v3-footer-1440-r2.png` id `1748xjje5z` ·
`v3-home-1440-full-r2.jpg` id `jgtnc9hwpe` · `v3-home-390-full-r2.jpg` id `0bxed734g9`；本地副本在 `.render-tmp/v3-f/`。
第一轮的 4 张（id `8b8n2rebsp` / `bsa3w9cgbc` / `zywpfpj20r` / `8raky0gsex`）含已取消的博客块和旧页脚、旧图标，作废。
截图用 `prefers-reduced-motion`（shoot-pages 的设计），只代表版式；动效由 check-motion 实测。

## 每项做法与理由

1. **Hero 副标 + 两个动作**（`app/src/pages/index.astro`、`app/src/styles/global.css`）
   - 副标是文件顶部一个常量 `HERO_TAGLINE`，换词只改一处；`tools/check-home.py` 直接从源码读这个常量去比对产物，换词后检查自动跟随。
   - 按钮沿用产品页的两种药丸按钮（首个强调色描边，第二个灰描边），只有颜色过渡。
   - 原副标 `<p>` 带「上移 + 淡入」入场（`heroIn`）。按钮是可点元素，AGENTS.md 规定不能位移，所以按钮行用单独一条 **只改 opacity** 的
     `heroFade`，比副标晚 0.2 s（1.9 s 起）。纯 CSS、不依赖 JS，不会卡在隐藏态；`prefers-reduced-motion` 下直接显示。
     check-motion 新增的逐帧实测：intro 开始后约 1.87 s 按钮开始可见，可见的约 145 帧里位置始终是同一点 (40, 656.6)，终值 opacity 1。
   - 按钮 URL 必须是对应产品 `.md` 的 `links` 之一，否则**构建直接报错**——首页和产品页不会悄悄分叉。
2. **产品条**（`index.astro`，`<section id="products">`）
   - 三块：图标 48 px + 名称（取条目 `title`）+ 一句话 + 直达按钮；右上角小号 `Details →` 进站内详情页。
     一句话从各自 `summary` 精炼，不含任何数字：
     - MotionPilot：An After Effects panel that applies your motion spec to keyframes.
     - MotionRules：Motion design tools that share one motion spec, from definition to Lottie handoff.
     - Cubby：Remember where you put things: note it in one line, find it later.
   - 直达动作：MotionPilot → Get on Adobe Exchange；MotionRules → Open motionrules.com；Cubby → App Store（id 链接）+ Google Play。
   - 产品条**不加 `.reveal`**：它是首屏下第一组可点按钮，滚入动画会让按钮在点击瞬间位移。
   - 眉题 "Products" 与 "Work" 同一形态：小号大写标签压在一条通栏细线上（Work 下面那条线就是 #code 原有的 `border-t`）。
3. **博客块**：用户取消，已删除（见下方「博客块的删除」）。
4. **Work 眉题**：一个独立的 `<div id="work">` 放在三板块前，不包裹它们——三个 `<section>` 的源码一行没改（diff 里只有新增行）。
   `/#work` 可作锚点；Header 导航与 `/#code` 等锚点不变，check-motion 实测同页锚点落点仍是 96 px。
5. **页脚**（`app/src/components/Footer.astro`）：在原来那行小号大写链接里、Blog 之后插入 MotionRules / Cubby / MakerLion，
   与 X / GitHub 完全相同的 class、间距、颜色，没有任何强调。原有 5 个链接的顺序和位置不变，Blog 仍只出现一次。
   `zosc.com` 自身不列——人已经在站上，页头 logo 就回首页。MakerLion 只有一个链接，不附任何描述。
   第一版（一排大号粗体站点名压在小字行上方）被用户否掉，已整体撤回，diff 只剩 3 个 `<a>`。
6. **Schema 配对**（`app/src/lib/entity.ts`、`app/src/layouts/Layout.astro`、`app/src/pages/project/[slug].astro`）
   - `entity.ts` 只放 `SITE` 与三个 `@id`：`https://zosc.com/#organization` / `#person` / `#website`，Layout 与产品页共用，引用不会漂。
   - Organization：`name: zosc`、`url`、`logo`（`zosc-mark-192.png`，192×192 正方形，高于 Google 组织 logo 的 112 px 下限）、
     `founder → #person`、`sameAs` 与 Person 同一个数组（五条）。没加 `brand`。
   - Person：加 `@id`；`worksFor` 与 `affiliation` 都 `→ #organization`（只用 `@id` 引用，不复制实体）；`alternateName` 的 ZERB 系列没动。
   - WebSite：加 `@id`、`publisher → #organization`。
   - SoftwareApplication：`author` = Person（带 `@id`）、`publisher` = Organization（带 `@id`），两者都保留 `@type` / `name` / `url`，
     不解析 `@id` 的读者看到的也是完整实体。
   - sameAs 仍定义在 Layout.astro，TODO 里「改 handle 必须同步改 Layout.astro 的 sameAs 和 Footer.astro」这条依然准确。
7. **解码句**：about 页标题下 `<p class="mt-6 text-sm text-mist">`（站内现有工具类，没新造样式），放在 `<article>` 之外，
   所以 about 正文、字数校验、AI prompt 都不变（check-about：prompt 里的 about 文本与 about.html 全文一致）。README.md 标题下同句。

## 图标（`app/public/media/images/products/<slug>/`）

**先说为什么两个图标「一样」**：MotionPilot 在 Adobe Exchange 上架页的图标（`d3awf6rem6b5na.cloudfront.net/.../205857/icons/…png`，48×48）
与 motionrules.com 的 `favicon.svg` 是**同一张图**——都是一条缓动曲线加两根贝塞尔手柄，几何完全一致
（`M15 46 C25 18 39 46 49 18`，端点与控制点同位置）。第一版两边都用了各自的官方图标，于是长得一样。

| 产品 | 文件 | 做法 |
|---|---|---|
| MotionPilot | `icon.svg` 874 B | **保留它自己的 Exchange 图标**（按「用它自己的图标，从 Adobe Exchange 取」），按上面的几何重绘为 SVG，套统一风格。 |
| MotionRules | `icon.svg` 645 B | **新画的直尺**（用户建议：rules = ruler）：圆角尺身 + 5 根刻度（两端与中间长、其余短），水平放置——与 MotionPilot 的对角曲线轮廓差别最大。 |
| Cubby | `icon.png` 144×144，9.8 KB | 未改：App Store 页的 AppIcon（mzstatic，512 px 版缩到 144），烘焙 15/64 圆角。`Findly/exports/zosc-site/` 里只有应用内截图，图标取自商店页。 |

统一风格：两个 SVG 都是**线性**，同一笔画 3.5（64 网格），圆头圆角，白色主线 + 浅橙 `#ffd9c2` 次线；底板用 MotionRules 家族同一条橙色渐变；
与 Cubby 同为 64 网格、满版方块、15/64 圆角，显示同为 48 px。第一版的 `motionpilot/icon.png` 已删除（本分支新加、未提交过、已无引用）。

## 博客块的删除（用户取消第 3 项）

- 删掉：`app/src/lib/blog-feed.ts`、`index.astro` 里的导入 / `await` / `<section id="blog">`、check-home 的博客检查与 `--expect-no-blog` 参数、
  `--online` 里的文章源与 posts.json 比对。`app/src` 里 `posts.json` / `blog-feed` / `latestPosts` / `BLOG_ORIGIN` 均为 0 处。
- **构建不请求 blog.zosc.com 的实证**：`tools/trace-build-requests.mjs`（经 `NODE_OPTIONS=--import` 注入 npm、astro build、postbuild 三个进程）
  记录全部出站请求，最终构建只有 1 条：`https://telemetry.astro.build/api/v1/record`（Astro 自带遥测），blog.zosc.com 0 条。
  正向对照：同一钩子下 `fetch('https://blog.zosc.com/posts.json')` 会被记下，说明钩子有效。
- 构建产物（`dist/`、`.vercel/output/`）里 `posts.json` / `blog-feed` / `#/post/` / `Latest from the blog` 均 0 处。
- 页头与页脚的 Blog 链接保留（那是链接，不是请求）。

## 校验（命令与结果，均为最终构建）

| 命令 | 结果 |
|---|---|
| `cd app && npm run build`（经 trace-build-requests 钩子） | exit 0；warn/error 0 行；出站请求仅 Astro 遥测 1 条 |
| `python3 tools/check-home.py --online` | OK：ok 55 行、FAIL 0；首页 10 个外链全部 200 |
| `curl -sL` 首页全部外链（10 个） | 10/10 返回 200（含 X、Steam；Steam 早先一次探测回过 429，重试即 200） |
| `node tools/check-about.mjs` | RESULT: PASS（无年份、deny-list 0、引用 13/13、字数在范围内、prompt 与 about.html 全文一致） |
| `python3 tools/check-projects.py --dist --schema --online` | OK：8 个产品页 `author → #person, publisher → #organization`；schema.org 词表（3256 项）校验了每页全部 JSON-LD 块；产品外链全 200 |
| 词表反向测试（误拼 `foundr`、`worksFor` 放在 Organization、`founder` 放在 Person） | 均报错——校验不是空转 |
| JSON-LD | 首页恰好 3 块：Organization / Person / WebSite，`@id` 如上；24 个有 JSON-LD 的页面，每个 `@id` 引用都能在本页解析 |
| 引用完整性 | check-home 检查 5：161 个 `/media`+`/fonts` 引用全部存在于 `app/public`（含 3 个图标）；其余 29 个站内引用都能解析 |
| `node tools/shoot-pages.mjs`：首页 1440/390 整页、Hero+产品条（2x）、页脚，另测 about / cubby / works | 7 个镜头：横向溢出 0、伸出右边界的元素 0、坏图 0 |
| `node tools/check-motion.mjs`（动效真跑） | Hero 每次都通过：三行按位置 遮罩 → 模糊 → 打字机，起始约 10 / 450 / 900 ms，intro-ready 约 1.7 s，从未触发 `.hero-fallback`；按钮只淡入不位移（逐帧检查从第 9 次起加入，之后每次都过）。最终构建跑 2 次：1 次全过，1 次只在跨页锚点「cubby → #code」一项失败（−184 px）；此前带博客块的中间版本 9 次有效运行 8 次全过、1 次同项失败（−18 px）。Hero 相关检查 11 次全过。锚点项是 DONE.md 记录的既有问题，见下方「发现」2 |

## 工具改动

- `tools/check-home.py`：检查 1 只看三个板块（首页现在还有 #products）。新增 10–16：版面顺序（再出现任何多余 section 即失败）、Hero 副标 = 常量、
  旧副标消失、两个按钮及 `target/rel`、按钮淡入只动 opacity（读产物 CSS）、产品条（图标存在且 ≤64 KB、名称 = 条目标题、一句话、
  动作 URL ∈ 条目 links、Details 链接）、Hero 与产品条文案不准出现数字、Work 眉题紧贴 #code、每页页脚是同一行同一样式的 8 个链接且 Blog 一次、
  新增可点元素不带 translate/scale/rotate/animate 类、JSON-LD 三实体与 `@id` 互引 / logo 为正方形 ≥112 px / 每页引用可解析。
  `--online`：首页全部外链 200（遇 429 重试一次）。
- `tools/check-projects.py`：`--dist` 要求产品页 author / publisher 指向本页定义的 Person / Organization `@id`；`--schema` 校验本页全部 JSON-LD 块。
- `tools/shoot-pages.mjs`：`clip=A..B` 区间截图（从 A 顶到 B 底）；`--profile` 指定 chromium 配置目录（并行会话不再抢同一目录的锁）；
  区间截图超出视口时同样先把 vh 高度钉成像素。
- `tools/check-motion.mjs`：`--profile`（它退出时会**删除**配置目录，共用默认路径会删掉别的会话正在用的目录）；
  期望的 Hero 词序从 `Code / Motion / Visual` 改回 `Motion / Visual / Code`——a3d7400 回退 Hero 后没同步，**在未改动的 main 上也报 2 项 FAIL**；
  新增 Hero 按钮「只淡入、不位移」的逐帧实测。
- 新增 `tools/probe-anchor-landing.mjs`：同一个跨页锚点点击重复 N 次，打印落点分布和最差一次的滚动轨迹（为「发现」2 写的）。
- 新增 `tools/trace-build-requests.mjs`：记录构建期全部出站请求（为「博客块的删除」写的）。

## 发现（不在本任务范围，知会）

1. **motionrules.com 的 `favicon.svg` 里有旧身份**：`<metadata>MotionRules by ZERB LION / motionrules.com</metadata>`（今天线上实抓）。
   10-07 那轮清扫的口径是六个页面的可见文本 / meta / schema，SVG 内部元数据不在口径内；是否要改（和 `data-origin` 一样可能零 SEO 影响），归 motion_design 那边定。
   另：MotionPilot 的 Exchange 图标与这个 favicon 是同一张图（见「图标」）。
2. **跨页锚点落点的竞态比 DONE.md 记的范围大，且页面变高后最坏情况更深**。`tools/probe-anchor-landing.mjs` 各跑 12 次「/project/cubby/ → ← Back to work」：

   | 构建 | #code 落点（应为 96 px） | 落到视口顶上方 |
   |---|---|---|
   | 未改动的 main（55ee1dc） | −16 … 192 px | 3 / 12 |
   | 本分支 | −87 … 153 px（check-motion 另有一次 −184） | 3 / 12 |

   频率相同，说明是既有问题；但本分支 #code 上方多了产品条（#code 从 900 px 移到 1449 px），偏差幅度跟着变大，最坏时 "Code" 标题会被页头挡住。
   滚动轨迹（每 50 ms 采样）：点击后约 200 ms 开始滚动，约 300 ms 内停住，之后不再动；停住的位置每次不同。
   猜测与 DONE.md 一致——路由自己的 hash 滚动与 `motion.ts` 在 page-load 120 ms 后的 `lenis.scrollTo(..., { immediate: true })` 相互抢；
   另外 `global.css` 给 html 设了 `scroll-behavior: smooth`，可能让本应瞬时的滚动也变成平滑的。**根因未查实**，没有改 `motion.ts`。
3. check-motion 的词序过期（见「工具改动」），已修。

## 待拍板

1. **Hero 副标措辞**：目前是候选句，改 `index.astro` 顶部 `HERO_TAGLINE` 一处即可。附带一点：新副标里没有 "zosc" 这个词，
   首屏可见文字里不再出现品牌词（logo 是图，alt 为 zosc）；title / meta / schema / 页脚仍都有。
2. **MotionPilot 图标**：按指示保留它自己的 Exchange 图标（重绘为 SVG）。但这张图与 motionrules.com 的 favicon 是同一张——
   如果希望 MotionPilot 也和 motionrules.com 那边区分开，需要给 MotionPilot 另画（面板 / 关键帧意象），Adobe Exchange 上架图标要不要跟着换也得一起定。
3. **跨页锚点竞态**（「发现」2）：要不要单开一个任务修 `motion.ts` 的 hash 落点。产品条让最坏情况更明显，建议在合并 v3 之前或同时处理。
4. **Organization 与 Person 同名 "zosc"、共用同五条 sameAs**（按任务要求）。风险：Google 可能把两者合并成一个实体，也可能把信号拆到两个实体上。
   保守的替代方案是 sameAs 只留在 Person 上，Organization 只给 url / logo / founder。`worksFor` 与 `affiliation` 两个都加了，可以只留一个。
5. 细节：`Details →` 用了句首大写（与站内 "View all work"、"Back to work" 一致，任务原文写的是小写）；README.zh-CN.md 没加解码句；
   产品按钮文案为 Get on Adobe Exchange / Open motionrules.com / App Store / Google Play；页脚三链接放在 Blog 与 Email 之间。
