import logging
from threading import Thread
from alert import alert_thread
from bot import run

# Get the top-level logger object
logging.basicConfig(format='[%(threadName)16s] [%(asctime)s] [%(levelname)s] %(message)s')
log = logging.getLogger()
log.setLevel(logging.INFO)

# make it print to the console.
# console = logging.StreamHandler()
# log.addHandler(console)

alert_thread = Thread(target=alert_thread, name='ScanChecker', args=[log])
alert_thread.start()

# Start Discord Bot
run(log)

