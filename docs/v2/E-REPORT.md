# v2 子任务 E「收尾」报告（2026-10-08）

分支 `worktree-agent-a1c8c7083ddf25283`，基于 `origin/v2` @ `5a8afd9`（20 个条目）。未碰 `main`、未推 `v2`、未改 `docs/TODO.md` / `docs/DONE.md`。
事实源：`docs/TODO.md`（main @ 071fe63）「v2 改版」「v2 当前状态」两节的十项拍板 + 合并前必修。

## 结论

| # | 项 | 改前（v2 @ 5a8afd9） | 改后 |
|---|---|---|---|
| 1 | MotionPilot 首页大卡 | 用 `cover.jpg`（1600×540 横幅，左半是字标）：手机 3:2 切成「nPilot.」，桌面卡片标题压在「Adobe Exchange ↗」上 | 新 `coverLarge` = `motionpilot/cover-large.jpg`（1600×520，53 KB）：**图里没有任何字**，截图窗口落在两种裁切的交集里，320–1440 宽都完整；小卡、详情页、og:image、JSON-LD 仍用原 `cover.jpg` |
| 2 | Code 板块 | 4 张（第二行只有 gateway，右半空） | **3 张**：motionpilot 大卡 + motionrules / cubby 一行两张；gateway 仍在 `/works`（Code 筛选 9 条之一） |
| 3 | Hero 三行 | Motion / Visual / Code | **Code / Motion / Visual**；动效仍按行位（1 遮罩、2 模糊、3 打字机），`motion.ts` 一行没改 |
| 4 | MotionSheet（`zerb-cc-cd`） | 外链 `https://zerb.cc.cd`；封面写 `zerb.cc.cd ↗` | 外链 `https://motionrules.com/app`（直接 200）；封面那一行改为 `motionrules.com/app ↗` |
| 5 | MotionRules | 无 `offers` | `app.free: true` → JSON-LD `offers {price "0", USD}` |
| 6 | 「← Back to work」 | 20 页全部 `/#visual` | 按条目第一个板块：`#code`×9、`#motion`×3、`#visual`×8 |
| 7 | favicon 改名说明 | HTML 注释，进了全部 24 个页面（含 `zerb-favicon-*`） | 挪进 Layout frontmatter 的 JS 注释（原文逐字保留）；产物里 `zerb-favicon` **0** |
| 8 | README 中英 | H1 与三支柱列表 Motion · Visual · Code | **Code · Motion · Visual**，其余一字未动 |
| — | 首页长度 1440 / 390 | 6371 / 6013 px | **6034 / 5786 px**（与 C 报告里「只留 3 张」的预测值一致） |
| — | 构建 | 通过 | 通过，warn/error 0 |

## 每项做法

### 1. MotionPilot `coverLarge`
- **几何**：大卡 `object-fit: cover` 居中，`lg`（1024）以下 3:2、以上 1600:430（`ProjectCard.astro`）。一张 1600×H 的图：3:2 只留中间 1.5H 列，1600:430 只留中间 430 行；主体必须落在两者交集里。
  取 H=520 → 交集是 x 410–1190、y 45–475。截图窗口放在 x 488–1112、y 80–340（624×260，2.4:1）。
- **为什么窗口偏上**：手机上卡片标题在左下、占底部约 25%（390 宽：标题字顶约在卡高 76% 处），窗口底边放在 0.65H，320 宽手机仍留约 8 px、390 宽留约 25 px；桌面上窗口顶边离卡片上沿 35 px（1600 尺度，1440 宽约 30 px，1024 宽约 20 px；hover 放大 1.05 后仍有余量）。
- **没有任何文字**：字标和说明都不放（卡片自己叠标题，图里再写一遍就是 C 指出的「名字出现两遍」）；中间是商店截图 #2（B 用过的干净那张，`Spec` 面板 + 关键帧，无旧品牌标题栏），裁 `(370, 338, 1360, 750)` = 「APPLY TO SELECTED KEYFRAMES / gentle / Apply」+ 时间线上的关键帧。左下角只有网格。
- **装饰（拿不准点 3）**：一条横贯的 ease 曲线（两端关键帧菱形 + 贝塞尔手柄），从窗口背后穿过，填满桌面两侧的空白；手机裁切里只露出窗口左右两小段。纯图形、无字。纯底版本也渲染过，见截图 `alt-plain-*`。
- **底色/网格/光晕**沿用 B 横幅的同一套 token（`#0e0e11→#050505`、57 px 网格、`#e7503a` 光晕）。
- **可复跑**：`tools/product-covers.py` 新增任务 `motionpilot-large`（`python3 tools/product-covers.py motionpilot-large`），2x 渲染再缩到 1600 宽；
  重跑一次产物 sha256 逐字节相同（`61db02f3…71da72`）。源截图仍是脚本里已有的 `MP_SHOT_SPEC`。几何和理由写在 `MP_LARGE` 上方注释里。
