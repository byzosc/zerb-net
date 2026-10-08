# v2 子任务 C「首页顺序与标题」报告（2026-10-08）

分支 `worktree-agent-a4232382de7c60fdf`，基于 `origin/v2` @ `ded6475`（A、B 已合并，20 个条目）。
未合并、未碰 `main`、未推 `v2`。事实源：`docs/TODO.md`「v2 改版」一节。按主会话要求，本分支**没有改** `docs/TODO.md` / `docs/DONE.md`。

## 结论

| 项 | 改前（v2 @ ded6475） | 改后 |
|---|---|---|
| 首页板块顺序 | Motion → Visual → Code | **Code → Motion → Visual**（板块名、锚点 id 不变） |
| Code 板块卡片 | 按 order 取前 5：motionpilot · motionrules · cubby · gateway · nas-monitoring | **只取 `featured: true`**：motionpilot · motionrules · cubby · openwebui-cliproxy-gateway（4 张） |
| Header 导航（桌面 + 手机菜单） | Motion · Visual · Code | **Code · Motion · Visual** |
| 默认 `<title>`（og/twitter 跟随） | `zosc — Motion · Visual · Code` | **`zosc — Code · Motion · Visual`** |
| 构建产物里 `Motion · Visual · Code` | 24 个 HTML 全有（title + 页面源码注释） | **0 / 24** |
| 页头 logo URL | `/media/images/common/brand/zerb-logo.png` | **`/media/images/common/brand/zosc-logo.png`**（逐字节复制，旧文件保留） |
| 产品页 og:image / twitter:image | 全站默认 logo（253×83） | 6 个栅格封面产品用**自己的封面**；2 个 SVG 封面产品与其余页面仍是默认图 |
| about 介绍段 | 一整段 150 词 `.lead` 大字（A 报告估计手机约 30 行） | **3 段**：首段 `.lead`（19 词）+ 两段正文字号（59 / 72 词），**字词零改动** |
| 首页长度（1440 / 390） | 6371 / 6240 px | **6371 / 6013 px**（桌面不变，手机短 227 px） |
| 构建 | 通过 | 通过（warn/error 0） |

## 做了什么、为什么

1. **板块顺序**（`app/src/pages/index.astro`）：`pillars` 数组改成 code、motion、visual。`<section id>` 仍是
   `code` / `motion` / `visual`，跨页锚点逻辑（`motion.ts` 里 `document.querySelector(location.hash)` + Lenis
   `scrollTo`）按 id 查找，与顺序无关。Hero → 三板块 → AI Ask 的骨架不变，没有改任何脚本、动效或可点元素的样式。
2. **Code 取 featured**：每个板块对象带 `featuredOnly` 标记，取数统一走 `cardsFor()`。规则见下一节。
   没有改成「只要板块里有 featured 就只取 featured」这种隐式规则——那样以后给 Visual 某条加 featured，
   Visual 板块会突然只剩一张卡。B 在 `content.config.ts` 里的字段注释原来写「首页板块显示 featured 条目」，
   容易被读成三个板块都看这个字段，已改成准确描述（只改注释）。
3. **标题与顺序一致**（`Layout.astro`）：默认 title 改为 `zosc — Code · Motion · Visual`；默认 description
   只把三项列举改了顺序（`Motion, visual art, and living interactive interfaces` →
   `Living interactive interfaces, motion, and visual art`），身份短语见待拍板 4；页面源码顶部注释里的同一串也改了
   （HTML 注释会原样进页面）。`knowledge.ts` THREE PILLARS 改为 Code、Motion、Visual（构建产物实抓的 AI prompt 已确认）。
   `about/index.astro` 的 meta description 结尾 `across motion, visual art, and code` → `across code, motion, and visual art`
   （按「grep `Motion, Visual`」口径命中；这是模板里的 meta，不是 A 的 about 正文）。
   `alternateName` 里的 ZERB 系列**没动**。
