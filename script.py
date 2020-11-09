import argparse
import asyncio
from telegram.messager import BotClient
from google.google_sheet import GoogleSheetHelper

async def schedule_message(target_sheet, minutes):
    message_scheduler = BotClient()
    sheet_helper = GoogleSheetHelper()
    results = sheet_helper.query_late_members(target_sheet, minutes)
    await message_scheduler.connect()
    #await message_scheduler.print_groups_info()
    await message_scheduler.send_late_remind_message(results)

parser = argparse.ArgumentParser(description='manual to scripture schedule')
parser.add_argument('--target', type=str, default="Be-late Record")
parser.add_argument('--minutes', type=int, default=30)
args = parser.parse_args()
target_sheet = args.target
minutes = args.minutes
loop = asyncio.get_event_loop()
loop.run_until_complete(schedule_message(target_sheet, minutes))
