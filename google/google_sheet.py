# -*- coding: utf-8 -*-
import os
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class GoogleSheetHelper:
    def __init__(self, spreadsheet='R&D Attendance Report'):
        self.sheet_headers = []
        self.current_date_index = None
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('google/config/config.json', scope)
        client = gspread.authorize(credentials)
        self.spreadsheet = client.open(spreadsheet)
    def _get_worksheet_records(self, worksheet):
        self.worksheet = self.spreadsheet.worksheet(worksheet)
        results = self.worksheet.get_all_records()
        return results
    def query_late_members(self, worksheet="Be-late Record", minutes=30):
        response = []
        results = self._get_worksheet_records(worksheet)
        last_query_time = datetime.datetime.now()-datetime.timedelta(minutes = minutes)
        #print(last_query_time)
        sample = results[0]
        self.sheet_headers = list(results[0].keys())
        for result in results:
            datetime_str = result.get("Timestamp")
            datetime_object = datetime.datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S')
            # date_str = datetime_object.strftime("%Y%m%d")
            if datetime_object > last_query_time:
                values = list(result.values())
                response.append(values)
        return response
