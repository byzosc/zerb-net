# TODO.md

## 当前目标

- 线上站 = `zosc.com`（Astro / Vercel / Cloudflare 橙云）。`zerb.net` 已是**纯 301 转发域名**，
  至少再续一年（301 必须持续有效，GSC 地址更改要靠它）。
- **SEO 主线：拿下裸词 `zosc` 的搜索结果。** 现状有利——该词没有任何竞争实体，
  占着首页的只是几个 Open Sound Control 技术文档页（GitHub 小库、Ubuntu manpage）和一个大学课程代码
  `ZOSC 312`，**没有知识图谱实体**。这和 `zerb` 被一位巴西 DJ 占着是完全不同的局面。
  可达目标：**第一名 + 知识面板 + 首页 3–5 个位置**；拿不到的是 ubuntu.com / github.com 上那些页面，
  它们域名权重太高，会在第一页待很多年——**但不影响首屏全是你**。
- 内容：12 个项目详情页正文已补齐；`zosc.com` 后续计划改造成**导航页**，索引到各个作品
  （motionrules、MotionPilot、makerlion 等），不再只是个人简介页。

## 2026-10-06 迁移已完成；邮件投递复核见 2026-10-07 待办

```
GSC 地址更改             2026-10-06 已提交（zerb.net → zosc.com），约 180 天迁移窗口
zosc.com/                200  title "zosc — Motion · Visual · Code"  canonical=zosc.com
zerb.net/*               301 → zosc.com/*  逐页保留路径
sitemap-index.xml        200  application/xml  15 个 URL 全新域名
favicon svg/ico/png      200  已换成 Z 标
hi@zosc.com + catch-all  → zcbgood@gmail.com（10-07 实际投递成功，但测试信进入垃圾邮件；DKIM 待补）
blog.zosc.com            HTTPS 200，证书 approved，Enforce HTTPS 已开
GitHub                   byzosc；profile README 仓库已改名为 byzosc
```

详细做法、七个踩过的坑、受保护不可替换的字符串清单，见 `docs/DONE.md` 2026-10-06 条目。

## v2 改版（2026-10-08 用户拍板，本节是各子任务的唯一事实源）

**定位：首页偏产品，节奏不变。** 骨架保持 Hero → 三板块（featured 优先网格）→ AI Ask，
只改顺序与内容；长度不变，页面数量变多（内容量加在详情页，不加在首页）。

### 已定决策（含理由）
| 决策 | 内容 | 理由 |
|---|---|---|
| 板块顺序 | **Code · Motion · Visual**，板块名不改 | 差异化在 Code（把动效体系落成工具链、上架 Adobe 商店）；改名=再一次抓取周期，只改顺序 |
| 标题 | `zosc — Code · Motion · Visual`，随 v2 一起推 | 与顺序一致，一次抓取 |
| Code 首页卡 | 固定 3–4 张 featured：MotionPilot · motionrules · Findly · +1 | 首页不变长；其余产品只在 /works 与详情页 |
| 产品上架 | MotionPilot / motionrules / Findly / QuantMind / quant-buddy-skills / openwebui-cliproxy-gateway / windows-never-sleep / nas-monitoring / zero-build-blog / s25edge-usa | 每页独立 title/description + `SoftwareApplication` schema，是裸词 zosc 的燃料 |
| 暂不上 | 第二个 app（游戏，未发布） | 用户定 |
| about 页 | **压缩不删**：约 120–180 词一段话 + 技能一行 + 认证一行 + 联系方式。拿掉逐条职责 bullet 与起止年份（2015/2019/2023） | 雇主名是实体锚点，短语级上下文保留；年份是暴露感主因且对 SEO 无用 |
| 备份 | **改 about 之前**先快照到私有仓库 `zosc-career/docs/ABOUT_PUBLIC_SNAPSHOT_2026-10-08.html` + Markdown 并入 RESUME 素材 | 详细履历的正确归宿是 PDF 简历，不是公开站 |
| AI 问答 | **不保留长版**：`knowledge.ts` 继续读页面短版，不加环境变量 | 压缩的动机是暴露感，AI 一问就背等于只防 Google 没防人；AI 职责是引到作品与联系方式，细节走邮件要 PDF；一份事实源零额外管线（用户 2026-10-08 定） |
| 对外邮箱 | **统一 `hi@zosc.com`**（Footer / about / knowledge.ts CONTACT / chat.ts 文案 / AskAI） | 品牌域名、实体一致、Gmail 不露；zcbgood 只是转发目的地 |
| 现任雇主 | **继续不出现在任何公开文本**（现状 0 次，v2 必须保持） | 隐私 + 求职中 |
| Findly → **Cubby** | 可公开关联，素材向 Findly 会话索取。**公开名 Cubby（英）/ 知物（中），Findly 只是内部代号**；App Store 线上为 1.0「Cubby — where did I put it」，改名版未放出，**页面不写死商店标题/版本** | 用户 2026-10-08 确认；Findly 会话 10-08 补充；注意这是不可逆的公开关联 |
| 测试方式 | 分支 `v2` + Vercel 预览部署（预览默认 `X-Robots-Tag: noindex`，第一次预览实测确认） | 不碰 main，不在生产站塞测试路由；定稿合并一次 |

