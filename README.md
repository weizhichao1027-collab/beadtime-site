# 拼豆时光公开站点

静态官网、支持中心和隐私政策。给 App Store 审核与用户查阅使用。没有后端、表单、cookie、分析和广告。字体已自托管。

生产主机：GitHub Pages

`https://weizhichao1027-collab.github.io/beadtime-site/`

公开仓库：`weizhichao1027-collab/beadtime-site`（本目录为源码）。

应用现已在 App Store 上架。商店链接使用 Apple ID `6799906107`。

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
```

会重写各语言 HTML，以及 `sitemap.xml`、`robots.txt`、`llms.txt`、`llms-full.txt`、`humans.txt`、`.well-known/security.txt`。

## SEO 与 GEO

- 正文写在 HTML 里，不依赖脚本注入。
- 每页有绝对地址 canonical、hreflang、sitemap、llms.txt、Open Graph、Twitter Card、JSON-LD。
- 支持页带 `FAQPage` 和 `HowTo`。
- `llms.txt` / `llms-full.txt` 给生成式引擎引用。
- `robots.txt` 允许主流搜索与助手爬虫。
- 分享图 `assets/img/og.png` 是无字实拍，避免各语言错字。

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

不收集数据。照片、相机和文件导入均在本机处理。无账号、广告、分析 SDK、内购和 iCloud 同步。UserDefaults 仅保存首次引导和语言偏好。网站不使用 cookie。最近更新日期：2026-09-18。
