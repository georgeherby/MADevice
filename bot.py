import asyncio
import json

import discord
from tabulate import tabulate
import requests
from run_args import get_args
args = get_args()


class MyClient(discord.Client):

    def __init__(self, log):
        discord.Client.__init__(self)
        self.log = log

    async def on_ready(self):
        self.log.info(f"Logged in as {self.user.name} {self.user.id}")

    async def on_message(self, message):
        if message.content.startswith('!status') and message.channel.id == int(args.alert_channel_id):
            with open('servers.json') as f:
                data = json.load(f)
                for server in data:
                    r = requests.get(f'http://{server["ip"]}/get_status').json()
                    header = ['Origin', 'Route', 'Route Position', 'Last MITM Data']
                    data = []
                    for device in r:
                        data.append([device['origin'],
                                     device['routemanager'],
                                     f"{device['routePos']}/{device['routeMax']}",
                                     device['lastProtoDateTime']
                                     ])

                    await message.channel.send(f"__**{server['name']}**__\n```{tabulate(data, headers=header)} ```")


def run(log):
    asyncio.set_event_loop(asyncio.new_event_loop())
    client = MyClient(log)
    client.run(args.discord_token)