- `motionpilot.md` 只加一行 `coverLarge:`。

### 2. Code 板块 3 张
- `openwebui-cliproxy-gateway.md` 删掉 `featured: true` 一行（默认 false，和其余非首页产品写法一致）。

### 3. Hero 三行
- `index.astro` 只改三行 `.hl-t` 里的词，以及每行小球的 `data-dot`：
  `data-mask>Code` + `data-dot="code"` / `data-blur>Motion` + `data-dot="motion"` / `data-type>Visual` + `data-dot="visual"`。
  `data-mask` / `data-blur` / `data-type` 留在原行位（`motion.ts` 取 `lines[0..2]`，`[data-mask]` 还挂着 CSS 遮罩规则），DOM 结构、class、元素数量不变。
- **「对应链接/锚点」查证结果**：Hero 没有任何链接或锚点，历史上也从来没有——`git log -S'data-dot'` 只有引入它的 `28b8061`，全仓没有给 `[data-dot]` 绑点击的代码（`motion.ts` 只是把它放进光标 hover 选择器，悬停显示「Go」）。
  每行唯一跟板块对应的属性是 `data-dot`：它决定小球性格（global.css：Motion 滚动、Visual 呼吸光晕、Code 光标式闪烁；`motion.ts` 让 motion 那颗被光标弹开），所以让它跟着词走。
- `motion.ts` 里的变量名和注释（`mText/vText/cText`、「Code is the only typewriter」）仍按旧顺序命名，按要求没改；在 `index.astro` frontmatter 里写了一段说明，避免以后有人照注释误改（frontmatter 注释不进页面）。
- 实测见「校验 / check-motion」：三行分别在 15 / 450 / 900 ms 开始，与 `motion.ts` 的 0 / 0.45 / 0.9 s 一致。

### 4. MotionSheet
- `curl -sSL https://motionrules.com/app` → `200`，0 次跳转，`<title>MotionSheet · Lottie handoff & audit · MotionRules</title>`；带尾斜杠的 `/app/` 是 308 → `/app`，所以用不带斜杠的。
- `cover.svg` 原本就有「MotionSheet.」字标，所以「重做」落到一行：`zerb.cc.cd ↗` → `motionrules.com/app ↗`（同字号、同色 `#ff6f59`、同位置）。其余元素逐字未动，风格自然一致。旧 SVG 没留副本（git 历史可找回）。
- slug、目录 `zerb-cc-cd` 不动；正文 `project-bodies/zerb-cc-cd.html` 本来就没有 `zerb.cc.cd`。

### 5. MotionRules 免费
- `motionrules.md`：`app` 下加 `free: true`；原注释「motionrules.com 没写价格所以不加」改成「依据所有者 2026-10-08 的确认，站点本身未标价」。

### 6. Back to work
- `project/[slug].astro`：`href={`/#${pillars[0] ?? 'visual'}`}`（schema 允许空数组，回退到原来的 `#visual`）。

### 7. favicon 注释
- Layout 里那段 HTML 注释原文搬进 frontmatter（`//` 注释，前面加两行说明为什么放这里）；`<link rel="icon">` 四行原样。页面源码顶部的版权 HTML 注释是有意输出的，没动。

### 8. README
- 两份 README 只改 H1 和三支柱列表顺序（4+4 行）。

