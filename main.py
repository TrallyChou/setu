import asyncio

import httpx

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.message_components import *
from astrbot.api.star import Context, Star, register
from astrbot.core.platform import MessageType
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent


@register("插画展示", "Trally", "色色", "0.1")
class SetuPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.semaphore = asyncio.Semaphore(10)  # 限制并发请求数量为 10
        self.setu_image = []
        self.r18image = []
        asyncio.create_task(self.fetch_setu())

    async def fetch_setu(self):
        while True:
            await asyncio.sleep(10)
            if len(self.setu_image) <= 9:
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        resp = await client.get("https://api.lolicon.app/setu/v2?r18=0")
                        resp.raise_for_status()
                        image_url = resp.json()['data'][0]['urls']['original']

                    tmp = Image.fromURL(image_url)
                    self.setu_image.append(tmp)


                except Exception as e:
                    self.context.logger.exception("Setu command error:")  # 记录异常，方便调试
            if len(self.r18image) <= 9:
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        resp = await client.get("https://api.lolicon.app/setu/v2?r18=1")
                        resp.raise_for_status()
                        image_url = resp.json()['data'][0]['urls']['original']

                        tmp = Image.fromURL(image_url)
                        self.r18image.append(tmp)




                # except httpx.HTTPStatusError as e:
                #     yield event.plain_result(f"获取涩图时发生HTTP错误: {e.response.status_code}")
                # except httpx.TimeoutException:
                #     yield event.plain_result("获取涩图超时，请稍后重试。")
                # except httpx.HTTPError as e:
                #     yield event.plain_result(f"获取涩图时发生网络错误: {e}")
                # except json.JSONDecodeError as e:
                #     yield event.plain_result(f"解析JSON时发生错误: {e}")
                except Exception as e:
                    self.context.logger.exception("Setu command error:")  # 记录异常，方便调试

    @filter.command("setu", alias=["来一张", "涩图"])
    async def setu(self, event: AstrMessageEvent, count=0):
        if len(self.setu_image) != 0:
            if count == 0:
                chain = [
                    At(qq=event.get_sender_id()),
                    Plain("给你一张涩图："),
                    self.setu_image.pop(0),
                ]
                yield event.chain_result(chain)
            else:
                nodes = []
                for nothing in range(1, count):
                    node = Node(
                        uin=730394312,
                        name="robot",
                        content=[
                            self.setu_image.pop(0)
                        ])
                    nodes.append(node)
                yield event.chain_result(nodes)

        else:
            yield event.plain_result("没有找到涩图。")

    @filter.command("setur18")
    async def taisele(self, event: AstrMessageEvent):
        if len(self.r18image) != 0:
            chain = [
                At(qq=event.get_sender_id()),
                Plain("给你一张涩图："),
                self.r18image.pop(0),
            ]
            yield event.chain_result(chain)
        else:
            yield event.plain_result("没有找到涩图。")

    @filter.command("setu_help")
    async def setu_help(self, event: AstrMessageEvent):
        help_text = """
        Everything.
        """
        yield event.plain_result(help_text)