### 硬约束（所有子任务）
- 不碰 `main`；不删任何媒体；改引用后必须跑「引用的文件是否真实存在」校验（10-06 favicon 全 404 的坑）
- 受保护字符串：`com.zerblion.motionpilot.cep`、`zerbnet-media`、`zerb-cc-cd`（slug，另议）
- 改 `app/` 前必读 `AGENTS.md`「Astro 重建版工作规则」（View Transitions / 遮罩 / Lenis / 无 Google Fonts）
- 无头 chromium 是 snap：读不到 `/tmp` 与隐藏目录，渲染/截图一律从 `~/render-tmp/` 起，用完即删

### v2 当前状态（2026-10-08 12:xx SGT，额度耗尽前落盘）
```
分支 origin/v2 = 5a8afd9   A（内容与隐私）+ B（产品库 8 页）+ C（首页 Code 优先/标题/logo/about 分段）已全部合并
预览            Vercel 对 v2 自动部署，x-robots-tag: noindex 已实测；但受 Deployment Protection 保护，打开需登录 Vercel
博客            blog.zosc.com 标题已改 zosc blog（D 子任务，zero-build-blog@cb8c754，线上实测 zerb 命中 0）
main            未动。合并 v2 → main 由用户看过预览后决定
报告            docs/v2/A-REPORT.md · B-REPORT.md · C-REPORT.md（校验输出都在里面）；截图 .render-tmp/v2-c/
```
**合并前必须做**：MotionPilot 首页大卡封面裁切——横幅自带字标，手机 3:2 下被切成「nPilot.」，桌面标题压在「Adobe Exchange ↗」上。
修法：给 motionpilot 条目加 `coverLarge`（schema 已有字段），构图中间与左下不放字。

**十项已按主会话建议拍板（用户 2026-10-08「按你的建议来」），子任务 E 执行中：**
```
1 预览：用户登录 Vercel 看        2 App Store 按钮保留       3 s25edge 的 China Mobile 保留
4 motionrules 标免费              5 MotionSheet 外链改 motionrules.com/app + 封面重做
6 Hero 三行改 Code/Motion/Visual（只换文字，动效按行位绑定不动）
7 Code 板块 3 张（gateway 不 featured，仍在 /works）
8 QuantMind / quant-buddy-skills 不上（fork、0 提交）
9 博客「Zerb Hub」历史叙述与 README 旧截图保留      10 about 三段保留
+ MotionPilot 大卡 coverLarge（合并前必修）· Back to work 按板块跳 · favicon 注释挪 frontmatter · README 顺序
```

**C 顺手改的（不要可一行回退）**：/works 筛选顺序 All·Code·Motion·Visual；.gitignore 加 .render-tmp/；og:image 位图封面产品页各用自己的。
**小尾巴**：「← Back to work」所有项目都跳 /#visual，可改成按板块跳（一行）；Layout 里 favicon 改名的 HTML 注释会输出到页面，含旧文件名，可挪进 frontmatter。

