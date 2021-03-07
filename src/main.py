import os
import threading
from bot import HomeBot

bot = HomeBot(os.environ.get('FB_USER'), os.environ.get('FB_PASS'))
collection = threading.Thread(name='background', target=bot.collect_whos_home)
collection.start()

bot.listen()
