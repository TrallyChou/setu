import asyncio

import httpx

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.message_components import *
from astrbot.api.star import Context, Star, register


@register("setu", "FateTrial", "一个发送随机涩图的插件", "2.0.0")
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
            if len(self.setu_image) <= 9 or len(self.r18image) <= 9:
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        resp = await client.get("https://api.lolicon.app/setu/v2?r18=0")
                        resp.raise_for_status()
                        image_url = resp.json()['data'][0]['urls']['original']

                        def tmp_fun():
                            tmp = Image.fromURL(image_url)
                            self.setu_image.append(tmp)

                        await asyncio.get_running_loop().run_in_executor(None, tmp_fun)

                    async with httpx.AsyncClient(timeout=10.0) as client:
                        resp = await client.get("https://api.lolicon.app/setu/v2?r18=1")
                        resp.raise_for_status()
                        image_url = resp.json()['data'][0]['urls']['original']

                        def tmp_fun():
                            tmp = Image.fromURL(image_url)
                            self.r18image.append(tmp)
                        await asyncio.get_running_loop().run_in_executor(None, tmp_fun)


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

    @filter.command("setu")
    async def setu(self, event: AstrMessageEvent):
        if len(self.setu_image) != 0:
            chain = [
                At(qq=event.get_sender_id()),
                Plain("给你一张涩图："),
                self.setu_image.pop(0),
            ]
            yield event.chain_result(chain)
        else:
            yield event.plain_result("没有找到涩图。")

    @filter.command("taisele")
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
        **涩图插件帮助**

        **可用命令:**
        - `/setu`: 发送一张随机涩图。
        - `/taisele`: 发送一张随机R18涩图。
        - `/setu_help`: 显示此帮助信息。

        **使用方法:**
        - 直接发送 `/setu` 即可获取一张随机涩图。
        - 直接发送 `/taisele` 即可获取一张随机R18涩图。
        - 使用 `/setucd 15` 将冷却时间设置为 15 秒。

        **注意:**
        - 涩图图片大小为 small。
        - 冷却时间默认为 10 秒。
        """
        yield event.plain_result(help_text)