4. **about 三段**（`app/src/migrated/about.html`）：只在两处句号后插入 `</p>\n\n<p>`，首段保留 `class="lead"`，
   后两段是无 class 的 `<p>`（模板现有正文样式 1.05rem）。切分：身份与方法（第 1 句）/ 雇主锚点（vivo + JMGO 一句、
   "He has also led…" 一句——"also" 承接上句，所以同段）/ 能力与本站（CS 背景、被平台首页推荐、"Here it lives…"——
   "it" 指上一句的 "His work"，所以同段）。去掉标签后的文本与改前**逐字相同**（下方校验），AI prompt 里的 about 文本仍是 1357 字符。
   `tools/check-about.mjs` 的第 4 步原来只打印 `.lead` 段词数并标注「目标 120–180」，切分后会打印「19 词」误导人，
   改为打印「第一条 `<hr>` 之前的介绍：总词数 + 每段词数 + `.lead` 在哪段」；判定逻辑一行没改。
5. **logo 改名**：`cp -p` 出 `zosc-logo.png`（sha256 与旧文件相同 `dbf749e2…c404c4`），`Header.astro` 指向新文件。
   全仓 `grep -rn zerb-logo` 除文档外只有这一处引用。说明写在 frontmatter 注释里而不是 HTML 注释里——
   第一版写成 HTML 注释，会把旧文件名带进每个页面，构建前发现并改掉。
6. **产品页 og:image**：`Layout.astro` 加可选 prop `image`（`ogImage = image ?? 默认图`，其他 meta 逻辑不动）；
   `project/[slug].astro` 对 `kind: product` 且封面是 jpg/png/webp/gif 的条目传 `new URL(cover, Astro.site).href`
   （与同页 JSON-LD `image` 同一公式，`Astro.site` = `https://zosc.com`）。**SVG 封面不传**：X / Facebook / LinkedIn 的
   分享卡不渲染 SVG，传了等于分享时没图，所以 windows-never-sleep、s25edge-usa 回退默认图。旧 12 个项目页不传（见待拍板 7）。
7. **顺手同步（超出字面清单，各一行可回退）**：`/works` 筛选按钮顺序改为 All · Code · Motion · Visual（与首页、导航一致）；
   `.gitignore` 加 `.render-tmp/`（截图目录原先未被忽略）。

## 取数规则（两种板块）

| 板块 | 规则 | 现在的结果 |
|---|---|---|
| Code（`featuredOnly: true`） | 该板块里 `featured: true` 的条目，按 `order` 升序，最多 5 张 | 4 张：motionpilot(50) · motionrules(51) · cubby(52) · openwebui-cliproxy-gateway(53)；其余 5 个（nas-monitoring、zero-build-blog、windows-never-sleep、s25edge-usa、MotionSheet）只在 `/works` 和详情页 |
| Motion、Visual（`featuredOnly: false`） | **与 v2 前相同**：该板块按 `order` 升序取前 5 张，不看 `featured` | Motion 3 张（板块里只有 3 条）；Visual 5 张（共 8 条） |

两种板块都是第一张大卡 + 其余进两列网格，与之前的节奏相同。现状下 Motion / Visual 的条目没有一个带 `featured`，所以它们的取法不受这个字段影响，保持原样。

## 首页长度（无头 chromium 实测 `scrollHeight`，reduced-motion 下所有卡片可见）

| 状态 | 1440 宽 | 390 宽 | Code 板块 |
|---|---|---|---|
| 生产站 zosc.com（= main） | 5697 | 5331 | 1 张（MotionSheet），936 / 701 px |
| v2 合并 A、B 后，C 之前 | 6371 | 6240 | 5 张，1609 / 1610 px |
| **本分支（4 张 featured）** | **6371** | **6013** | 4 张，1609 / 1383 px |
| 对照：只留 3 张 featured（临时把 gateway 设为非 featured 构建实测，已用 `git checkout` 还原） | 6034 | 5786 | 3 张，1272 / 1155 px |

- 相对「v2 合 B 后」：桌面不变（4 张与 5 张在两列网格里都是 2 行），手机短 227 px。**首页没有变长。**
- 相对**生产站**：+674 / +682 px，原因是 Code 板块从 1 张变 4 张（TODO 定的「固定 3–4 张」本身就比现在多）。
  Motion / Visual 两个板块高度与生产站逐像素相同（1272/1609、1207/1610）。是否要压回生产站长度见待拍板 3。

## 校验（命令与输出，全部针对最终提交的状态）