### 子任务拆分
- **A 内容与隐私**：备份快照 → 压缩 about → 确认 knowledge.ts 仍读短版且输出正常 → 邮箱统一
- **B 产品库**：素材采集（商店页/站点截图/GitHub og 图）→ 10 个产品条目 → 详情页模板 + SoftwareApplication → /works 可筛
- **C 首页与标题**：顺序 Code 优先 → Code 板块 featured 卡 → 标题 → 预览验收（A/B 合并后做）

## 待办

### sameAs 五条（2026-10-06 全部实测 200）
```
github.com/byzosc · x.com/byzosc · behance.net/zosc
steamcommunity.com/id/byzosc · blog.zosc.com
```
**改任何一个平台的 handle，必须同步改 `app/src/layouts/Layout.astro` 的 sameAs 和
`app/src/components/Footer.astro`——死的 sameAs 比没有更糟，会破坏 Google 的实体聚合。**

### 判据：只改爬虫抓得到的（2026-10-07 用户定）

用户原话：「所有的东西都要遵循对 SEO 有帮助这个原则。如果对 SEO 没有帮助，牵扯又大，
可以先不改。只有对 ZOSC 这个字符的 SEO 有帮助，才让这边改。」

```
会被抓 → 含旧身份就改    线上 HTML、GitHub README、title / meta / schema
抓不到 → 牵扯大就不改    内部文档、agent 规则文件、代码注释、产物水印、插件界面文案
```

据此降级为**不改**的：CEP 面板 "by ZERB LION"（要重新上架，爬虫看不到）、
provenance 水印 `MotionSheet::ZERB-LION::zerb.net`（改了新旧产物无法同规则校验）、
`keyframe_sheet/CLAUDE.md`、`AGENTS.md`、代码注释。

**非 SEO 但有影响的问题照旧要知会用户**，不自行纳入范围。

### 旧身份清扫（2026-10-07 全量扫描结果）

**已清干净**（本会话改完并推送）：zerb-net · zero-build-blog · byzosc(profile) ·
nas-monitoring · s25edge-usa · windows-never-sleep · openwebui-cliproxy-gateway。
扫描口径：各仓库全文 `zerblion|zerb lion|zerb.net`，含 README/LICENSE/徽章 URL/克隆命令/源码常量。

- [ ] **motionrules.com / MotionPilot（最大一块，简历上写出去的两个链接）**
      线上实测仍有 `zerbLion`×9 `zerb.net`×6 `ZERB LION`×4。源头：
      ```
      motion_design/legal/{privacy,terms}.html   zerblion@gmail.com — ZERB LION   ← 低风险，建议先改
      motion_design/cep/.../index.html           面板标题/关于页 "by ZERB LION"    ← 要重新打包上架
      keyframe_sheet/README.md                   "MotionSheet by ZERB LION"、© 、AGPL 署名条款
      keyframe_sheet 多处                        旧规划域名 motion.zerb.net / zerb.net/motion-sheet
      ```
      **`com.zerblion.motionpilot.cep` 绝对不能动**（Adobe CEP 标识符，与上面文件同目录）。
      这两个工程有自己的会话/AGENTS.md，改动需用户指派，避免撞车。
- [ ] `makerlion` README：`github.com/zerbLion/makerlion` 旧仓库 URL（其余 zerb.net 为描述性引用）。归 makerlion 会话。
- [x] ~~`findly-site` 隐私政策里的 zerblion@gmail.com~~ **刻意不改**：Findly 是独立品牌，
      且应用商店备案邮箱须与隐私政策一致；该邮箱仍正常收信。
- [ ] **只能用户改**：X 简介 / Behance「大标题」/ Steam 个人资料正文
- [ ] `windows-never-sleep` 已发布的 exe 内仍含 zerbLion（源码已改，待下次发版自然带上，不必专门发版）

### 需要用户操作（无 API 通道）
- [ ] ~~改 Mac DNS~~ 已撤销：zosc.com 打不开只是 NS 切换的正常传播，
      最晚 2026-10-08 16:26 SGT 自愈，无需任何操作。详见 DONE.md 2026-10-07
