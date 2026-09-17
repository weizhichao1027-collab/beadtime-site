# 拼豆时光公开站点

静态官网、隐私政策和支持中心，给 App Store 审核与用户查阅使用。没有后端、表单、分析和广告。字体已自托管，页面不会向 Google Fonts 发请求。

生产主机：GitHub Pages

`https://weizhichao1027-collab.github.io/beadtime-site/`

公开仓库：`weizhichao1027-collab/beadtime-site`（本目录为源码）。

## 本地预览

```bash
cd website
python3 -m http.server 4173
```

- 官网：http://127.0.0.1:4173/
- 隐私政策：http://127.0.0.1:4173/privacy/
- 技术支持：http://127.0.0.1:4173/support/
- 404 页：http://127.0.0.1:4173/404.html

中英文切换保存在 `localStorage`，也可以使用 `?lang=zh-Hans` 或 `?lang=en`。

兼容路径：

- `/en` → 英文支持
- `/en/privacy` → 英文隐私
- `/ja`、`/ar` 等语言前缀 → 支持或隐私别名页

## 公开地址

| 用途 | 完整 URL |
| --- | --- |
| 官网 / 营销 | https://weizhichao1027-collab.github.io/beadtime-site/ |
| 支持中心 | https://weizhichao1027-collab.github.io/beadtime-site/support/ |
| 隐私政策 | https://weizhichao1027-collab.github.io/beadtime-site/privacy/ |
| 英文支持 | https://weizhichao1027-collab.github.io/beadtime-site/en |
| 英文隐私 | https://weizhichao1027-collab.github.io/beadtime-site/en/privacy |

## App Store Connect

- 营销 URL：官网
- 简体中文支持 URL：`/support/`
- 简体中文隐私 URL：`/privacy/`
- 英文支持 URL：`/en`
- 英文隐私 URL：`/en/privacy`
- 支持邮箱：`281916057@qq.com`
- 版权：2026 Shanghai Qishan Cultural Communication Co., Ltd.

## 隐私口径

不收集数据。照片、相机和文件导入均在本机处理。无账号、广告、分析 SDK、内购和 iCloud 同步。UserDefaults 仅保存首次引导和语言偏好。最近更新日期：2026-09-17。
