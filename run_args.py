import configargparse


def get_args():
    parser = configargparse.ArgParser(default_config_files=["config.ini"])

    parser.add_argument('-dt', '--discord_token', required=True,
                        help='Enter token for discord')

    parser.add_argument('-acw', '--alert_channel_webhook', required=True,
                        help='Enter Discord webhook for alert channel')

    parser.add_argument('-art', '--alert_recheck_time', required=False, default=20,
                        help='Enter time you want to wait before rechecking status (Default: 20)')

    parser.add_argument('-aci', '--alert_channel_id', required=True,
                        help='Enter channel id (number) of the channel for posting alerts when there is a problem')

    return parser.parse_args()