```
$ cd app && npm run build
[build] Complete!
[patch-vercel-redirects] patched 24 redirect routes
npm run build exit=0                      构建日志 warn/error 计数 = 0

$ python3 tools/check-home.py --code motionpilot,motionrules,cubby,openwebui-cliproxy-gateway   # 本轮新增
1. homepage section order + cards
  ok   sections: #code → #motion → #visual
  ok   #code (featured only, 9 in pillar): 4 cards ['motionpilot', 'motionrules', 'cubby', 'openwebui-cliproxy-gateway']
  ok   #motion (first 5 by order, 3 in pillar): 3 cards ['vivo-xr', 'luna-os-sinus', 'china-mobile-cave']
  ok   #visual (first 5 by order, 8 in pillar): 5 cards ['dynamic-weather-art', 'luna-os-ar-theme', 'time-garden', 'diy-motion-elements', '3d-ui-exploration']
2. titles
  ok   <title> = zosc — Code · Motion · Visual
  ok   og:title = zosc — Code · Motion · Visual
  ok   twitter:title = zosc — Code · Motion · Visual
       description = zosc — a motion designer, visual artist &amp; developer. Living interactive interfaces, motion, and visual art; proficient in After Effects, Cinema 4D, Octane.
  ok   "Motion · Visual · Code" in 0 of 24 built HTML files
3. nav + /works filter order
  ok   header + mobile menu: ['code', 'motion', 'visual', 'code', 'motion', 'visual']
  ok   /works filters: ['all', 'code', 'motion', 'visual']
4. zerb-logo in built text files
  ok   0 occurrences in 30 served static text files (dist/client: HTML/CSS/JS/XML/JSON)
  ok   server bundle: 0 references (2 public-file inventory entries — the kept old file, not a reference)
  ok   header logo /media/images/common/brand/zosc-logo.png referenced and present
5. reference integrity (built HTML + CSS)
  ok   157 distinct /media + /fonts references, all present under app/public
  ok   29 other root-relative references resolve in dist/client
6. og:image per page
  ok   motionpilot: cover /media/images/projects/motionpilot/cover.jpg
  ok   motionrules: cover /media/images/projects/motionrules/cover.jpg
  ok   cubby: cover /media/images/projects/cubby/cover.jpg
  ok   openwebui-cliproxy-gateway: cover /media/images/projects/openwebui-cliproxy-gateway/cover.png
  ok   nas-monitoring: cover /media/images/projects/nas-monitoring/cover.jpg
  ok   zero-build-blog: cover /media/images/projects/zero-build-blog/cover.jpg
  ok   windows-never-sleep: default (SVG cover) /media/images/common/brand/cropped-logo_high2.png
  ok   s25edge-usa: default (SVG cover) /media/images/common/brand/cropped-logo_high2.png
  ok   4 non-project pages + 12 older project pages keep the default og:image
7. about intro paragraphs
  ok   3 paragraphs, words [19, 59, 72], .lead on paragraph 1 only
OK
```

- 第 4 步里「server bundle 2 处」是 Astro 服务端函数包里的 **public 目录文件清单**（JSON 路径列表，列出 public 下每个文件；
  旧 PNG 按规定保留所以在单子上），不是引用；脚本只放行这种形态，服务端出现任何其他 `zerb-logo` 都判 FAIL。
  浏览器和爬虫拿到的静态文件里是 0。
- 第 5 步同时查了根相对路径和绝对地址 `https://zosc.com/media/...`（og:image、JSON-LD image）；`dist/client/_astro` 的 2 个 JS 包里
  `/media`、`/fonts` 路径另行 grep 为 0。
- **反向对照**（证明检查会咬人）：① 对改动前的构建跑当时版本的脚本 → 18 个 FAIL：17 个正是预期的改动点（板块顺序、
  Code 第 5 张、三个 title、残留串、导航、筛选、zerb-logo 引用、新 logo 未引用、6 个产品 og:image、about 段数），
  1 个是误报（404 页自己的 canonical `/404/` 由 `404.html` 提供），随后脚本改为也接受 `<route>.html`；
  ② 往最终构建产物里塞一个不存在的 `/media/...png` 和 `/fonts/...woff2` → 这两条准确 FAIL，还原后 OK。

