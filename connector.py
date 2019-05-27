import logging

import requests

log = logging.getLogger('__name__')


def get_status(server):
    try:
        if 'username' in server and 'password' in server:
            log.debug("MADmin auth used")
            return requests.get(f'http://{server["ip"]}/get_status', auth=(server['username'], server['password'])).json()
        else:
            if 'username' in server or 'password' in server:
                log.warning("Ensure both username and password are set to use authenticated MADmin")
            log.debug("No MADmin auth used")
            return requests.get(f'http://{server["ip"]}/get_status').json()
    except requests.exceptions.Timeout:
        log.error("Connection to get_status timed-out")
    except requests.exceptions.RequestException as e:
        log.error(str(e))
    except Exception as e:
        log.error("General error {0}".format(e))
