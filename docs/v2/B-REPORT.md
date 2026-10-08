# v2 子任务 B「产品库」报告（2026-10-08）

分支 `worktree-agent-a6d5fbca71d480bf4`，未合并、未碰 `main`。事实源：`docs/TODO.md`「v2 改版」一节。
本文件只记 B 的结果与决定；`docs/TODO.md` / `docs/DONE.md` 由主会话汇总，本分支未改。

## 1. 条目清单（8 个上架，2 个待拍板未上架）

| slug | 标题 | featured | order | 封面（来源） | 链接按钮（第一个为强调色） |
|---|---|---|---|---|---|
| `motionpilot` | MotionPilot | ✅ | 50 | `cover.jpg` 1600×540：Adobe Exchange 商店截图 #2（Spec 面板 + 关键帧）嵌进 MotionSheet 同款横幅版式，字标用站内自托管 Montserrat 渲染 | Adobe Exchange · Demo & guide（motionrules.com/pilot） |
| `motionrules` | MotionRules | ✅ | 51 | `cover.jpg` 1584×535：motionrules.com 首页无头截图（暗色主题） | motionrules.com · Guide |
| `cubby` | Cubby | ✅ | 52 | `cover.jpg` 1600×600：Findly 会话交付的真实封面 `cover-dark-2400x900.png` 压缩；正文另用 2 张商店同款截图（600×1304） | App Store（id 链接）· Google Play · Website |
| `openwebui-cliproxy-gateway` | Self-Hosted Private AI Gateway | ✅ | 53 | `cover.png` 1280×640：仓库**自定义** og:image（与 README `social-preview.png` 逐字节相同），原样 | GitHub |
| `nas-monitoring` | nas-monitoring | — | 54 | `cover.jpg` 1340×453：README `docs/dashboard-preview.png` 的 THERMALS 段 | GitHub |
| `zero-build-blog` | zero-build-blog | — | 55 | `cover.jpg` 1600×541：blog.zosc.com 暗色无头截图，**裁在页头以下** | GitHub · Live blog |
| `windows-never-sleep` | Windows Never Sleep | — | 56 | `cover.svg`：手写，MotionSheet 同款版式，内容全取自 README | Download（Releases/latest）· GitHub |
| `s25edge-usa` | s25edge-usa | — | 57 | `cover.svg`：同上 | GitHub |

- 封面全部在 `app/public/media/images/projects/<slug>/`，单张最大 102 KB（≤ 400 KB），宽 ≤ 1600。新增媒体合计 656 KB。
- 现有 MotionSheet（`zerb-cc-cd`，order 70）一字未改，在 Code 列表里排在所有新产品之后。
- order 取 50–57：`/works` 的「All」视图开头（VIVO XR、LUNA OS…）保持不变，产品接在旧作品之后、MotionSheet 之前；
  Code 筛选里 featured 4 个在前。若 C 想让 All 视图也 Code 优先，只需把这 8 个的 order 改成负数，一行一个。
- 正文 190–296 词，英文，结构与旧正文一致（`wp-block-paragraph` / `wp-block-heading` / `wp-block-image`）。
- 没写任何下载量、用户数、star、安装量、评分；也没写会过期的版本号（AE 版本、App 版本都没写）。

## 2. 未上架：QuantMind、quant-buddy-skills —— 需用户拍板

两个都是**别人仓库的 fork，byzosc 名下零提交**（GitHub API，2026-10-08）：

| 仓库 | 上游 | `compare` 结果 | 上游贡献者 |
|---|---|---|---|
| byzosc/QuantMind | qusong0627/QuantMind（AGPL-3.0） | ahead_by **0**，behind_by 614 | qusong0627 (918)、cursoragent、guge199205-byte |
| byzosc/quant-buddy-skills | pseudo-longinus/quant-buddy-skills（MIT） | ahead_by **0**，behind_by 40 | ChuHongguang (107)、pseudo-longinus (23) |

