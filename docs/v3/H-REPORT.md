# v3 子任务 H「站点默认分享图」报告（2026-10-08）

分支 `worktree-agent-a91d5d5cb2e83976e`，基于 `origin/main` @ `5ea1709`。未合并、未碰 `main`。
按要求**没有改** `docs/DONE.md` / `docs/TODO.md` / `README.md` / `tools/check-home.py`，也没动 favicon 声明。

## 结论

| 项 | 改前 | 改后 |
|---|---|---|
| 默认 og:image / twitter:image | `cropped-logo_high2.png`：253×83、透明底，**图上是旧名字 “ZERB”**（Z 标 + ERB 字母），不只是一个白 Z | `og-default.png`：1200×630，纯 `#050505` 不透明，24 KB |
| og:image:width / height / alt | 无 | 1200 / 630 / 一句 alt，**只在用默认图时输出**（见「做法」2） |
| 产品页 6 页 | 各自封面 | 不变（cubby / motionpilot / motionrules 等仍是自己的 cover.jpg） |
| twitter:card | summary_large_image | 不变 |
| favicon 声明 | — | 未动 |
| 方版 | 无 | `og-default-square.png` 1200×1200，43 KB。**目前没有任何页面引用它**（见下一节） |
| 旧图 `cropped-logo_high2.png` | 默认 og:image | 保留在 `public/`，构建产物里 0 处引用 |

## 先说一个和 brief 前提不一致的发现：Google 缩略图取的不是 og:image

依据是用户 10-08 的搜索截图（clip `0kzyncb5z0`），我逐像素量过：

```
缩略图外框      184×184 设备像素（= 92×92 CSS 像素，正方形，圆角）
其中图片区域    184×150，宽高比 1.227
上下灰条        各 17 px，颜色 #43444d；页面底色 #22242a
图片内部        白 Z，透明处被填成黑色
```

- 1.227 和页头 logo `zosc-logo.png`（672×546 = 1.231，白 Z、透明底）吻合；旧 og:image 是 253×83（3.05），
  而且上面是 “ZERB” 四个字母，缩出来不会是一个顶满的白 Z。首页上唯一的 Z 标 `<img>` 就是页头 logo。
  **结论：Google 取的是页头 logo，不是 og:image。**（这是按比例和形状推断的，没有 Google 侧的直接证据。）
- **灰边不是透明造成的**：灰条在图片区域**外面**，是 Google 把非正方形的图等比缩进正方形框、
  空出来的地方补的灰。透明部分它填成了黑色（所以看到"黑底"）。
- Google 文档（developers.google.com/search/docs/appearance/google-images，「Specify a preferred image」一节，10-08 抓取）：
  指定首选图的方式是 `primaryImageOfPage`、挂在主实体上的 `image`，或 `og:image`；并且明确写了
  **"Avoid using a generic image (for example, your site logo) or an image with text"**，也要避免极端宽高比。
  新图是 logo + 文字，按这条 Google 很可能照样不用它。

**这对本任务意味着：**

1. 换 og:image **确实修好了** X / Slack 等按 og:image / twitter:image 出卡的平台，
   并把旧身份 “ZERB” 从每一页的可抓取元数据里拿掉了。这部分价值不受影响。
2. 换 og:image **单独不能保证改掉 Google 缩略图**。更糟的情况：如果 Google 采用了新的 1.91:1 横图、
   又像现在这样等比缩进方框，上下灰条会**比现在更厚**（预览图第 2 格）。只有 1:1 的图在那个方框里没有灰条。

**建议（都没做，需要主会话定；都碰到别人的文件）：**

- a. 页头 logo 不再作为候选：按 Google 文档，只收录 `<img src>` 引用的图，不收录 CSS 背景图；
  改成内联 `<svg>` 应该就不在候选里（这是推断，没实测）。页头正在做 logo 重设计，要和那边协调。
- b. 给 Google 一个正方形首选图：首页加 WebPage 节点的 `primaryImageOfPage` 指向 `og-default-square.png`。
  但 `check-home.py` 第 15 项要求首页 JSON-LD **恰好**是 Organization + Person + WebSite，要先改那边。
  另外 Google 自己说别用 logo，所以 b 也可能被忽略。
- c. 首页如果有一张真正能代表作品的图（非 logo、无字），拿它当 `primaryImageOfPage` 最符合 Google 的说法。
  这是内容上的决定，归用户。

## 预览（clip）

