import json
import logging
import time
from datetime import datetime, timedelta, timezone

import requests
from dateutil.parser import parse
from dateutil.tz import tz

from run_args import get_args

args = get_args()
log = logging.getLogger('__name__')


def alert_thread():
    try:
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
            with open('servers.json') as json_file:
                all_servers_config = json.load(json_file)
                for server in all_servers_config:
                    description_initial = f"__**{server['name']}**__\n"
                    description = description_initial
                    discord_data['embeds'][0]['description'] = description_initial
                    log.info(f"Starting check on {server['ip']}")
                    r = requests.get(f'http://{server["ip"]}/get_status').json()

                    for device in r:
                        log.info(f"Doing check for {device['origin']}")
                        log.debug(device)
                        origin = str(device['origin'])
                        if len(device['lastProtoDateTime']) > 0:

                            last_proto_date_time = parse(device['lastProtoDateTime']).replace(tzinfo=timezone.utc).astimezone(tz=None)
                            latest_acceptable_time = (datetime.now() - timedelta(minutes=alert_time)).astimezone(tz=tz.tzlocal())
                            log.debug(f"Last Proto Date Time: {last_proto_date_time}")
                            log.debug(f"Last Acceptable Time: {latest_acceptable_time}")

                            if last_proto_date_time < latest_acceptable_time:
                                log.info(f"{origin} breached the time threshold")
                                description = description + \
                                              f"{origin.capitalize()} (Last Received: {last_proto_date_time.strftime('%H:%M')})\n"
                                log.debug(f"Current description: {description}")
                            else:
                                log.debug(f"{origin} did not breach the time threshold")
                        else:
                            description = description + f"{origin.capitalize()} (Last Received: Not known)\n"

                    if len(description) > len(description_initial):
                        discord_data['embeds'][0]['description'] = description

                        next_check_time = (datetime.now() + timedelta(minutes=args.alert_recheck_time)).strftime('%H:%M')

                        discord_data['embeds'][0]['footer']['text'] = f"Next check will be at {next_check_time}"

                        log.debug(discord_data)
                        log.info("Sending alert for device check issue")
                        response = requests.post(
                            server['webhook'], data=json.dumps(discord_data),
                            headers={'Content-Type': 'application/json'}
                        )
                        log.debug(response)
                        if response.status_code != 204:
                            log.error(
                                'Post to Discord webhook returned an error %s, the response is:\n%s'
                                % (response.status_code, response.text)
                            )
                        else:
                            log.debug("Message posted to Discord with success")
                    else:
                        log.debug("There is no errors to report, going to sleep..")

            log.info("All device checks completed, going to sleep!")
            time.sleep(60 * alert_time)
    except Exception as ex:
        log.error('Issues in the checker tread exception was: ' + str(ex))
