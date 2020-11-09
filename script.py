import argparse
import asyncio
from telegram.messager import BotClient
from google.google_sheet import GoogleSheetHelper

async def schedule_message(code, target_sheet, minutes, group_id=325983737):
    message_scheduler = BotClient()
    await message_scheduler.connect()
    if not code :
        sheet_helper = GoogleSheetHelper()
        results = sheet_helper.query_late_members(target_sheet, minutes)
        #await message_scheduler.print_groups_info()
        await message_scheduler.send_late_remind_message(results)
    else:
        await message_scheduler.send_buy_snack_remind_message(group_id)

parser = argparse.ArgumentParser(description='manual to scripture schedule')
parser.add_argument('--code', type=int, default=0)
parser.add_argument('--target', type=str, default="Be-late Record")
parser.add_argument('--minutes', type=int, default=30)
parser.add_argument('--group-id', type=int, default=325983737)
args = parser.parse_args()
code = args.code
target_sheet = args.target
minutes = args.minutes
group_id = args.group_id
loop = asyncio.get_event_loop()
loop.run_until_complete(schedule_message(code, target_sheet, minutes,group_id))
