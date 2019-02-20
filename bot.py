import json

import discord
from tabulate import tabulate
import requests
from run_args import get_args

args = get_args()


class MyClient(discord.Client):

    async def on_ready(self):
        print(f"Logged in as {self.user.name} {self.user.id}")

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


def run():
    client = MyClient()
    client.run(args.discord_token)
