import json
import logging

import requests

requests.packages.urllib3.disable_warnings()

log = logging.getLogger('__name__')


def get_status(server):
    try:
        if 'username' in server and 'password' in server:
            if server["ip"].startswith("https://"):
                log.debug("MADmin auth + HTTPS used")
                return requests.get(f'{server["ip"]}/get_status', auth=(server['username'], server['password']), verify=False).json()
            else:
                log.debug("MADmin auth + HTTP used")
                return requests.get(f'{server["ip"]}/get_status', auth=(server['username'], server['password'])).json()
        else:
            if 'username' in server or 'password' in server:
                log.warning("Ensure both username and password are set to use authenticated MADmin")
            if server["ip"].startswith("https://"):
                log.debug("No MADmin auth + HTTPS used")
                return requests.get(f'{server["ip"]}/get_status', verify=False).json()
            else:
                log.debug("No MADmin auth used")
                return requests.get(f'{server["ip"]}/get_status').json()
    except requests.exceptions.Timeout:
        log.error("Connection to get_status timed-out")
    except requests.exceptions.RequestException as e:
        log.info("Sending alert to Discord as server is not available")

        if 'alert_role_id' in server:
            description = f"<@{server['alert_role_id']}> Server {server['name']} is not available"
        elif 'alert_user_id' in server:
            description = f"<@{server['alert_user_id']}> Server {server['name']} is not available"
        else:
            description = f"Server {server['name']} is not available"

        discord_post_data = {
            "username": "MAD Alert",
            "avatar_url": "https://www.iconsdb.com/icons/preview/red/exclamation-xxl.png",
            "embeds": [{
                "title": f"Server unavailable",
                "color": 16711680,
                "description": description,
            }]
        }
        response = requests.post(
            server['webhook'], data=json.dumps(discord_post_data),
            headers={'Content-Type': 'application/json'}
        )
        log.debug(response)
        log.error(str(e))
    except Exception as e:
        log.error("General error {0}".format(e))
