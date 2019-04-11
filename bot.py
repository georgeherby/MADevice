import asyncio
import json
import logging

import discord
import requests
from dateutil import parser
from tabulate import tabulate

from run_args import get_args

args = get_args()
log = logging.getLogger('__name__')


class MyClient(discord.Client):

    def __init__(self):
        discord.Client.__init__(self)

    async def on_ready(self):
        log.info(f"Logged in. Username: {self.user.name}. User ID:{self.user.id}")

    async def on_message(self, message):
        if message.content.startswith('!status'):
            with open('servers.json') as f:
                servers_config_json = json.load(f)
                for server in servers_config_json:
                    if message.channel.id == int(server['status_channel_id']):
                        log.info(f"Status request received for {server['name']}")
                        device_status_response = requests.get(f'http://{server["ip"]}/get_status').json()
                        table_header = ['Origin', 'Route', 'Pos', 'Last Data']
                        table_contents = []
                        for device in device_status_response:
                            try:
                                datetime_from_status_json = parser.parse(device['lastProtoDateTime'])
                                formatted_device_last_proto_time = datetime_from_status_json.strftime("%H:%M")
                            except Exception:
                                formatted_device_last_proto_time = 'Unknown'

                            table_contents.append([device['origin'],
                                                   device['routemanager'],
                                                   f"{device['routePos']}/{device['routeMax']}",
                                                   formatted_device_last_proto_time
                                                   ])
                        log.debug(f"Sending status table for {server['name']}")
                        await message.channel.send(f"__**{server['name']}**__\n```{tabulate(table_contents, headers=table_header)}```")


def run():
    asyncio.set_event_loop(asyncio.new_event_loop())
    client = MyClient()
    client.run(args.discord_token)