| 内容 | clip id |
|---|---|
| `og-default.png` 1200×630 | `kwke6n5ct0` |
| `og-default-square.png` 1200×1200 | `27s92gybat` |
| 深色底合成预览（搜索缩略图 4 格 + 分享卡） | `db68z71erb` |
| 浅色底合成预览（同上） | `4t85qkq2ap` |

缩略图 4 格：①现在（页头 logo 按 Google 的方式缩入，和截图一致）②新横版若同样等比缩入
③新横版若改为居中裁方 ④新方版。深色版的灰条色用截图实测的 `#43444d`；浅色版灰条色是示意，没实测。
本地副本在 worktree 的 `.render-tmp/v3h/`（已被 gitignore，worktree 删了就没了，以 clip 为准）。

## 做法

1. **`tools/og-default.py`（新增，可重跑）**——用户规则「临时脚本一律进仓库」，而且 Hero 副标还没最终定，
   换词后要能一条命令重出图：
   ```bash
   python3 tools/og-default.py --work ~/render-tmp/og-default      # 出两张图并自检
   python3 tools/og-default.py --check                              # 只检查已提交的图
   python3 tools/og-default.py --work ~/render-tmp/og-default --preview .render-tmp/og-preview
   ```
   - 无头 Chromium 在 `<canvas>` 上画，字体用站点自托管的可变字体（base64 内嵌）：Montserrat 800 字标、
     Mulish 400 副标。字形、字距、字重和线上一致。
   - 版式：一条中轴，从上到下是 Z 标（`favicon.svg` 的路径，`#f4f3ef`，高 168）、字标 `zosc`（148 px，
     字距 -0.02em，同站点标题）、副标（24 px，mist `#a1a1aa`）。间距按**墨迹到墨迹**算（measureText 的真实墨迹框），
     不按行盒算。方版是同一张卡整体放大 5/3（Z 标 280，字标 247，副标 40 px）。
   - 唯一的橙色是字标后面那个点，几何**照搬首页 Hero 的 `.hero-dot`**：直径 0.17em、离字 0.04em、坐在基线上，
     和首页三个词后面的点是同一个东西。居中时这个点不算在内（悬挂），这样 `zosc` 四个字母正对 Z 标。
   - 副标的字号是为了让**所有墨迹都在中间 630×630 的正方形里**：万一哪个平台把横图居中裁成方形，
     一个字都不会被切（左右各余 28 px）。
   - 副标文字**直接从 `index.astro` 的 `HERO_TAGLINE` 读**，不另抄一份；写进 PNG 的 tEXt 块
     （`zosc:tagline`）。`--check` 会比对：PNG 里的副标 = 当前 HERO_TAGLINE，且 Layout 的 alt 也引用了它。
     **换了 Hero 副标而没重出图，这个检查会失败。**
   - 踩到并写进注释的坑：
     - `getContext('2d', { alpha: false })` 会让 Chromium 用 LCD 子像素抗锯齿画字，每个字的边缘带蓝/橙色边
       （第一版就是这样，放大可见）。改用默认 canvas 后是灰度抗锯齿。检查第 4 项会拦这个：除了那个点，
       全图不允许有彩色像素。
     - `document.fonts.check()` 对一个**根本不存在**的字体族也返回 true（实测：`check` = true、`load` 返回 0 个字体），
       证明不了字体加载成功。改为检查 `load()` 返回的 FontFace 对象；加载不到就报错，不会用回退字体出图。
     - snap 版 Chromium 读不了 `/tmp` 和点开头的目录（worktree 在 `.claude/` 下），所以页面和临时 profile
       放在 `--work`（家目录下）；该目录必须事先不存在，跑完删除。本次用的是 `~/render-tmp/v3h/`，已删。
     - 输出由 PIL 重新编码成纯 RGB（PNG colour type 2），**文件格式层面就没有 alpha 通道**。
   - 出图是确定性的：修好抗锯齿后同样输入跑了四次，md5 都是 `dc290aed…`（横）/ `5d21f51c…`（方）；
     每次跑完 `~/render-tmp/v3h/` 都已删除（`ls` 确认不存在）。

2. **`app/src/layouts/Layout.astro`**：默认 `ogImage` 改为 `og-default.png` 的绝对 URL；
   新增 `og:image:width` 1200 / `og:image:height` 630 / `og:image:alt`，**只在没有传 `image` 时输出**。
   原因：产品页封面是 1600×600、1584×535、1600×540，无条件输出的话，会对这些封面声明错误的 1200×630。
   `image` prop 的逻辑、产品页输出都没变。说明写在 frontmatter 注释里（不进 HTML）。
   alt：`The zosc Z mark and wordmark on black, above the tagline “Design that runs. Code that moves. Things that ship.”`