### 校验脚本的改动（为了让本轮的断言可复跑）
- `tools/check-home.py`：默认期望 Code = `motionpilot, motionrules, cubby`（`EXPECT_CODE`，用户决定；`--code` 可覆盖）并要求网格整行；每个板块大卡用 `coverLarge ?? cover`；`/works` 链到全部 20 条；
  旧名检查从 `zerb-logo` 扩到 `zerb-logo / zerb-favicon / zerb.cc.cd`，扫描加 `.svg`（`zerb.cc.cd` 原来就藏在 SVG 里）；新增 8（Hero 词序 / 行位动效标记 / `data-dot` 跟词）和 9（Back to work 按板块）。
- `tools/check-projects.py`：封面 ≤ 400 KB；`offers`（price "0"）当且仅当 `app.free: true`。
- 新增 `tools/check-motion.mjs`：**不**模拟 reduced-motion，真实跑 `motion.ts`；页内 rAF 逐帧采样 Hero 三行，另存 3 帧 + 终态；真实鼠标点击验证锚点。头注释写了为什么分两次加载（截图会让渲染卡 100–250 ms，采样出现空洞）。

## 校验（全部针对最终提交状态；命令在仓库根目录执行）

```
$ cd app && rm -rf dist .vercel && npm run build
[build] Complete!
[patch-vercel-redirects] patched 24 redirect routes
npm run build exit=0          构建日志 grep -ciE "warn|error" = 0

$ python3 tools/check-home.py
1. homepage section order + cards
  ok   sections: #code → #motion → #visual
  ok   #code (featured only, 9 in pillar): 3 cards ['motionpilot', 'motionrules', 'cubby']
  ok   #code grid: 1 large + 2 small cards, rows full
  ok   #code large card image /media/images/projects/motionpilot/cover-large.jpg
  ok   #motion (first 5 by order, 3 in pillar): 3 cards ['vivo-xr', 'luna-os-sinus', 'china-mobile-cave']
  ok   #motion large card image /media/images/projects/vivo-xr/GLASS.jpg
  ok   #visual (first 5 by order, 8 in pillar): 5 cards ['dynamic-weather-art', 'luna-os-ar-theme', 'time-garden', 'diy-motion-elements', '3d-ui-exploration']
  ok   #visual large card image /media/images/projects/dynamic-weather-art/10.webp
2. titles
  ok   <title> = zosc — Code · Motion · Visual          （og:title / twitter:title 同）
  ok   "Motion · Visual · Code" in 0 of 24 built HTML files
3. nav + /works filter order
  ok   header + mobile menu: ['code', 'motion', 'visual', 'code', 'motion', 'visual']
  ok   /works filters: ['all', 'code', 'motion', 'visual']
  ok   /works links all 20 live entries (non-featured products included)
4. old names in built text files: zerb-logo, zerb-favicon, zerb.cc.cd
  ok   0 occurrences in 34 served static text files (dist/client: HTML/CSS/JS/SVG/XML/JSON)
  ok   server bundle: 0 references (2 public-file inventory entries — kept old files, not references)
  ok   header logo /media/images/common/brand/zosc-logo.png referenced and present
5. reference integrity (built HTML + CSS)
  ok   158 distinct /media + /fonts references, all present under app/public
  ok   29 other root-relative references resolve in dist/client
6. og:image per page        （8 个产品逐条 ok，与 C 时相同；4 个非项目页 + 12 个旧项目页仍是默认图）
7. about intro paragraphs
  ok   3 paragraphs, words [19, 59, 72], .lead on paragraph 1 only
8. hero headline
  ok   words: Code / Motion / Visual
  ok   effects by line position: ['data-mask', 'data-blur', 'data-type'] (mask wipe / blur / typewriter)
  ok   data-dot follows the word: ['code', 'motion', 'visual']
9. project pages: '← Back to work' -> the entry's first pillar section
  ok   20 pages: #code×9, #motion×3, #visual×8
OK
```
- 第 4 步的 2 个 inventory 条目是 `zerb-logo.png`（C 时就有，旧文件按规定保留）；`zerb-favicon` 在 public 下没有同名文件，所以服务端出现任何一次都会判 FAIL。
- 第 5 步比 C 时多 1 条引用 = `cover-large.jpg`；本地静态服务器实取：`cover-large.jpg` 200 `image/jpeg` 54889 B，`zerb-cc-cd/cover.svg` 200 `image/svg+xml`。
- **反向测试**（证明新断言会咬人）：往产物里改回 Hero 词序、把大卡图换回 `cover.jpg`、cubby 的 Back 改成 `#visual`、SVG 写回 `zerb.cc.cd`、about 页塞一个 `zerb-favicon-32.png` 注释 → 5 条 FAIL 全部命中；还原后 OK。

