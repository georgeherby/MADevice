import asyncio
import json
import logging
from datetime import datetime, timedelta

import discord
from dateutil import parser
from tabulate import tabulate

import connector
from run_args import get_args

args = get_args()
log = logging.getLogger('__name__')

iconURL = 'https://raw.githubusercontent.com/Map-A-Droid/MAD/master/madmin/static/mad_banner_trans.png'


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
                    error_found = False
                    if message.channel.id == int(server['status_channel_id']):
                        server_name = server['name']
                        table_header = ['Origin', 'Route', 'Pos', 'Time']
                        table_contents = []

                        log.info(f"Status request received for {server_name}")
                        log.debug("Calling /get_status for current status")
                        device_status_response = connector.get_status(server)

                        for device in device_status_response or []:
                            table_before = tabulate(table_contents, headers=table_header)
                            routemanager = device.get('rmname', '') if device.get('rmname',
                                                                                        'Not Defined') is not None else 'Not Defined'
                            origin = device.get('name', '') if device.get('rmname', '') is not None else ''
                            route_pos = device.get('routePos', '?') if device.get('routePos', '?') is not None else '?'
                            route_max = device.get('routeMax', '?') if device.get('routeMax', '?') is not None else '?'
                            lastProtoDateTime = device.get('lastProtoDateTime', '') if device.get('lastProtoDateTime',
                                                                                                  '') is not None else ''
                            number_front_chars = 6
                            number_end_chars = 5

                            try:
                                datetime_from_status_json = datetime.fromtimestamp(lastProtoDateTime)
                                formatted_device_last_proto_time = datetime_from_status_json.strftime("%H:%M")
                                latest_acceptable_datetime = (datetime.now() - timedelta(minutes=args.duration_before_alert))
                                log.debug(f"{origin} Last Proto Date Time: {datetime_from_status_json}")
                                log.debug(f"{origin} Last Acceptable Time: {latest_acceptable_datetime}")

                                if datetime_from_status_json < latest_acceptable_datetime:
                                    error_found = True

                            except Exception as e:
                                error_found = True
                                formatted_device_last_proto_time = 'Unkwn'

                            if args.trim_table_content:
                                if len(routemanager) > (number_front_chars + number_end_chars):
                                    routemanager = f"{routemanager[:number_front_chars]}..{routemanager[-number_end_chars:]}"
                                if len(origin) > (number_front_chars + number_end_chars):
                                    origin = f"{origin[:number_front_chars]}..{origin[-number_end_chars:]}"

                            table_contents.append([origin,
                                                   routemanager,
                                                   f"{route_pos}/{route_max}",
                                                   formatted_device_last_proto_time
                                                   ])

                            table_after = tabulate(table_contents, headers=table_header)

                            table_before_len = len(table_before)
                            table_after_len = len(table_after)

                            log.debug(f"{table_before_len} and after {table_after_len}")
                            log.debug("Error" + str(error_found))

                            color = 0xFF6E6E if error_found is True else 0x98FB98

                            if table_before_len > 2000:
                                log.error("Table before exceeds 2000 word count. How did this happened?")
                                return

                            if table_after_len > 2000:
                                log.info("Table size was greater than 2000. Commence table split.")
                                log.debug(table_before)

                                embed = discord.Embed(description='```' + table_before + '```', colour=color)
                                embed.set_thumbnail(url=iconURL)
                                embed.set_author(name=server['name'], url='', icon_url='')
                                await message.channel.send(embed=embed)

                                table_contents.clear()
                                table_contents.append([origin,
                                                       routemanager,
                                                       f"{route_pos}/{route_max}",
                                                       formatted_device_last_proto_time
                                                       ])

                        log.debug(f"Sending status table for {server_name}")
                        table_to_send = tabulate(table_contents, headers=table_header)

                        log.debug(table_to_send)

                        # TODO Status colours
                        embed = discord.Embed(description='```' + table_to_send + '```', colour=color)
                        embed.set_thumbnail(url=iconURL)
                        embed.set_author(name=server['name'], url='', icon_url='')
                        await message.channel.send(embed=embed)


def run():
    asyncio.set_event_loop(asyncio.new_event_loop())
    client = MyClient()
    client.run(args.discord_token)