## 校验（命令输出）

```
$ npm run build --prefix app            → exit=0；构建日志里 warn/error 0 行
$ identify og-default.png og-default-square.png
  og-default.png         PNG 1200x630   8-bit sRGB 24993B
  og-default-square.png  PNG 1200x1200  8-bit sRGB 44219B
$ convert og-default.png -format "%[opaque]" info:          → true
$ convert og-default-square.png -format "%[opaque]" info:   → true
$ python3 tools/og-default.py --check                       → ALL OK，exit 0
  og-default.png         colour type 2（RGB 无 alpha）；四角都是 (5,5,5)
                         墨迹框 x 313-887, y 126-505 → 离边 左313 上126 右313 下125（要求 ≥80）
                         全部墨迹在中间方形 x 285-915 内，左右各余 28 px
                         彩色像素只有一团 26×26（那个点），其中 451 px 正好是 #e7503a
  og-default-square.png  墨迹框 x 122-1078, y 284-916 → 离边 122/284/122/284；彩色只有一团 43×42
  Layout.astro           alt 引用了当前 HERO_TAGLINE；默认 og:image 是 og-default.png
```

构建产物（`app/dist/client`，共 24 个 HTML）：

```
18 页  og:image = https://zosc.com/media/images/common/brand/og-default.png，且都带 og:image:width
       （首页、about、works、404、12 个旧项目页、2 个 SVG 封面产品页 windows-never-sleep / s25edge-usa）
 6 页  og:image = 各自封面：cubby / motionpilot / motionrules / nas-monitoring /
       openwebui-cliproxy-gateway / zero-build-blog；不带 width/height/alt
 0 页  引用 cropped-logo
首页：og:image + width 1200 + height 630 + alt；twitter:card = summary_large_image；twitter:image = 新图
cubby：og:image = twitter:image = https://zosc.com/media/images/projects/cubby/cover.jpg
dist 里的 og-default.png 与 public 里的逐字节相同（cmp）
```

### `tools/check-home.py` 会因为一个常量失败（我按要求没改它）

它第 95 行写死了 `DEFAULT_OG = f"{SITE}/media/images/common/brand/cropped-logo_high2.png"`，第 6 项拿它比对。

- 原样运行：exit 1，15 个 FAIL，**全部在第 6 项**，内容都是「拿到 og-default.png，期望 cropped-logo_high2.png」。
- 只在内存里把这一个字符串换成 `og-default.png` 再跑（磁盘上的文件没动）：**exit 0、0 个 FAIL**，
  第 1–15 项全过，包括第 5 项引用完整性（新图的绝对 URL 对应 `public/` 里的真实文件）和第 15 项 JSON-LD。

**需要这个文件的负责人改一行**：`DEFAULT_OG = f"{SITE}/media/images/common/brand/og-default.png"`
（顺便把 docstring 第 6 项的 "keep the default logo" 改成 default card）。在这之前合并的话，check-home 会是红的。

## 旧图 `cropped-logo_high2.png` 的去留

保留，没删（规则：媒体不删，外部可能有引用，比如各平台缓存的旧分享卡）。

```
$ grep -rn cropped-logo app/src tools
app/src/layouts/Layout.astro:33   注释（frontmatter，不进 HTML），说明它被替换了
tools/check-home.py:95            DEFAULT_OG 常量，见上
```

**页头不用它**：Header 用的是 `zosc-logo.png`（672×546，白 Z 透明底）——也就是 Google 实际拿去当缩略图的那张。

## 没做 / 留给主会话

- `tools/check-home.py` 第 95 行（见上）。
- 方版目前**没有被引用**，单独存在不会被任何平台发现。要不要用、怎么声明，见上面的建议 a / b / c。
- 只加了 brief 列出的 `og:image:alt`，没加 `twitter:image:alt`（X 读后者；要加只是一行）。
- Hero 副标还没最终定：一旦改了，重跑 `tools/og-default.py`，再改 Layout 里的 alt；`--check` 会盯着这两处。
- 上线后，已经被分享过的链接，各平台可能还缓存着旧卡，需要它们重新抓取；具体刷新方式我没核实，不在这里写。
