import logging
from threading import Thread
from alert import alert_thread
from bot import run

if __name__ == '__main__':

    # Get the top-level logger object
    logging.basicConfig(format='[%(threadName)16s] [%(asctime)s] [%(levelname)s] %(message)s')
    log = logging.getLogger()
    log.setLevel(logging.INFO)

    # # make it print to the console.
    # console = logging.StreamHandler()
    # log.addHandler(console)

    discord_thread = Thread(target=run(), name='Status Bot')
    alert_thread = Thread(target=alert_thread(log), name='Alert Check')

    discord_thread.start()
    alert_thread.start()