```
$ node tools/check-about.mjs --before <v2 的 about.html> --private-deny /data/Projects/zosc-career/tools/public-denylist.txt
1–3 ok（年份 0、通用/私有词 0、13/13 引用存在）   4. 201 words → 201 words（about 未改）
5. AI system prompt: about 全文未截断、hi@zosc.com、无旧 Gmail、0 private-term
RESULT: PASS

$ python3 tools/check-projects.py --dist --schema --online
20 entries, 8 of kind: product
4. external links of product entries        15 × 200
5. built pages: SoftwareApplication JSON-LD
   ok  motionrules: DesignApplication, url == canonical, offers price 0      （其余 7 个产品同为 offers price 0）
6. schema.org vocabulary (3256 terms): property names + domains checked
OK
# motionrules 的 JSON-LD：{"@type": "SoftwareApplication", "name": "MotionRules", "applicationCategory": "DesignApplication",
#   "installUrl": "https://motionrules.com/", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}

$ grep -rlF zerb-favicon app/dist/client app/.vercel/output | wc -l     → 0   （改前 dist/client 24 个 HTML）
$ grep -rlF zerb.cc.cd   app/dist/client app/.vercel/output | wc -l     → 0   （改前 4：MotionSheet 页、cover.svg、2 个服务端内容数据 chunk）
$ grep -o 'data-\(mask\|blur\|type\)>[A-Za-z]*<' app/dist/client/index.html
data-mask>Code<  data-blur>Motion<  data-type>Visual<
$ MotionSheet 页：外链按钮 https://motionrules.com/app，Back → /#code；curl → 200，0 redirects
```

```
$ node tools/check-motion.mjs --out /data/Projects/zerb-net/.render-tmp/v2-e/motion
1. hero intro (motion on, 1440x900)
       frames (ms after intro start): hero-1.png @303ms, hero-2.png @702ms, hero-3.png @1156ms, hero-final.png @2605ms
  ok   words: Code / Motion / Visual
  ok   effect markers by line: mask, blur, type
  ok   dots follow the words: code, motion, visual
  ok   line 1 "Code": mask wipe seen mid-way (--mx 83.9949% at 15 ms)
  ok   line 2 "Motion": blur resolving seen mid-way (blur(16.506px) at 450 ms)
  ok   line 3 "Visual": typewriter, 6 chars appear one by one (5 partial states, never backwards)
  ok   lines start in order: 1 @15 ms, 2 @450 ms, 3 @900 ms (motion.ts: 0 / 450 / 900)
  ok   intro-ready at 1700 ms after start; .hero-fallback never set
  ok   final: all three lines opaque, unblurred, unmasked; all chars and dots visible
2. anchors (real clicks, motion on)
  ok   header nav "code": /#code, #code top 96px          （motion / visual 同为 96px）
  ok   /project/cubby/ "← Back to work": /#code, #code at the top (145px)
  ok   /project/vivo-xr/ "← Back to work": /#motion, #motion at the top (139px)
  ok   /project/dynamic-weather-art/ "← Back to work": /#visual, #visual at the top (132px)
OK
```

浏览器实测（`tools/shoot-pages.mjs`，`python3 -m http.server` 直接服务 `app/dist/client`；与 C 一样模拟 reduced-motion，所以这些图只证明版式）：