- [x] `hi@zosc.com` 实际转发已确认（2026-10-07）：已连接 Gmail 中找到主题「666」的测试信，
      `Delivered-To` 与 `X-Forwarded-For` 确认经 Cloudflare 投递到目标邮箱；当前标签为 `SPAM`。
- [ ] 在 Gmail 将这封测试信标记为「非垃圾邮件」，再观察后续正常邮件的归类。
- [ ] 补齐 `cf2024-1._domainkey.zosc.com` 的 Cloudflare DKIM TXT 公钥：DNS API 无此记录，
      Google / Cloudflare 公共 DNS 均返回 NXDOMAIN，测试信邮件头为 `dkim=permerror (no key for signature)`。
      其余 Gmail / Cloudflare 公共域 DKIM、SPF、DMARC、ARC 均通过；本次进垃圾邮件的具体原因待确认。
      当前 token 读取 `/email/routing/dns` 返回 403；需增加 Zone Settings Read 权限读取官方公钥，
      或从 Cloudflare Email Routing 设置页补齐。不要借用其他域名的公钥。
      用户已授权补齐公钥；本轮复查本机 token 存在且 `/user/tokens/verify` 返回 active，
      公钥端点仍 403、对应 DNS 查询仍为空。无需重复提供原 token；等待用户在原 token 上
      为 `zosc.com` 增加 `Zone → Zone Settings → Read`，保存后即可重试读取并添加 TXT。
      当前保存 token 的非密钥 ID 为 `3ec02115a4a8ce7ea27facaf967f3964`；名称待确认，
      `/user/tokens/{id}` 返回 403 / Unauthorized，不能凭用途猜名称。
      补齐后用新邮件复核 DKIM 与收件箱归类；本轮未修改 DNS 或 Gmail 标签。
- 用户本轮写的是 `hi@vosc.com`；找到的测试信实际 `To: hi@zosc.com`。
  `vosc.com` 的 NS/MX 属另一套服务，且不在当前 Cloudflare 账号中，不能当成本项目地址。

### 可做
- [ ] X `@zosc` 句柄申请可行性（2026-10-08）：官方现有 Handle Marketplace，个人需 Premium+、
      账号超过 3 个月且持续原创活动；是否可申请须登录 `https://handles.x.com` 搜索 `zosc`。
      当前未登录，`@zosc` 页面读取返回 403，是否列入市场及价格待确认；对方约 100 粉丝为用户提供信息，
      不代表可回收或可转移。不可申请时可登记兴趣；不因粉丝少、公开发帖少就推断闲置。
      商标投诉只适用于真实侵权/混淆，不是域名所有者自动取回句柄的通道。
      未提交申请、未联系对方、未购买订阅；现有 `@byzosc` 和站内 sameAs 暂不变。
      用户追问实际成功案例：找到 Suganthan Mohanadasan 的本人博客（2026-03-14），
      记录 `@Suganthanmn → @suganthan`，嵌入 2026-01-30 的宣布帖并提供
      `Transfer complete` 截图；另有 Beast Industries 获得 `@Beast` 的帖子镜像，
      含 `@XHandles` 祝贺回复。证据支持确有完成转移案例，不能推算 `@zosc` 的成功率。
      https://suganthan.com/blog/get-your-dream-handle-on-x/ 、
      https://twstalker.com/chucky/status/1983238001577566652 。
      依据：https://help.x.com/en/using-x/x-handle-marketplace 、
      https://help.x.com/en/rules-and-policies/inactive-twitter-accounts 、
      https://help.x.com/en/rules-and-policies/x-trademark-policy 。
- [ ] `zosc.com` 改造成导航页（用户方向，尚未开工）
- [ ] 子域名服务迁移：`clip` / `img` / `hub` / `drop` 仍挂在 `zerb.net` 下，
      若将来卖掉 zerb.net 必须先迁走（用户说今年慢慢做）
- [ ] 项目 `.md` 补 `year` 字段（featured 叠层不显示年份）