上游提交作者邮箱与用户任何已知身份都对不上；本机 `/data/Projects` 下也没有这两个项目的本地改动。
以 `author: zosc` 的 SoftwareApplication 上架等于把别人的作品署成自己的，访客点进 GitHub 就会看到
「forked from …」和 0 提交，对作品集是减分项，所以**没有建条目**（没有草稿、没有封面）。
可选：① 不上（建议）；② 若用户确实以别的方式参与过（私有仓库、上游 PR 等），告诉我证据再按真实参与度写。

## 3. 第四个 featured：openwebui-cliproxy-gateway

QuantMind 是零提交 fork（见上），不符合「用户的产品」，候选只剩 gateway；它本身也够格：
原创仓库、MIT、README 中英双语，包含架构图、快速开始、FAQ、免责声明、CONTRIBUTING、THIRD-PARTY-NOTICES；
13 个 topics；**有自定义社交预览图**（5 个原创产品仓库里唯一一个），可直接当封面。
短板：README 截图区写着「截图待补」，真机界面截图还没有。

## 4. 数据结构与模板

**`app/src/content.config.ts`**：新字段全部可选或带默认值，现有 12 条不受影响（构建通过即证明）。
- `featured: boolean = false`（给 C 的首页 Code 板块用；本分支没动 `index.astro`）
- `kind: 'project' | 'product' = 'project'`：只有 `product` 才出按钮行和 JSON-LD
- `links: { label, url, type: store | download | site | source }[]`
- `app: { category（限 Google 支持的 22 种 app type）, os?, requirements?, free = false }`

**`app/src/pages/project/[slug].astro`**：
- 产品页在 hero 摘要下渲染按钮行（与原 `externalUrl` 按钮同款 class，只有 `transition-colors`，无位移动画，
  不会吞 click）。原 `externalUrl` 按钮代码未动，旧页面输出不变（已核对 vivo-xr / zerb-cc-cd / luna-os-ar-theme：
  无 SoftwareApplication、无按钮行、JSON-LD 仍是 2 块）。
- 按钮放在模板而不是正文 HTML：链接只在 frontmatter 写一次，同时喂按钮和 JSON-LD，避免两处不同步；
  且 `.entry-content a` 的下划线样式（无 layer）会盖过正文里的 Tailwind 按钮 class。
- 新增 CSS 只作用于 `ul/li` 与 `figure.shots`；旧正文没有一个用到（grep 验证），旧页面视觉不变。

**JSON-LD（`SoftwareApplication`）规则与理由**：
- `url` 与 Layout 输出的 canonical 用同一公式，构建产物逐页核对相等。
- `installUrl` = 第一个 `store` 链接；没有 store 也没有 download 时，取第一个 `site`/`source`（任务允许「站点」）。
  `downloadUrl` = 第一个 `download` 链接（只有 windows-never-sleep 有 Releases）。
- `offers {price "0", USD}` 只在来源**明确说免费**时加：商店页写 Free（MotionPilot、Cubby）、或 MIT 开源。
  **MotionRules 没加**：motionrules.com 全站没有任何价格表述，不替它下结论。
- `applicationCategory` 只能用 Google 列表里的值（2026-10-08 查官方文档）：没有 Productivity，
  Cubby 用 `UtilitiesApplication`（Google Play 归在 Tools）。
- `author` = `{Person, "zosc", https://zosc.com}`；`image` = 封面绝对地址。
- **不会出富结果**：Google 的 Software App 富结果要求 `aggregateRating` 或 `review`，我们没有评分，也绝不编；
  这里的价值是实体数据（站名 zosc ↔ 各产品），不是富结果。字段拼写已对照 schema.org 官方词表逐个校验（见 §6）。

## 5. 封面与素材的决定（以及为什么没照原方案做）

- **GitHub 自动 og 卡没用**：5 个原创产品仓库里 4 个的 og:image 是 GitHub 自动生成卡，图里**写死了 contributors / issues /
  stars / forks 数字**（windows-never-sleep 那张是「1 Star · 0 Forks」），违反「不写 star 数、会过期的数字」，
  而且是白底 GitHub 卡，放在暗色网格里很突兀。只有 gateway 的自定义预览图可用。
