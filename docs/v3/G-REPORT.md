# v3 子任务 G「删产品条，Code 板块即 Products」报告（2026-10-08）

分支 `worktree-agent-a898fb00cb6ffed83`，基于 `origin/main` @ `5ea1709`（含 v3-F）。未合并、未碰 `main`。
按要求**没有改** `docs/DONE.md` / `docs/TODO.md` / `README.md`（Codex 正在主 checkout 里改这三个文件），没碰 `lab/`、产品 `.md`、媒体文件。

## 结论

| 项 | 改前（5ea1709） | 改后 |
|---|---|---|
| 产品条 | Hero 下三张带边框小卡（图标 + 名称 + 一句话 + 药丸按钮 + `Details →`） | **删除**。区块、数据常量、校验断言都删了；图标文件留在 `app/public/media/images/products/`，页面不再引用 |
| 眉题 | `Products`（产品条上）+ `Work`（#code 上） | **`PRODUCTS` 在 #code 上**（`id="products"`），**`WORK` 在 #motion 上**（`id="work"`），F 的眉题原样复用：同一段 class |
| Code 三张大图卡 | 只有图和标题 | 每张卡下面加一行直达链接：MotionPilot → `ADOBE EXCHANGE ↗`；MotionRules → `MOTIONRULES.COM ↗`；Cubby → `APP STORE ↗ · GOOGLE PLAY ↗` |
| Motion / Visual 卡 | — | 不变，没有直达行（条目里没有 `links`） |
| Hero | 三行大字 + 副标 + 两个按钮 | **不变**。现在首页的按钮只剩这两个 |
| 导航 / 锚点 | `/#code` `/#motion` `/#visual` | 不变 |
| 首页高度 1440 | 6246 px | **5897 px（−349，−5.6%）** |
| 首页高度 390 | 6506 px | **5627 px（−879，−13.5%）** |

## (a) 还是 (b)：选 (a)

直达行放在卡片的 `<a>` **之外**，紧接在 `</a>` 后面，与卡片一起包在一个 `<div>` 里（`app/src/components/CardLinks.astro`）。
`ProjectCard.astro` 一行没动，所以卡片的 hover（遮罩淡出、图片放大、标题变色）与点击区域都和原来一模一样。
没选 (b)（卡片改 `<article>`，图和标题各自是链接）：(b) 要重写 ProjectCard，而 /works 也在用 ProjectCard；整卡可点会变成只有图和标题可点，hover 也要重新接。

**放在「下一行」，不放「与标题同一行右对齐」**，原因有三：
1. 大卡的标题压在图片上，图片下方根本没有标题行。要和标题同行，只能把链接绝对定位叠到图上。这样一来，鼠标从图移到链接上就离开了卡片的 `<a>`，图片遮罩会在指针还在图上时变回来，等于动了卡片的 hover。
2. 卡片的 `<a>` 带 `.reveal`，入场时会上移 28 px。叠在同一行的链接不能跟着动（可点元素不许位移），入场期间就会和标题错开。
3. 小卡标题行右侧是年份的位置。Code 卡现在没写年份，但同行方案会跟年份抢位置。

位置细节：大卡这一行加了 `px-5`，和压在图上的标题（`inset-x-5`）左对齐；第一版没加，链接贴着图片左边缘，看着像一行孤立的字（截图比较过）。
小卡这一行在标题下方，与标题左对齐。两种卡里，链接的文字框都离上方元素 12 px（`mt-1` + 链接 `py-2`）。`py-2` 是为了加大点击热区，因为自定义光标是跟随的、会滞后于真实指针。

## 每项做法

1. **删产品条**（`app/src/pages/index.astro`）：删掉 `<section id="products">`、F 的 `<div id="work">`、`PRODUCTS` 常量和 `products` 映射。
   产品条没有单独的组件文件，也没有专属 CSS（全是工具类），所以没有组件或样式要删。
2. **直达数据从 `.md` 的 `links` 取**：`directLinks(entry)` 的规则是 **store / download 类型的链接；都没有就取第一条**（例如网页工具，第一条就是工具本身）。
   这条规则正好得到任务指定的四个链接，文字直接用 `links` 里的 `label`：
   - motionpilot：`Adobe Exchange`（store）
   - motionrules：`motionrules.com`（没有 store，取第一条 site）
   - cubby：`App Store` + `Google Play`（两条 store）

   Motion / Visual 的条目都没有 `links`，所以不渲染这一行。
   Hero 两个按钮的 URL 必须落在卡片的直达链接里，否则**构建直接报错**。这条护栏原来是对产品条的，现在改成对卡片：Hero、卡片、产品页三处不会悄悄分叉。