### 凭据（本会话已配置，存在本机）
```
~/.config/cloudflare/token   Zone·DNS·Edit + Zone·Email Routing Rules + Account·Email Routing Addresses
                             （2026-10-07 复核：规则可读且启用、收件地址 verified；
                               routing 设置及所需 DNS 端点返回 403，缺 Zone Settings 权限。
                               不能把写规则 + 加 MX/SPF 当作配置完整，DKIM 也必须检查）
~/.config/vercel/token       全账号权限；team = zerbs-projects (team_uL4RMxYBszxow0z3ELSHmi4M)
gh                           已登录 byzosc
```
Cloudflare account_id `f2f3c33a954d9e68ea2005b021c54c67`，后台直达 URL 可按
`https://dash.cloudflare.com/<account_id>/<域名>/<页面>` 拼。

## 正在处理

**Astro 重建版已上线，`app/` 是站点唯一实现**（根目录 WordPress 静态导出已于 2026-07-04 删除，git 历史可找回）：

- 线上地址：**`https://zerb.net`**（Vercel 项目 `net-website-mu.vercel.app`，Root Directory = `app`，生产分支 `main`，push main 即部署）。zerb.net 的 DNS 在 Cloudflare：橙云（已代理）+ 缓存，SSL 用 Full/Full(strict)。
- 改 `app/` 前**必读 `AGENTS.md`「Astro 重建版工作规则」**（架构 + View Transitions/遮罩/Lenis/光标/预览环境等踩坑总结）。
- 视频在 Cloudflare R2（`zerbnet-media`，公共域名 r2.dev）；图片在 `app/public/media/images`；字体自托管（Montserrat 标题 + Mulish 正文）；AI 问答 `/api/chat` 多 provider（Gemini key 在 Vercel 环境变量）。
- 站内中文已全部翻成英文（项目正文/博客/标题）。
- 首页 = Hero 三段进场（蒙版/模糊/打字）+ 三板块 featured-first 网格 + 「AI Ask」内联引导块（复用侧边栏）。

### 当前待办 / 待用户决定

- **AI 限流（可选，用户操作）**：限流器支持 Upstash Redis（REST）跨实例共享计数（`app/src/lib/ratelimit.ts`），未配置时自动回退内存版、Redis 出错时 fail-open 不影响问答。激活只差一步：在 https://upstash.com 建免费 Redis → 把 `UPSTASH_REDIS_REST_URL` / `UPSTASH_REDIS_REST_TOKEN`（或 Vercel KV 的 `KV_REST_API_URL` / `KV_REST_API_TOKEN`）加到 Vercel 环境变量并重新部署。限流本身已在生产生效（2026-06-22 实测 per-min=5、全站 cap=200），Upstash 仅为跨实例共享计数。
- **媒体高清**：Motion 的 featured（VIVO XR / GLASS）只有 950px 源图，全宽横幅略糊；想清晰需用户给 ≥1600px 高清横图。其余 featured 已用高清源（dynamic-weather 用 1920px）。
- **项目 `year` 未填**：所有 `app/src/content/projects/*.md` 都没填 `year`，featured 叠层不显示年份——要显示就补。
- **Code 板块**：目前只有 MotionSheet 一个作品，是否补内容待定。
- **可选打磨**：详情页正文（`app/src/project-bodies/*.html`）部分仍含 WordPress 导出的冗余 class/空块，可逐页清理；桌面 featured 卡片高度可再微调（现 ~3.7:1）。
- **R2 自定义域名（可选）**：r2.dev 有速率限制，可换 `media.zerb.net` + Cloudflare CDN，只需改 `.env` 的 `R2_PUBLIC_BASE` 重跑 `npm run media:manifest && npm run media:apply`。
- **国内访问再加速（可选）**：现橙云 + 缓存后国内可正常访问；要更快才需国内 CDN/备案。
- **跨项目依赖（2026-07-28 记）**：新站 `makerlion.com`（仓库 `/data/Projects/makerlion`，GitHub `zerbLion/makerlion`，部署 Vercel）**未来唯一可能从本项目移植的东西就是 AI 问答能力**——`app/src/pages/api/chat.ts` + `app/src/lib/{providers,knowledge,ratelimit}.ts` + `app/src/components/AskAI.astro`。现在不做。**大改这几个文件时顺手想一下可移植性**（尤其别把知识库逻辑和作品集内容耦合死）。makerlion 侧的评估写在该仓库 `docs/TODO.md`。