```
shot               overflow broken  html scrollW/clientW  body        sticking  scrollHeight  sections
home-1440-full     False    0       1430/1440             1430/1430   0         6034          #code 3 · #motion 3 · #visual 5
home-390-full      False    0       390/390               390/390     0         5786
home-1024-code     False    0       1014/1024             1014/1014   0         5450          （1600:430 裁切的最窄宽度）
home-320-code      False    0       320/320               320/320     0         5522          （3:2 裁切的最窄宽度）
cubby 1440 / 390   False    0       1430/1440 · 390/390   同左        0         3175 / 3468
motionpilot 1440/390 False  0       1430/1440 · 390/390   同左        0         3222 / 3745
motionsheet-1440   False    0       1430/1440             1430/1430   0         2243
```

## 截图（`/data/Projects/zerb-net/.render-tmp/v2-e/`，已被 `.gitignore` 忽略）

| 文件 | 内容 |
|---|---|
| `home-1440-code.png` / `home-390-code.png` | 首页 Code 板块（对照 C 的 `.render-tmp/v2-c/` 同名图） |
| `home-1024-code.png` / `home-320-code.png` | 两种裁切各自的最窄宽度：大卡都不裁字 |
| `home-1440-full.jpg` / `home-390-full.jpg` | 首页整页 |
| `cubby-1440.jpg` / `cubby-390.jpg`、`motionpilot-1440.jpg` / `motionpilot-390.jpg` | 产品页整页 |
| `motionsheet-1440.png` / `motionsheet-cover-1440.png` | MotionSheet 页首屏 / 新封面 SVG 单独截取 |
| `cover-large.jpg` | 新 coverLarge 原图 |
| `motion/hero-1.png`…`hero-3.png`、`hero-final.png` | Hero 入场三帧（303 / 702 / 1156 ms：Code 已擦出 → Motion 模糊对焦 → 「Visua」打字中）+ 终态 |
| `alt-plain-*` | 不加曲线装饰的版本（窗口略大的早期几何），供对比 |

中间产物：`~/render-tmp/product-covers` 由脚本自删；`~/render-tmp/chrome-profile-motion` 由 check-motion 自删；`~/render-tmp/chrome-profile-shoot`（本轮 shoot-pages 建的）已删。

## 拿不准 / 待拍板

1. **动效跟词的对应变了。** 动效按行位不动，于是现在 **Code 是遮罩擦出、Motion 是模糊对焦、Visual 是打字机**（原来打字机是给 Code 的）。小球性格跟词走，Code 那颗仍是光标式闪烁，只是在第一行。
   这是「只换文字」的直接结果，用户已接受；若想让 Code 仍然打字，需要把 `motion.ts` 改成按 `data-*` 选行，属于动效改动，本轮没做。
2. **跨页锚点落点高度不稳定（既有问题，非本轮引入）。** 从项目页回首页时，目标板块总是正确、hash 正确，但板块上沿离视口顶 21–160 px 不等（4 轮 12 次 Back：110/139/154、139/160/145、21/29/126、145/139/132；从项目页点页头导航 Code/Motion/Visual 也一样：126/157/93/29/93），
   而同页点页头导航稳定在 96 px。逻辑在 `motion.ts` 的 `astro:page-load`（120 ms 后 `lenis.scrollTo(el, { offset: -96, immediate: true })`），推测与路由自己的 hash 滚动（`html { scroll-behavior: smooth; scroll-padding-top: 96px }`）抢跑有关——这是推测，未核实。
   改它要动 `motion.ts`，本轮未动；`check-motion.mjs` 对跨页只断言「目标板块在顶部」，并在注释里记了这组数。
3. **coverLarge 的曲线装饰**是我加的设计元素（满足「中间与左下无字」，但任务没要求装饰）。不要的话：删 `MP_LARGE_HTML` 里的 `<svg class="k">…</svg>` 后重跑 `python3 tools/product-covers.py motionpilot-large`，纯底效果见 `alt-plain-*`。
4. `check-home.py` 现在把 Code 三张写死成默认期望（这是本轮要的断言）；以后调整 featured 要同步改 `EXPECT_CODE`，否则会 FAIL——有意为之。
5. 动效与 hover 仍需在 Vercel 预览上人工看一眼（`check-motion` 证明了时序与终态，但「好不好看」只能人判断）；推送后等部署完再 `Ctrl+Shift+R`。
6. MotionSheet 封面 SVG 作为 `<img>` 时用不了站点字体，字标回退到系统无衬线——原 SVG 就是这样，未改。