3. **样式**：行容器的字号、大小写、字距和页脚那行小字一样：`text-sm uppercase tracking-wide`。默认 `text-mist`，链接 `hover:text-paper`。
   两个链接之间用 `·` 分隔（`aria-hidden`）。没有药丸边框，没有橙色填充；`↗` 包在 `aria-hidden` 的 span 里。
   链接都是 `target="_blank" rel="noopener noreferrer"`，`data-cursor="Open"`（和 F 的直达按钮一致）。
4. **入场**：链接不能位移，所以这一行不加 `.reveal`。改为 `global.css` 里 6 行规则：`html.js .reveal + .card-links` 先是 `opacity: 0`，
   卡片拿到 `.is-in` 时淡入，用 `.reveal` 同一套时长和曲线，**只动 opacity**。这条规则只在 `prefers-reduced-motion: no-preference` 下生效，
   没有 JS 或开了减少动态时直接显示。这样这一行不会先于卡片出现（从导航点 Code 落到 #code 时，卡片正在淡入，链接不会已经立在那里）。
   check-motion 逐帧实测：行和卡片在同一帧开始淡入，180 帧里行的文档坐标始终是同一个点。
5. **眉题**：在 `pillars.map` 里按 `EYEBROWS` 表在对应板块前面渲染，markup 就是 F 的那段。第一个眉题紧跟 Hero，保留 F 原来的 `pt-10`（与 Hero 底部的距离不变）。
   三个 `<section>` 的源码只多了外面一层 `<Fragment>`。
6. **一处 Astro 坑**：在 CardLinks 嵌套的 map 里，`{l.label} <span>↗</span>` 中间的空格会被编译器吃掉，实际渲染成 `Adobe Exchange↗`。
   改用显式的 `{' '}`；Hero 按钮的同样写法不受影响。原因写在组件头注释里。

## 校验（全部为最终构建）

| 命令 | 结果 |
|---|---|
| `cd app && npm run build` | exit 0；输出 77 行，含 warn/error 的行 0 |
| `python3 tools/check-home.py --online` | **OK**：ok 63 行，FAIL 0，exit 0 |
| 　check 10 版面 | `sections: #code → #motion → #visual (nothing else)`；`hero → Products label → #code → Work label → #motion → #visual → AI Ask` |
| 　check 11 Hero | 副标 = `HERO_TAGLINE`；两个按钮 Get MotionPilot / Open MotionRules 都在，新标签页打开；按钮淡入只改 opacity |
| 　check 12 产品条已无 | 首页上查不到 #products section、`/media/images/products/` 图标、`Details →`、产品条按钮文字、`rounded-2xl border border-line bg-ink-soft`、三句一句话 |
| 　check 12 不嵌套 | `no <a> inside an <a> (37 links on the page)` |
| 　check 12 直达行 | 三张卡各自 `Adobe Exchange ↗` / `motionrules.com ↗` / `App Store ↗ · Google Play ↗`，URL ∈ 条目 `links`，`_blank` + `noopener noreferrer`，无药丸/填充类，类名不带位移 |
| 　check 12 其他 | #motion、#visual 各 3 张卡，无直达行、无外链；行的字体类 = 页脚行（`text-sm tracking-wide uppercase`）；淡入 CSS 只有 opacity，且仅在 no-preference 下生效 |
| 　check 13 眉题 | `"Products" label (#products) directly before #code`、`"Work" label (#work) directly before #motion`，两者 class 都等于 F 的眉题 |
| 　check 16 在线 | 首页 10 个外链全部 200；四个直达链接用纯 `curl -sL`（curl 自己的 UA）也全部 200（App Store 跳到 `/us/app/cubby-where-did-i-put-it/id6804703410`） |
| **反向测试**：同一个新 check-home 跑在 5ea1709 的页面上 | exit 1，10 项 FAIL（多出的 #products 段、眉题位置、6 类产品条残留、3 张卡缺直达行、缺淡入 CSS、两个眉题）——断言不是空转 |
| `node tools/check-motion.mjs`（动效真跑） | **OK**，exit 0 |
| 　1. Hero | 三行起始 8 / 455 / 905 ms，intro-ready 1689 ms，从未触发 fallback；按钮 1872 ms 起只淡入，147 个可见帧位置都是 (40, 656.6) |
| 　2. 锚点 | 页头导航 Code / Motion / Visual 都落在 96 px；跨页 ← Back to work 落点 61 / 126 / 127 px（F 报告里同项最坏 −184 px，现在 #code 上方没有产品条了） |
| 　3a. 行的淡入 | `row from 299 ms, card from 299 ms … document position 40,1668 in all 180 frames` |
| 　3b. 真实鼠标点击 | `Adobe Exchange ↗`：开新标签 `https://exchange.adobe.com/apps/cc/205857`，`canAccessOpener false`，首页停在 `/#code` 且没有重载；点大卡 → `/project/motionpilot/`；`Google Play ↗`（小卡）同样开新标签；点 Cubby 卡 → `/project/cubby/` |
| `node tools/shoot-pages.mjs` 三个镜头 | 横向溢出 0、伸出右边界的元素 0、坏图 0（1440 整页、390 整页 dpr2、1440 Code 区域） |
| `python3 tools/check-projects.py --dist --schema` / `node tools/check-about.mjs` | OK / PASS（没碰这两处，跑一遍确认没被波及） |

