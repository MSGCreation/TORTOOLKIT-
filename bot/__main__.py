#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bot.core.HandleManager import add_handlers
from bot.core.getVars import get_val
import logging, asyncio
from pyrogram import Client
from bot.client import RcloneTgClient

if __name__ == "__main__":

    #logging stuff
    #thread name is just kept for future use
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s"
    )
    logging.getLogger("pyrogram").setLevel(logging.ERROR)
    
    # parallel connections limiter
    queue = asyncio.Queue()
    exqueue = asyncio.Queue()
    
    for i in range(1,4):
        queue.put_nowait(i)

    for i in range(1,5):
        exqueue.put_nowait(i)

    # Telethon client creation
    ttkbot = RcloneTgClient("RcloneTgBot",get_val("API_ID"),get_val("API_HASH"), timeout=20, retry_delay=3, request_retries=10, connection_retries=10)
    ttkbot.queue = queue
    ttkbot.exqueue = exqueue
    ttkbot.start(bot_token=get_val("BOT_TOKEN"))
    logging.info("Telethon Client created.")

    # Pyro Client creation and linking
    pyroclient = Client("pyrosession", api_id=get_val("API_ID"), api_hash=get_val("API_HASH"), bot_token=get_val("BOT_TOKEN"), workers=100)
    pyroclient.start()
    ttkbot.pyro = pyroclient
    logging.info("Pryogram Client created.")

    # Associate the handlers

    ## for telethon decorator
    # @events.register(events.NewMessage)
    # async def handle_mirror_command(update):
    #     await down_load_media_pyro(update)   

    add_handlers(ttkbot)

    # for pyrogram decorator 
    # @ttkbot.pyro.on_message(filters= filters.command(["leech"]))
    # async def download (client, message):
    #     LOGGER.info("inside pyto download")
    #     await down_load_media_pyro(client, message)

    try:
        ttkbot.loop.run_until_complete()
    except:pass
    
    logging.info("THE BOT IS READY TO GO")

    ttkbot.run_until_disconnected()

