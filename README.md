# 拼豆时光公开站点

静态官网、支持中心和隐私政策。给 App Store 审核与用户查阅使用。没有后端、表单、cookie、分析和广告。字体已自托管。

生产主机：GitHub Pages

`https://weizhichao1027-collab.github.io/beadtime-site/`

公开仓库：`weizhichao1027-collab/beadtime-site`（本目录为源码）。

应用 **1.1.2（Build 8）已正式上架**，2026-10-30 08:33（Asia/Shanghai）只读核对 App Store Connect 为 `READY_FOR_SALE`。支持 iPhone 和 iPad，最低 iOS / iPadOS 17。商店链接使用 Apple ID `6799906107`。

## 本地预览

```bash
cd website
python3 -m http.server 4173
```

- 简体官网：http://127.0.0.1:4173/
- 简体支持：http://127.0.0.1:4173/support/
- 简体隐私：http://127.0.0.1:4173/privacy/
- 英文官网：http://127.0.0.1:4173/en/home/
- 英文支持：http://127.0.0.1:4173/en/
- 英文隐私：http://127.0.0.1:4173/en/privacy/
- 404：http://127.0.0.1:4173/404.html

## 信息架构

App Store 已填写的地址保持可用，并补上 13 语完整页面。

| 页面 | 简体中文 | 其他语言 |
| --- | --- | --- |
| 营销官网 | `/` | `/{locale}/home/` |
| 技术支持 | `/support/` | `/{locale}/` |
| 隐私政策 | `/privacy/` | `/{locale}/privacy/` |

语言：`zh-Hans` `en` `zh-Hant` `ja` `ko` `de` `fr` `es` `it` `pt-BR` `ru` `ar` `hi`。

旧的 `/?lang=en`、`/support/?lang=en` 仍会跳到对应英文页。网站不再用 `localStorage` 切换文案；语言由地址决定。

## 重新生成页面

正文在 `scripts/copy_*.py`。改完后在本目录执行：

```bash
python3 scripts/build.py
python3 scripts/check.py
```

会重写各语言 HTML，以及 `sitemap.xml`、`robots.txt`、`llms.txt`、`llms-full.txt`、`humans.txt`、`.well-known/security.txt`。

## SEO 与 GEO

- 正文写在 HTML 里，不依赖脚本注入。
- 每页有绝对地址 canonical、hreflang、sitemap、llms.txt、Open Graph、Twitter Card、JSON-LD。
- 支持页带与可见内容一致的 `FAQPage`（每语 18 问）和带步骤锚点的 `HowTo`，内页有 `BreadcrumbList`。App 实体版本来自 `config.APP_VERSION`，机构与网站使用稳定 `@id`。
- `llms.txt` 提供实体、版本与引用索引，`llms-full.txt` 同源生成 13 语言完整 FAQ 和政策章节，附 canonical 锚点。
- `robots.txt` 允许主流搜索与助手爬虫。
- 分享图 `assets/img/og.png` 是无字实拍，避免各语言错字。
- 39 个 canonical 页构成 13 语×3 类页面；两个历史简体别名使用 canonical + `noindex,follow`，不进入 sitemap。404 为 `noindex`。
- JSON-LD 使用逐块 SHA-256 CSP 授权，普通脚本仍仅允许本站来源。正文与链接无需 JavaScript 即可读取。
- 6 张真实应用截图来自中英文 iPhone / iPad 现有抓图，压缩为 WebP，每张约 37–55 KB，来源记录在主仓库 `QA/Website-2026-10-30/screenshot-sources.json`。其他语言明确说明截图为中英文示例。

这些是可抓取、可理解和可引用的基础优化，不承诺收录、排名或 AI 引用。FAQ / HowTo 标记不代表搜索结果会出现富摘要；`llms.txt` 是补充引用文件，不是 Google 排名要求。依据：[Google AI 搜索说明](https://developers.google.com/search/docs/appearance/ai-features)、[Google 生成式 AI 优化指南](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)。

## 校验与发布

```bash
# 在 website/ 下执行；--base-url 可验证本地服务器或生产站全部路由和资源的字节一致性
python3 scripts/check.py --base-url http://127.0.0.1:4173
python3 scripts/check.py --base-url https://weizhichao1027-collab.github.io/beadtime-site/
```

生成器使用 Python 标准库，无 npm 构建依赖。先改文案源和 `config.py`，生成并校验，再将本目录内容同步到独立公开仓库 `beadtime-site` 的 `main` 根目录。保留 `.nojekyll` 与 `.well-known/`，排除 `__pycache__`、本地浏览器产物和私有项目文件。GitHub Pages 当前从 `main` 的 `/` 发布，`_redirects` 在该主机不生效，旧地址由生成的 HTML 与 `site.js` 保持兼容。

发布后检查 Pages build 成功、39 页与资源 SHA-256 回读一致、随机不存在地址 HTTP 404、中英文旧 URL 与 `?lang=`、手机菜单及 RTL。回滚使用站点仓库 `git revert` 恢复上个已验证版本后推送；主 App 仓库内源码也应同步回滚，避免下次构建覆盖。

Search Console / Bing Webmaster 的所有权验证和 sitemap 提交需使用对应站长账号；本轮不伪造验证标记或已收录结果。之后通过真实搜索表现观察优化效果。

## 公开地址

| 用途 | URL |
| --- | --- |
| 官网 | https://weizhichao1027-collab.github.io/beadtime-site/ |
| 支持中心 | https://weizhichao1027-collab.github.io/beadtime-site/support/ |
| 隐私政策 | https://weizhichao1027-collab.github.io/beadtime-site/privacy/ |
| 英文官网 | https://weizhichao1027-collab.github.io/beadtime-site/en/home/ |
| 英文支持 | https://weizhichao1027-collab.github.io/beadtime-site/en/ |
| 英文隐私 | https://weizhichao1027-collab.github.io/beadtime-site/en/privacy/ |
| 引用说明 | https://weizhichao1027-collab.github.io/beadtime-site/llms.txt |

## App Store Connect

- 营销 URL：官网
- 简体支持 URL：`/support/`
- 简体隐私 URL：`/privacy/`
- 英文支持 URL：`/en`
- 英文隐私 URL：`/en/privacy`
- 支持邮箱：`281916057@qq.com`
- 版权：2026 Shanghai Qishan Cultural Communication Co., Ltd.

## 隐私口径

App 不向开发者自动收集数据，照片、相机和文件导入均在本机处理，无账号、广告、分析 SDK、内购或 App 自带云同步。UserDefaults 还保存生成参数与包装数量；系统备份可能按用户设置包含 App 数据（含 iCloud）。旧临时分享文件在后续导出操作时清理，不承诺后台定时删除。网站未添加 cookie、分析或广告；GitHub Pages 为托管和安全处理 IP 等请求数据。用户主动发邮件时邮箱会收到地址、正文和附件。最近更新日期：2026-10-30。已上架 App 内法律文本仍需在下个二进制版本同步这些细化说明，参见主仓库交接文档。
