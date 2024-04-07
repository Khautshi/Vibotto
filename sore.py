import discord
import json
from datetime import datetime as dt

MIN_COUNT = 5       # Minimum amount of messages per day for the day to count
MIN_DAYS = 2        # Minimum amount of days active in the server


def read_json():
    with open("data.json", mode="r", encoding="utf-8") as file:
        return json.load(file)


class Sore:

    def __init__(self, dare: discord.Member):
        self.sore = dare
        self._id = str(self.sore.id)
        self._data = read_json()

    def is_active(self):
        return self.get_days() >= MIN_DAYS

    def set_last(self):
        self._data[self._id]["last_active"] = dt.today()
        self.update_json()

    def get_last(self):
        return self._data[self._id]["last_active"]

    def reset_count(self):
        self._data[self._id]["today_count"] = 1
        self.update_json()

    def add_count(self):
        self._data[self._id]["today_count"] += 1
        self.update_json()

    def get_count(self):
        return self._data[self._id]["today_count"]

    def add_day(self):
        self._data[self._id]["days_active"] += 1
        self.update_json()

    def get_days(self):
        return self._data[self._id]["days_active"]

    def track_msg(self):
        if self._id in self._data:
            if self.get_last() == dt.today().strftime('%Y-%m-%d'):
                if self.get_count() < MIN_COUNT:
                    self.add_count()
                if self.get_count() == MIN_COUNT:
                    self.add_day()
            else:
                self.set_last()
                self.reset_count()
        else:
            self._data[self._id] = {
                "days_active": 0,
                "last_active": dt.today().strftime('%Y-%m-%d'),
                "today_count": 1,
            }
            self.update_json()

    def update_json(self):
        with open("data.json", mode="w", encoding="utf-8") as file:
            json.dump(self._data, file)
