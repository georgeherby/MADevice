import configargparse


def get_args():
    parser = configargparse.ArgParser(default_config_files=["config.ini"])

    parser.add_argument('-dt', '--discord_token', required=True, type=str,
                        help='Enter token for discord')

    parser.add_argument('-dba', '--duration_before_alert', required=False, default=20, type=int,
                        help='Enter the number of minutes a device can go before an alert is triggered  (Default: 20)')

    parser.add_argument('-dbc', '--delay_between_checks', required=False, default=20, type=int,
                        help='Enter time you want to wait before rechecking status (Default: 20)')

    parser.add_argument('-ttc', '--trim_table_content', required=False, default=False, type=bool,
                        help='Enable to trim the contents of !status (helps with mobile view)')

    verbose = parser.add_mutually_exclusive_group()
    verbose.add_argument('-v',
                         help='Show debug messages',
                         action='count', default=0, dest='verbose')
    verbose.add_argument('--verbosity',
                         help='Show debug messages',
                         type=int, dest='verbose')

    return parser.parse_args()