```
$ node tools/check-about.mjs --before <改前 about.html> --private-deny /data/Projects/zosc-career/tools/public-denylist.txt
（第 1–3、5 步每步的 ok 行合并成一行显示；原样输出用同一命令复跑即可）
1. years in about.html                 ok   0 matches for \b20[12][0-9]\b
2. generic deny-list in about.html     ok   0 matches / 0 private-term matches / name only lowercase
3. reference integrity                 ok   13/13 root-relative references resolve; 0 private-term matches in built page
4. word count (built about article)
  built article: 201 words  (source fragment: 201; must match since set:html injects it verbatim)
  intro (before the first <hr>): 150 words in 3 paragraph(s) [19 / 59 / 72]  (target ~120–180 in total)
  .lead size on paragraph: #1
  ok   article word count within 120–260
  before (c-about-before.html): 201 words  →  after: 201 words
5. AI system prompt (built /api/chat, fetch stubbed, fake key)
  ok   handler streamed the stub reply (status 200, body "stub-ok")
  about text inside prompt: 1357 chars (slice cap 4000)
  ok   about text in prompt == full about.html text (nothing truncated or dropped)
  ok   contact hi@zosc.com present / no old Gmail / no tag-gap artifacts / 0 private-term matches
  | THREE PILLARS: Code (built tools), Motion (systems of movement / interactive interfaces), Visual (worlds, surfaces, light).
RESULT: PASS

# about 字词未改（去标签、合并空白后比较；word-diff 只出现 </p> <p>）
text identical (tags stripped, whitespace collapsed): True
$ git diff --word-diff=porcelain app/src/migrated/about.html | grep -E '^[+-][^+-]'
-toolchains. Across   +toolchains.</p>   +<p>Across
-mall. A              +mall.</p>         +<p>A

$ python3 tools/check-projects.py --dist --schema --online          （逐条结果合并显示）
20 entries, 8 of kind: product
4. external links of product entries    15 × 200
5. built pages: SoftwareApplication JSON-LD   ok ×8, url == canonical
6. schema.org vocabulary (3256 terms): property names + domains checked
OK
```

**浏览器实测**（`tools/shoot-pages.mjs`，本轮新增；`npm run preview` 不可用——@astrojs/vercel 不支持 preview 命令，
所以用 `python3 -m http.server` 直接服务 `app/dist/client`，即上线的同一批预渲染 HTML）：

```
shot            overflow broken  html scrollW/clientW  body scrollW/clientW  sticking  scrollHeight
home 1440       False    0       1430/1440             1430/1430             0         6371  #code 4 → #motion 3 → #visual 5
home 390        False    0       390/390               390/390               0         6013
about 390       False    0       390/390               390/390               0         2171
about 1440      False    0       1430/1440             1430/1430             0         1505
works 1440/390  False    0       1430/1440 · 390/390   1430/1430 · 390/390   0         4201 / 5424
cubby 1440/390  False    0       1430/1440 · 390/390   1430/1430 · 390/390   0         3175 / 3468
```

- 桌面 `html` 的 1430/1440：`scrollbar-gutter: stable` 给（无头模式下不绘制的）滚动条预留了 10 px，body 实际 1430 宽，scrollWidth 不大于 clientWidth 即无溢出。
- body 有 `overflow-x: hidden`，单比 scrollWidth 可能被它掩盖，所以另外逐元素扫了「右边缘超出视口、且不在 fixed / 裁切容器里」的元素：全部 0。
- 截图前模拟 `prefers-reduced-motion`（motion.ts 会直接显示所有 `.reveal`、跳过 Lenis 和 Hero 入场），并整页滚一遍让懒加载图片加载；
  所以**截图只证明版式，不代表动效**——动效、hover、光标仍需在 Vercel 预览上人工实测（AGENTS.md「预览环境的真实局限」）。

## 截图（`/data/Projects/zerb-net/.render-tmp/v2-c/`，已被 `.gitignore` 忽略）

| 文件 | 内容 |
|---|---|
| `home-1440-full.jpg` | 首页整页，桌面 1440 |
| `home-1440-code.png` | 首页 Code 板块，桌面 1440 |
| `home-390-full.jpg` | 首页整页，手机 390 @2x |
| `home-390-code.png` | 首页 Code 板块，手机 390 @2x |
| `about-390-full.png` | about 整页，手机 390 @2x |

中间产物在 `~/render-tmp/`，已删除。

## 待拍板

