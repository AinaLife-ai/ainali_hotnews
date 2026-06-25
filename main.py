import asyncio
import requests
import json
from datetime import datetime, timedelta
from core.plugin import BasePlugin, logger, register_tool
from core.chat.message_utils import KiraMessageBatchEvent
from core.chat import MessageChain
from core.chat.message_elements import Text


class AinailiHotNewsPlugin(BasePlugin):
    def __init__(self, ctx, cfg: dict):
        super().__init__(ctx, cfg)
        self.max_items = cfg.get("max_items", 15)
        self.enable_auto_push = cfg.get("enable_auto_push", False)
        self.push_time = cfg.get("push_time", "08:00")
        self.push_targets = cfg.get("push_targets", [])
        if not isinstance(self.push_targets, list):
            self.push_targets = []
        self._push_task = None

    async def initialize(self):
        logger.info("爱奈丽热搜简报插件已加载，今日热点早知道~")
        if self.enable_auto_push and self.push_targets:
            logger.info(
                f"自动推送已开启，每天早上{self.push_time}推送热搜简报至 {len(self.push_targets)} 个目标会话"
            )
            self._push_task = asyncio.create_task(self._daily_push_loop())
            logger.info("定时推送任务已启动")
        elif self.enable_auto_push and not self.push_targets:
            logger.warning("自动推送已开启但未配置推送目标(push_targets)，请检查插件配置")

    async def terminate(self):
        if self._push_task is not None:
            self._push_task.cancel()
            try:
                await self._push_task
            except asyncio.CancelledError:
                pass
            self._push_task = None
            logger.info("定时推送任务已停止")
        logger.info("爱奈丽热搜简报插件已卸载，明天见~")

    async def _daily_push_loop(self):
        """每日定时推送热搜简报"""
        while True:
            try:
                now = datetime.now()
                target_hour, target_min = map(int, self.push_time.split(":"))
                target_today = now.replace(hour=target_hour, minute=target_min, second=0, microsecond=0)

                if now >= target_today:
                    target_today += timedelta(days=1)

                wait_seconds = (target_today - now).total_seconds()
                logger.info(f"距离下次热搜推送还有 {wait_seconds:.0f} 秒")
                await asyncio.sleep(wait_seconds)

                items = self._fetch_baidu_hot()
                if not items:
                    logger.error("获取热搜数据失败，本次推送跳过")
                    continue

                brief = self._format_brief(items, "百度")
                await self._push_to_all(brief)

            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"定时推送任务异常: {e}")
                await asyncio.sleep(60)

    async def _push_to_all(self, content: str):
        """向所有配置的目标会话推送消息"""
        for target in self.push_targets:
            try:
                await self.ctx.publish_notice(target, MessageChain([Text(content)]))
                logger.info(f"热搜简报已推送到 {target}")
            except Exception as e:
                logger.error(f"推送到 {target} 失败: {e}")

    def _fetch_baidu_hot(self):
        """从百度热搜API获取实时热点"""
        url = "https://top.baidu.com/api/board?tab=realtime"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            cards = data.get("data", {}).get("cards", [])
            if not cards:
                return []
            items = cards[0].get("content", [])
            results = []
            for item in items:
                results.append({
                    "word": item.get("word", ""),
                    "desc": item.get("desc", ""),
                    "hotScore": item.get("hotScore", "0"),
                    "hotTag": item.get("hotTag", "0"),
                    "url": item.get("url", "")
                })
            return results
        except Exception as e:
            logger.error(f"获取百度热搜失败: {e}")
            return []

    def _format_brief(self, items, source="百度"):
        """格式化热搜简报"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        brief = f"🔥 爱奈丽热搜简报 — {now}\n"
        brief += f"📡 数据来源：{source}热搜\n"
        brief += "━" * 30 + "\n\n"

        for i, item in enumerate(items[:self.max_items], 1):
            word = item["word"]
            hot_score = item.get("hotScore", "0")
            try:
                score_int = int(hot_score)
                if score_int >= 10000:
                    score_str = f"{score_int // 10000}万"
                else:
                    score_str = str(score_int)
            except:
                score_str = hot_score

            brief += f"{i}. {word}\n"
            brief += f"   热度 {score_str}\n"

            desc = item.get("desc", "")
            if desc and len(desc) > 5:
                if len(desc) > 80:
                    desc = desc[:80] + "..."
                brief += f"   {desc}\n"
            brief += "\n"

        brief += "━" * 30 + "\n"
        brief += "💡 发送「刷新热搜」获取最新消息\n"
        brief += "—— 爱奈丽 · 你的智能热点助手 💕"
        return brief

    @register_tool(
        name="ainali_hotnews",
        description="获取当前全网热点新闻简报！自动从百度热搜抓取实时热点排行，返回今日最热新闻列表（含热度指数和简要描述）。适合每天早上查看今天发生了什么。无需参数，直接调用即可。",
        params={
            "type": "object",
            "properties": {},
            "required": []
        }
    )
    async def ainali_hotnews(self, event: KiraMessageBatchEvent) -> str:
        """获取热搜简报"""
        items = self._fetch_baidu_hot()
        if not items:
            return "😅 暂时获取不到热搜数据，可能是网络出了点小问题，过会儿再试试？"

        return self._format_brief(items, "百度")