- **MotionPilot**：商店 5 张截图里 #1/#3/#5 与 motionrules.com 两张海报的面板标题栏都是「MotionPilot by ZERB LION」
  （旧品牌，CEP 面板未重新上架，TODO 已记）。只有 #2（Spec 面板）和 #4 干净。#4 直接裁成横幅大半是空的 AE 界面，
  太弱，所以封面改成「MotionSheet 同款横幅 + #2 截图」的合成图；正文配 #2 全图。
- **zero-build-blog**：README 截图和线上博客页头都还是「Zerb's Blog / Zerb's Notebook」，所以封面裁在页头以下。
- **nas-monitoring**：只取 THERMALS 段。README 图下半部分（容量 / 负载 / UPS / 风扇）在 README 里属于路线图，
  不是 API 今天提供的东西，放出来会夸大功能。
- 全流程可复跑：`python3 tools/product-covers.py`（脚本头注释记了全部来源 URL、裁切与坑：snap chromium 读不了
  `/tmp` 和点目录、motionrules 按**本地时间**切暗色所以用夜间时区渲染、博客跟随 `prefers-color-scheme`）。
  中间产物在 `~/render-tmp/`，跑完自动删除。

## 6. 校验（命令与输出，2026-10-08 最终状态）

```
$ cd app && npm run build
npm run build exit=0
  ├─ /project/motionpilot/index.html … /project/s25edge-usa/index.html（8 个新页面）
[build] Complete!          构建日志 warn/error 计数 = 0
[patch-vercel-redirects] patched 24 redirect routes

$ python3 tools/check-projects.py --dist --online        # 新增的可复用检查脚本
20 entries, 8 of kind: product
1. covers                       （20 条全部存在）
2./3. body media + internal links
   159 /media refs checked      （含旧正文里百分号编码的中文文件名）
4. external links of product entries
    200  cubby        https://apps.apple.com/app/id6804703410  -> …/us/app/cubby-where-did-i-put-it/id6804703410
    200  cubby        https://play.google.com/store/apps/details?id=com.zerblion.findly
    200  cubby        https://byzosc.github.io/findly-site/
    200  cubby        https://byzosc.github.io/findly-site/privacy.html
    200  motionpilot  https://exchange.adobe.com/apps/cc/205857
    200  motionpilot  https://motionrules.com/pilot
    200  motionrules  https://motionrules.com/
    200  motionrules  https://motionrules.com/guide
    200  nas-monitoring / openwebui-cliproxy-gateway / s25edge-usa / zero-build-blog  GitHub 仓库页
    200  windows-never-sleep  …/releases/latest -> …/releases/tag/v1.0.0
    200  windows-never-sleep  GitHub 仓库页
    200  zero-build-blog      https://blog.zosc.com/
5. built pages: SoftwareApplication JSON-LD
   ok  ×8   url == canonical；非产品页 0 个 SoftwareApplication
OK

$ python3 tools/check-projects.py --dist --schema
6. schema.org vocabulary (3256 terms): property names + domains checked
OK        （反向测试：instalUrl / prize 拼错、priceCurrency 放错类型，均被拦下）

$ xargs curl -sL -o /dev/null -w "%{http_code} {}"  < 14 个 frontmatter 链接     → 14 × 200

$ grep -rniE "zerblion|zerb lion|zerb\.net|zcbgood" app/src/content/projects app/src/project-bodies
app/src/content/projects/cubby.md:14:  - { label: "Google Play", url: "https://play.google.com/store/apps/details?id=com.zerblion.findly", type: "store" }
```

- grep 唯一命中是 Google Play 的**包名** `com.zerblion.findly`：主会话指定使用这条链接，包名上架后永久不可改，
  性质同受保护的 `com.zerblion.motionpilot.cep`。8 个正文命中 0，MotionPilot 正文无 `com.zerblion.motionpilot.cep`。
  这意味着 zosc.com 的 HTML 里会出现一次这个 href（不是可见文字）。
