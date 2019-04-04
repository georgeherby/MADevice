import asyncio
import json
import logging
from datetime import timezone

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
        log.info(f"Logged in as {self.user.name} {self.user.id}")

    async def on_message(self, message):
        if message.content.startswith('!status'):
            with open('servers.json') as f:
                data = json.load(f)
                for server in data:
                    if message.channel.id == int(server['status_channel_id']):
                        log.info(f"Status request received for {server['name']}")
                        r = requests.get(f'http://{server["ip"]}/get_status').json()
                        header = ['Origin', 'Route', 'Pos', 'Last Data']
                        data = []
                        for device in r:
                            try:
                                dt = parser.parse(device['lastProtoDateTime']).replace(tzinfo=timezone.utc).astimezone(tz=None)
                                last_proto_time = dt.strftime("%H:%M")
                            except ValueError:
                                last_proto_time = 'Unknown'
                            except Exception:
                                last_proto_time = 'Unknown'

                            data.append([device['origin'],
                                         device['routemanager'],
                                         f"{device['routePos']}/{device['routeMax']}",
                                         last_proto_time
                                         ])
                        log.debug(f"Sending status table for {server['name']}")
                        await message.channel.send(f"__**{server['name']}**__\n```{tabulate(data, headers=header)} ```")


def run():
    asyncio.set_event_loop(asyncio.new_event_loop())
    client = MyClient()
    client.run(args.discord_token)
