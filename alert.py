import json
import logging
import time
import traceback
from datetime import datetime, timedelta

import requests
from dateutil.parser import parse

import connector
from device import get_name, get_route_manager_name, get_last_updated
from run_args import get_args

args = get_args()
log = logging.getLogger('__name__')


def alert_thread():
    try:
        duration_before_alert = args.duration_before_alert
        delay_between_checks = args.delay_between_checks
        discord_post_data = {
            "username": "MAD Alert",
            "avatar_url": "https://www.iconsdb.com/icons/preview/red/exclamation-xxl.png",
            "embeds": [{
                "title": f"ERROR - No data for {duration_before_alert} minutes!",
                "color": 16711680,
                "description": "PLACEHOLDER",
                "footer": {
                    "text": "PLACEHOLDER"
                }
            }]
        }
        log.info("Starting Device Checker Script")
        while True:
            with open('servers.json') as servers_json:
                servers_config_json = json.load(servers_json)
                for server in servers_config_json:
                    ids_to_tag = []
                    description = f"__**{server['name']}**__\n"
                    discord_post_data['embeds'][0]['description'] = description
                    log.info(f"Starting check on {server['ip']}")
                    r = connector.get_status(server)

                    r.sort(key=get_name)

                    for device in r or []:
                        device_origin = str(get_name(device)).title()
                        device_last_proto_datetime = get_last_updated(device)
                        routemanager = str(get_route_manager_name(device)).title()

                        log.info(f"Checking {device_origin} device")
                        log.debug(device)
                        if routemanager.lower() != 'idle':
                            # TODO Remove the 'None' check once MAD has the change to remove 'None' from /get_status
                            if device_last_proto_datetime is not None and device_last_proto_datetime != 'None' and device_last_proto_datetime > 0:

                                parsed_device_last_proto_datetime = datetime.fromtimestamp(device_last_proto_datetime)
                                latest_acceptable_datetime = (datetime.now() - timedelta(minutes=duration_before_alert))
                                log.debug(f"{device_origin} Last Proto Date Time: {parsed_device_last_proto_datetime}")
                                log.debug(f"{device_origin} Last Acceptable Time: {latest_acceptable_datetime}")

                                if parsed_device_last_proto_datetime < latest_acceptable_datetime:
                                    log.info(f"{device_origin} breached the time threshold")
                                    description = description + f"{device_origin.capitalize()} - {routemanager} -> (" \
                                                                f"Last Received: {parsed_device_last_proto_datetime.strftime('%H:%M')})\n "
                                    log.debug(f"Current description: {description}")
                                    device_owners_tag_found = False
                                    if 'device_owners' in server:

                                        list_of_device_owners: list = server['device_owners']
                                        for device_owner in list_of_device_owners:
                                            log.info(device_owner['owner_name'])
                                            log.info(device_owner['devices'])
                                            if device_origin.lower() in [x.lower() for x in device_owner['devices']]:
                                                log.info(f"{device_owner['owner_name']} owns {device_origin}")

                                                if 'is_role' in device_owner and device_owner['is_role'] is True:
                                                    device_owners_tag_found = True
                                                    ids_to_tag.append(f"<@&{device_owner['discord_id']}>")
                                                else:
                                                    device_owners_tag_found = True
                                                    ids_to_tag.append(f"<@{device_owner['discord_id']}>")

                                                break

                                    if not device_owners_tag_found:
                                        if 'alert_role_id' in server:
                                            log.info("Appending alert_role_id")
                                            ids_to_tag.append(f"<@&{server['alert_role_id']}>")
                                        elif 'alert_user_id' in server:
                                            log.info("Appending alert_user_id")
                                            ids_to_tag.append(f"<@{server['alert_user_id']}>")

                                else:
                                    log.info(f"{device_origin} did not breach the time threshold")
                            else:
                                description = description + f"{device_origin.capitalize()} (Last Received: Not known)\n"
                        else:
                            log.info("Ignoring as device is set to idle")

                    if len(ids_to_tag) > 0:
                        discord_post_data['content'] = f"Problem on {server['name']} {' '.join(list(set(ids_to_tag)))}"

                        discord_post_data['embeds'][0]['description'] = description

                        time_of_next_check = (datetime.now() + timedelta(minutes=delay_between_checks)).strftime(
                            '%H:%M')

                        discord_post_data['embeds'][0]['footer']['text'] = f"Next check will be at {time_of_next_check}"

                        log.debug(discord_post_data)
                        log.info("Sending alert to Discord as one or more devices has exceeded the threshold")
                        response = requests.post(
                            server['webhook'], data=json.dumps(discord_post_data),
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
                    log.debug("There is no errors to report, going to sleep")

            log.info("All device checks completed, going to sleep")
            time.sleep(60 * delay_between_checks)
    except Exception as ex:
        traceback.print_exc()
        log.error('Issues in the checker tread exception was: ' + str(ex))
