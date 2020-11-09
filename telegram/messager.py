# -*- coding: utf-8 -*-
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import SessionPasswordNeededError
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, MessageMediaDocument, DocumentAttributeAudio, MessageMediaWebPage
from telethon import utils
import csv
import copy
import datetime
from pytz import timezone

class BotClient:
    @staticmethod
    def is_number(n):
        try:
            int(n)
        except ValueError:
            return False
        except TypeError:
            return False
        return True

    def __init__(self):
        self.api_id = 941748
        self.api_hash = '03398ae66b58de459de3ed8a67adea40'
        self.phone = '+13126004866'
        self.client = TelegramClient(self.phone, self.api_id, self.api_hash)
        self.available_groups = {}
        self.available_entities = {
            "John Tao":249230371,
            "Micah Liu":148025347,
            "Jie Liu":282608054,
            "Zhi Fu": 171189988,
            "Quanquan Xu": 821608836,
            "Kyoungsik Mun":530989334
        }
    async def connect(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone)
            try:
                await self.client.sign_in(self.phone, input('Enter the code: '))
            except SessionPasswordNeededError:
                await self.client.sign_in(password=input('Password: '))
        self.available_groups = await self.retrieve_group_chat_list()

    async def retrieve_group_chat_list(self):
        chats = []
        last_date = None
        chunk_size = 2000
        groups = {}
        result = await self.client(GetDialogsRequest(
            offset_date=last_date,
            offset_id=-0,
            offset_peer=InputPeerEmpty(),
            limit=chunk_size,
            hash=0
        ))
        chats.extend(result.chats)
        for chat in chats:
            try:
                groups[chat.id] = chat.title
            except Exception as e:
                print(e)
                continue
        return groups

    async def print_groups_info(self, group_name=None, save_file=True):
        chats = []
        titles = []
        last_date = None
        chunk_size = 2000
        groups = []
        result = await self.client(GetDialogsRequest(
            offset_date=last_date,
            offset_id=-0,
            offset_peer=InputPeerEmpty(),
            limit=chunk_size,
            hash=0
        ))
        chats.extend(result.chats)
        for chat in chats:
            try:
                # print(chat.title)
                # if chat.megagroup:
                groups.append(chat)
                titles.append(chat.title)
            except Exception as e:
                print(e)
                continue
        # groups = list(set(groups))
        if not group_name:
            print('Choose a group to scrape members from:')
            i = 0
            for g in groups:
                print(str(i) + '- ' + g.title + '-' + str(g.id))
                i += 1
            g_index = input("Enter a Number: ")
            target_group = groups[int(g_index)]

        else:
            try:
                g_index = titles.index(group_name)
            except Exception as e:
                print(str(e))
                target_group = None
            else:
                target_group = groups[g_index]
        if target_group:
            # print('Fetching Members...')
            all_participants = await self.client.get_participants(target_group, aggressive=True)
            all_participants_ids = {}
            all_participants_info = []
            for user in all_participants:
                if user.username:
                    username = user.username
                else:
                    username = ""
                if user.first_name:
                    first_name = user.first_name
                else:
                    first_name = ""
                if user.last_name:
                    last_name = user.last_name
                else:
                    last_name = ""
                name = (first_name + ' ' + last_name).strip()
                all_participants_ids["{}".format(name)] = user.id
                participant_info = [name, user.id, user.access_hash, username, target_group.title, target_group.id]
                all_participants_info.append(participant_info)
            if save_file:
                print('Saving In file...')
                with open("{}-members.csv".format(target_group.title.replace("/", "-")), "w",
                          encoding='UTF-8') as f:
                    writer = csv.writer(f, delimiter=",", lineterminator="\n")
                    writer.writerow(['Name', 'UserId', 'AccessHash', 'UserName', 'group', 'group id'])
                    for participant_info in all_participants_info:
                        writer.writerow(participant_info)
                print('Members scraped successfully.')
            return all_participants_ids
        else:
            raise TypeError("Please check your group name")

    async def retrieve_members_in_group(self, group):
        if self.is_number(group):
            group = await self.get_input_entity(group)
        all_participants = await self.client.get_participants(group, aggressive=True)
        all_participants_ids = []
        for user in all_participants:
            if user.id != self.client_id:
                all_participants_ids.append(user.id)
        return all_participants_ids

    async def send_late_remind_message(self,results):
        late_compensate_table ={
            "T < 30 min": "1 hour",
            "30 min <= T <= 60 min": "2 hours",
            "60 min < T <= 90 min": "3 hours",
            "T > 90min": "4 hours"
        }
        deal_link = "https://forms.gle/yx5h26MTmbEYvuVPA"
        for result in results:
            deal_code = result[0]
            entity_name = result[1]
            late_info = result[2]
            requsted_info = result[3]
            entity_id = self.available_entities.get(entity_name)
            if entity_id:
                entity = await self.client.get_input_entity(entity_id)
                person = '<b>Dear {} :</b>'.format(entity_name)
                introduction_info = "<b>Today you are late.</b> <i>Here is the be-late recording info: " + '<b> {} </b>. '.format(late_info)
                punishment_info = 'In principle, you need to compensate for <b>{}</b> after 6:30pm today</i>. '.format(late_compensate_table.get(late_info))
                if requsted_info:
                    requsted_info = "But the supervisor hope that you can start to work from {} to compensate for it !".format(requsted_info)
                deal_link_info = "\n<i>After you complete your be-late deal, please don't forget submit your deal info. Your deal code is <b>{}</b>, and here is Attendance Deal Record Form link </i>: \n{}".format(deal_code,deal_link)
                end_info = "<b>Have a good day!</b>"
                message = person + "\n\n" + introduction_info + punishment_info + requsted_info + "\n" + deal_link_info + "\n\n" + end_info
                #print(message)
                await self.client.send_message(entity, message, parse_mode='html')