1. **MotionPilot 大卡的封面裁切（最显眼，建议合并前处理）。** B 的封面是 1600×540 横幅，里面自带「MotionPilot.」字标、
   两行说明和「Adobe Exchange ↗」。大卡在手机上是 3:2、桌面是 1600:430，`object-cover` 居中裁切后：
   **手机上字标被切成「nPilot.」**（见 `home-390-code.png`）；桌面上卡片自己叠加的标题「MotionPilot」正好压在封面的
   「Adobe Exchange ↗」那行字上，名字也出现两遍（见 `home-1440-code.png`）。v2 合 B 后就已如此，但当时 Code 在第三屏，
   现在它是 Hero 下面的第一张卡。改法：给 motionpilot 加一张专供大卡的 `coverLarge`（schema 已有该字段，大卡优先用它），
   构图在 3:2 中心区与左下角都不放字——可用 B 的 `tools/product-covers.py` 出图。这是改 B 的条目和素材，所以没自己动。
2. **Hero 大字仍是 Motion / Visual / Code**，紧接着第一个板块是 Code。没改的原因：任务只点了三板块；而且 Hero 三行的入场动效
   在 `motion.ts` 里**按行的位置**绑定（第 1 行遮罩擦入、第 2 行模糊对焦、第 3 行打字机），换顺序要么让 Code 的打字机先跑，
   要么改 motion.ts 按 `data-*` 选行——属于动效改动，按 AGENTS.md 应先由用户定。选项：保持（把 Hero 当作"做什么"的标语）/ 换成 Code · Motion · Visual。
3. **Code 放 4 张还是 3 张。** 4 张时第二行网格只有 gateway 一张、右半空着（见 `home-1440-code.png`）；相对生产站首页长 +674 / +682 px。
   3 张（gateway 去掉 featured，一行字）时网格对称、+337 / +455 px。若要求与生产站同长，还得同时把 Visual 收到 3 张——那是改 Visual 取法，需另定。
4. **默认 description 的身份短语**保留了 `a motion designer, visual artist & developer`：同一顺序（motion designer → visual artist →
   developer）也出现在 Person `jobTitle`、about 首句（A 的原文）、Hero 副标题与页脚（后两处写作 creative developer），实体描述统一更重要；
   只把后面三项列举改成 Code 在前。若身份短语也要 developer 打头，会牵动 jobTitle 和 about 原文，需单独定。
5. **README.md / README.zh-CN.md** 的 H1 仍是 `zosc — Motion · Visual · Code`，正文三支柱列表也是 Motion、Visual、Code 顺序。
   README 在 GitHub 上可被抓，但不是站点本身、且属于主会话统一处理的项目文档，本分支没改。
6. **「← Back to work」**（`project/[slug].astro`）对所有项目都指向 `/#visual`（原有行为，B 已提）。产品页点回去会落在 Visual 板块。
   一行改法：`href={`/#${pillars[0]}`}`，按条目第一个板块跳。不在本任务清单里，没改。
7. **og:image 范围**：只给产品页（任务标题写的是"产品页"）；12 个旧项目页仍是默认图，扩到它们只需去掉 `kind === 'product'` 条件。
   另外默认图 `cropped-logo_high2.png` 只有 253×83，作为分享卡偏小——所有非产品页分享时都是它；2 个 SVG 封面产品若也想要自己的分享图，需要各出一张 PNG。
8. `/works` 筛选按钮顺序是我顺手改的（见「做了什么」第 7 条），不要就把那一行改回 `['all', 'motion', 'visual', 'code']`。

## 范围外发现（都没改）

- `openwebui-cliproxy-gateway` 封面是 2:1，小卡是 950:320，裁切后底部一排标签（one docker compose / OpenAI-compatible / MIT licensed）被切掉一半。
- `Layout.astro` 里关于 favicon 改名的中文 HTML 注释会原样输出到每个页面源码，内容里有旧文件名 `zerb-favicon-*.png`。
  HTML 注释不进索引，按「只改爬虫抓得到的」判据优先级很低；若要清，把它挪进 frontmatter 注释即可（本轮 Header 的说明就是这样处理的）。

## 新增的两个工具（可复跑）

- `tools/check-home.py`：上面「校验」第一段的全部检查。改首页顺序、取卡规则、导航、标题、品牌/媒体文件名之后跑。
- `tools/shoot-pages.mjs`：无头 chromium（CDP）量横向溢出、板块高度并截图；`--resolve zosc.com=172.67.141.94` 可直接量生产站
  （生产站那一行数据就是这样测的）。文件头注释写了为什么要模拟 reduced-motion、为什么要先滚一遍、为什么要钉住 vh 高度。
