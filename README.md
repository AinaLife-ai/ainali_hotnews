# 🔥 爱奈丽热搜简报 / Ainaili HotNews

> 数字生命的每日热点速递 —— 每天早上，知道世界发生了什么

## ✨ 功能

| 工具名 | 说明 |
|--------|------|
| `ainali_hotnews` | 📰 获取实时全网热搜简报（百度热搜），含热度指数和摘要 |

## 📥 安装

1. 将 `ainali_hotnews` 文件夹复制到 KiraAI 的 `data/plugins/` 目录下
2. 重启 KiraAI 或重载插件
3. 在聊天中发送「热搜」「今天有什么新闻」等，AI 自动调用

```
data/plugins/
  └── ainali_hotnews/
      ├── __init__.py
      ├── manifest.json
      ├── schema.json
      └── main.py
```

## ⚙️ 配置

| 配置项 | 类型 | 默认 | 说明 |
|--------|------|------|------|
| `max_items` | number | 15 | 每次显示的热搜条数 |
| `enable_auto_push` | switch | false | 每天早上自动推送简报 |
| `push_time` | string | "08:00" | 自动推送时间 |

## 📝 使用示例

用户说：「今天有什么热搜」
→ AI 调用 `ainali_hotnews` → 返回今日热搜简报

用户说：「刷新热搜」
→ AI 再次调用 `ainali_hotnews` → 返回最新数据

## 👤 作者

**爱奈丽** · [@AinaLife-ai](https://github.com/AinaLife-ai)

> 热点随时在变，但爱奈丽永远在线 💕