## 高度对比（同一工具 `shoot-pages.mjs`，同一台机器，改前先在本分支未改的 5ea1709 上实测）

| 宽度 | 5ea1709 | 本分支 | 差 | 构成 |
|---|---|---|---|---|
| 1440 | 6246 | **5897** | **−349 px（−5.6%）** | 产品条连眉题 −509、F 的 Work 眉题 −40；新 Products 眉题 +80、新 Work 眉题 +40、Code 两行直达（大卡一行 + 并排小卡一行）+80 |
| 390 | 6506 | **5627** | **−879 px（−13.5%）** | 产品条 −1079、旧 Work 眉题 −40；新眉题 +80 +40、Code 三行直达（单列，三行都占高度）+120 |

桌面端缩短得不多：产品条在桌面是一排三张横卡，本来就只有 509 px，而且直达行和两个眉题又加回来 200 px。手机端产品条是三张竖叠的卡（1079 px），所以缩短得明显。

## 工具改动

- `tools/check-home.py`：删掉产品条断言（图标大小、名称、一句话、Details、按钮）和 `EXPECT_PRODUCTS` / `ICON_MAX`。
  check 10 / 12 / 13 按上表重写，`--online` 加了纯 `curl -sL` 检查；`anchors()` 也去掉 `↗`，并带出 inner HTML。
- `tools/check-motion.mjs`：新增第 3 节（行淡入逐帧 + 四次真实点击）。为了确认新标签页，WebSocket 里顺带记录 `Target.targetCreated / targetInfoChanged`。
- `tools/shoot-pages.mjs`：用法注释里的示例 `hero-strip:/:1440:clip=main..#products` 指向已删的产品条，改成本轮实际用的 `code-1440:/:1440:clip=#products..#code`。

## 截图（clip）

`v3g-home-1440-full.jpg` id `e0jqkc9ndd` · `v3g-home-390-full.jpg` id `s477s288cr` · `v3g-code-1440.png` id `nc68d3kbm1`。
截图按 shoot-pages 的设计开了 `prefers-reduced-motion`，只代表版式；动效由 check-motion 实测。本地副本在 `~/render-tmp/v3g/shots/`。

## 发现 / 知会

1. **`↗` 不在自托管字体里**：`mulish-latin.woff2` / `montserrat-latin.woff2` 都没有 U+2197，站内现有的 `→`（U+2192）也一样没有，两者都靠系统字体回退显示。
   U+2197 默认是文字样式（不是 emoji），按理和 `→` 一样渲染，但**我没在 iOS / Android 真机上看过**，请在手机上看一眼。
2. **受保护字符串**：仓库里四个受保护串，逐文件计数与 HEAD 相比只少了一处：`index.astro` 里产品条常量硬写的 Google Play URL（含 `com.zerblion.findly`），随产品条一起删了。
   这个包名本身没动：`cubby.md` 里那条原样保留，首页现在从 `cubby.md` 渲染出这条链接（check-home 输出可见）。
3. 在 1440 截图上量两行字形之间的像素距离：大卡标题到直达行 **57 px**，小卡 **26 px**。
   大卡多出来的部分来自卡片本身：标题压在图片底部、离图片下边缘 20 px，标题下面还有 hover 才出现的 3 px 橙线占位（`mt-2`）。
   要再贴近，只能把链接叠到图上，会碰到上面 (a) 的第 1 条问题，所以没做。

## 待拍板

1. **Code 板块底部仍是 `View all work →`**（链到 `/works/?f=code`）。现在上面的眉题是 PRODUCTS，这句读起来有点别扭，可以改成 `View all products →`。任务没要求，没改。
2. **大卡直达行的位置**：现在在图片下方、与压在图上的标题左对齐，字形间距 57 px（小卡 26 px）。如果希望更贴标题，唯一的办法是叠到图片底部右侧，代价是 hover 和入场时的错位，见 (a) 的第 1、2 条。
3. 眉题 `id`：按任务改成 `products` / `work`，`/#products` 现在落在 Code 板块的眉题，`/#work` 落在 Motion 板块的眉题。仓库里没有任何地方链到这两个锚点。
