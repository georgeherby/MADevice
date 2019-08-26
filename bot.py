import asyncio
import json
import logging

import discord
from dateutil import parser
from tabulate import tabulate

import connector
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
                        server_name = server['name']
                        table_header = ['Origin', 'Route', 'Pos', 'Time']
                        table_contents = []

                        log.info(f"Status request received for {server_name}")
                        log.debug("Calling /get_status for current status")
                        device_status_response = connector.get_status(server)

                        for device in device_status_response:
                            table_before = tabulate(table_contents, headers=table_header)
                            routemanager = device.get('routemanager', '')
                            origin = device.get('origin', '')
                            route_pos = device.get('route_pos', 'NaN')
                            route_max = device.get('route_max', 'NaN')

                            number_front_chars = 7
                            number_end_chars = 5

                            try:
                                datetime_from_status_json = parser.parse(device.get('lastProtoDateTime', ''))
                                formatted_device_last_proto_time = datetime_from_status_json.strftime("%H:%M")
                            except Exception:
                                formatted_device_last_proto_time = 'Unknown'

                            if args.trim_table_content:
                                if len(routemanager) > (number_front_chars + number_end_chars):
                                    routemanager = f"{routemanager[:number_front_chars]}..{routemanager[-number_end_chars:]}"
                                if len(origin) > (number_front_chars + number_end_chars):
                                    origin = f"{origin[:number_front_chars]}..{origin[-number_end_chars:]}"

                            table_contents.append([origin,
                                                   routemanager,
                                                   f"{route_pos}/{route_max}'",
                                                   formatted_device_last_proto_time
                                                   ])

                            table_after = tabulate(table_contents, headers=table_header)

                            table_before_len = len(table_before)
                            table_after_len = len(table_after)

                            log.debug(f"{table_before_len} and after {table_after_len}")

                            if table_before_len > 2000:
                                log.error("Table before exceeds 2000 word count. How did this happened?")
                                return

                            if table_after_len > 2000:
                                log.info("Table size was greater than 2000. Commence table split.")
                                log.debug(table_before)
                                await message.channel.send(
                                    f"__**{server_name}**__\n```{table_before}```")

                                table_contents.clear()
                                table_contents.append([origin,
                                                       routemanager,
                                                       f"{route_pos}/{route_max}'",
                                                       formatted_device_last_proto_time
                                                       ])

                        log.debug(f"Sending status table for {server_name}")
                        table_to_send = tabulate(table_contents, headers=table_header)
                        log.debug(table_to_send)
                        await message.channel.send(f"__**{server_name}**__\n```{table_to_send}```")


def run():
    asyncio.set_event_loop(asyncio.new_event_loop())
    client = MyClient()
    client.run(args.discord_token)