更早的历史（Astro 重构 Phase 1-5、2026-07-04 根目录清理与 SEO 修正、2026-06-08 媒体优化等）见 `docs/DONE.md`。

## 未完成事项

- SEO 双线作战计划（2026-07-04 定，目标：`zerblion` 通吃 + 长期抢下 `zerb`，两线共用同一实体/内容/外链）——**⚠️ 已被 2026-09-03 更名决定取代，下列仅存档；更名落地后按 zezr 重写**：
  - **第 0 阶段（用户）**：GSC 确认域名级资源 + sitemap 状态"成功"；GitHub/X/blog 签名统一 `ZERB (zerblion) — zerb.net`。站内技术项（schema/重定向/sitemap）2026-07-04 已完成。
  - **第 1 阶段（内容冲刺）**：12 个项目详情页正文已于 2026-07-05 全部补齐；剩余顺手项：项目 `.md` 补 `year`；blog 用 "ZERB" 锚文本链回 zerb.net；个别页可继续加深。
  - **第 2 阶段（1-3 月，外部权重，攻 zerb 的关键）**：Behance/Dribbble/ArtStation/站酷建档（名字 ZERB、链 zerb.net）；投 Awwwards/CSSDA/siteInspire；每月初看 GSC 查询报告（zerb/zerblion/zerb lion 趋势）。
  - **检查点**：2 周 → zerblion 第一、索引 ≥13 页；1-2 月 → zerb lion 第一、zerb 进第一页；3-6 月 → zerb 前三。

## 已知问题

- 详情页正文（`app/src/project-bodies/*.html`）和 `app/src/migrated/about.html` 部分仍是 WordPress 导出的长行压缩 HTML（含冗余 class），大段 patch 风险较高，改动要小步、改完浏览器验证。
- Motion featured（VIVO XR / GLASS）无 ≥1600px 高清源，全宽横幅略糊（见待办）。
- GSC 有 15 页"已发现/已抓取-尚未编入索引"，属新站正常，等消化，月度复查即可。

## 下一步

1. 先阅读 `README.md`、`AGENTS.md`（改 `app/` 必读「Astro 重建版工作规则」）、`docs/TODO.md`、`docs/DONE.md`。
2. 本地开发：

```bash
cd app
npm install   # 首次
npm run dev   # http://localhost:4321/
```

3. 检查首页、`works/`、`about/`、关键 `project/` 页面；涉及导航、滚动、hover 等动效时先对照线上原效果，再小范围改动。
4. 上线前构建验证：`cd app && npm run build`（构建内含 `patch-vercel-redirects.mjs` 重定向后处理）。
5. 媒体：图片放 `app/public/media/images/...`；视频走 R2——根目录 `npm run media:upload` 上传、`npm run media:manifest && npm run media:apply` 更新引用（需 `.env` 里的 R2 凭据）。
6. 改完 commit 并 push `main`（生产分支，push 即触发 Vercel 部署）。
7. 文档只维护 `README.md`、`AGENTS.md`、`docs/TODO.md`、`docs/DONE.md`，不要新增分散状态文件。

## 注意事项

- 删除资源前必须确认没有页面/组件引用。
- 改写媒体路径后必须用浏览器验证，不要只依赖文本扫描。
- 不要过度压缩作品集图片。
- 不要创建或使用 `MIGRATION_NOTES.md`、`TASK_STATE.md`、`CHANGELOG.md`、`WEB_STATE.md`、`WEB_LOG.md`、`WEB_TODO.md`、`WEB_DONE.md`。
- 修改业务代码前先说明计划；复杂修改不要直接大改。
- 修改已有动效前必须先对照原效果，不要新增用户没有要求的折叠、隐藏或布局位移。