- `grep -o SoftwareApplication app/dist/client/project/cubby/index.html` → `SoftwareApplication`。
- sitemap 含 8 个新 URL。
- Cubby 页逐条对照 `FINDLY_FOR_ZOSC.md`「Do NOT put on the public page」7 条，构建产物检查结果：Findly 字样 0、
  商店标题 0、版本号 0、真名 0、下载/用户/评分 0、地区 0、绝对化隐私表述 0、未发布功能 0；
  隐私表述照抄安全措辞「No account, no sign-up, no ads. What you note is stored on your device.」。
  页面上唯一的邮箱来自全站 Footer / AskAI（子任务 A 的邮箱统一范围），不是 Cubby 的。
- 视觉：本地起静态服务器 + 无头 chromium 截了 `/project/cubby/`、`/project/motionpilot/`、`/works/?f=code`，
  版式正常（按钮行、并排手机截图、列表圆点、Code 网格）。动效与 hover 预览器看不到，需人工实测。

## 7. Cubby（原 Findly）素材

- ~~封面先用 MotionSheet 风格占位 SVG，待替换~~ → **已用真实素材**（Findly 会话 2026-10-08 交付，`/data/Projects/Findly/exports/zosc-site/`）。
- ~~文案待校对~~ → 按 `FINDLY_FOR_ZOSC.md` 重写：产品名 Cubby（知物），slug `cubby`，不写商店标题与版本。
- ~~商店链接找不到就先不放~~ → App Store 用 id 链接（标题改名后仍有效），Google Play、官网、隐私政策都已放。
- 以后若 Findly 会话换素材：重放 `cover-dark-2400x900.png` / `screen-2-find-grid.png` / `screen-3-rooms.png`
  到同一目录后跑 `python3 tools/product-covers.py cubby`，引用路径不用改。

## 8. 交接与待拍板

- **用户拍板**：QuantMind / quant-buddy-skills 上不上（§2，建议不上）。另有两点涉及隐私，已直接回报主会话，不写进公开仓库。
- **用户拍板**：MotionRules 若确认免费，在 `motionrules.md` 的 `app` 下加 `free: true` 即出 `offers`。
- **给子任务 C**：首页 Code 板块按 `featured: true` 取（当前 4 个：order 50–53）；`index.astro` 现在仍是「每板块前 5 个」，
  本分支没改。详情页「← Back to work」对所有项目都指向 `/#visual`（原有行为），C 可考虑按板块跳。
  产品页 `og:image` 仍是全站 logo，想用各自封面需要给 `Layout.astro` 加一个 prop（C 在改 Layout 标题，留给 C 统一做）。
- **MotionSheet（`zerb-cc-cd`）**：`externalUrl` 还是 `https://zerb.cc.cd`，现在跳到 motionrules.com 首页；
  MotionSheet 实际在 `https://motionrules.com/app`。封面 SVG 里也写着 `zerb.cc.cd ↗`。slug 受保护所以没碰内容，要不要改链接请定。

## 9. 旁支发现（不在 B 范围，未改）

- **blog.zosc.com 仍自称「Zerb's Blog」**：`zero-build-blog` 仓库 `index.html` 的 `<title>`、meta description（「Zerb 的博客」）、
  页头品牌、页脚「© Zerb」，以及 `assets/app.js` 的标题与「Zerb's Notebook」。10-07 的旧身份扫描用的是
  `zerblion|zerb lion|zerb.net`，单独的「Zerb」扫不到。blog.zosc.com 是 Person schema 的 sameAs 之一，
  标题会被抓，按「会被抓 → 含旧身份就改」应该改；README 截图 `docs/screenshot-home.png` 也是旧品牌。
- MotionPilot 在 Adobe Exchange 的 5 张截图里 3 张能看到「by ZERB LION」（即 TODO 已记的 CEP 面板文案），商店页访客可见。
