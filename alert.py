import json
import time
from datetime import datetime, timedelta
import requests
from dateutil import parser

from run_args import get_args

args = get_args()


def alert_thread(log):
    alert_time = args.alert_recheck_time
    discord_data = {
        "username": "MAD Alert",
        "avatar_url": "https://www.iconsdb.com/icons/preview/red/exclamation-xxl.png",
        "embeds": [{
            "title": f"ERROR - No data for {alert_time} minutes!",
            "color": 16711680,
            "description": "PLACEHOLDER",
            "footer": {
                "text": "PLACEHOLDER"
            }
        }]
    }
    log.info("Starting Device Checker Script")
    while True:
        description = ""
        discord_data['embeds'][0]['description'] = description

        with open('servers.json') as f:
            data = json.load(f)
            for server in data:
                log.info(f"Starting check on {server['ip']}")
                r = requests.get(f'http://{server["ip"]}/get_status').json()

                for device in r:
                    log.info(f"Doing check for {device['origin']}")
                    log.debug(device)
                    origin = str(device['origin'])
                    if len(device['lastProtoDateTime']) > 0:

                        last_proto_date_time = parser.parse(device['lastProtoDateTime'])
                        latest_acceptable_time = datetime.now() - timedelta(minutes=alert_time)

                        log.debug(f"{last_proto_date_time}")
                        log.debug(f"{latest_acceptable_time}")

                        if last_proto_date_time < latest_acceptable_time:
                            description = description + f"{origin.capitalize()} (Last Received: {last_proto_date_time})\n"
                            log.debug(f"Current description: {description}")
                        else:
                            log.debug(f"{origin} did not breach the time threshold")
                    else:
                        description = description + f"{origin.capitalize()} (Last Received: Not known)\n"
        if len(description) > 0:
            discord_data['embeds'][0]['description'] = description
            discord_data['embeds'][0]['footer']['text'] = f"Next check will be at {datetime.now() + timedelta(minutes=20)}"

            log.debug(discord_data)
            log.info("Sending alert")
            response = requests.post(
                args.alert_channel_webhook, data=json.dumps(discord_data),
                headers={'Content-Type': 'application/json'}
            )
            log.debug(response)
            if response.status_code != 204:
                log.error(
                    'Request to Discord returned an error %s, the response is:\n%s'
                    % (response.status_code, response.text)
                )
        else:
            log.debug("There is no errors to report, doing to sleep..")

        time.sleep(60)
