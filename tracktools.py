import discord
import json
from pprint import pformat
from datetime import datetime as dt

MIN_COUNT = 5  # Minimum amount of messages per day for the day to count
MIN_DAYS = 2  # Minimum amount of days active in the server


def read_data():
    with open("data.json", mode="r", encoding="utf-8") as file:
        return json.load(file)


class ActivityTracker:

    def __init__(self, user: discord.Member = None):
        self.user = user
        self.user_id = str(self.user.id) if user else None

        self._json = read_data()
        self._params = self._json["params"]
        self._data = self._json["data"]

        self._min_count = self._params["daily_threshold"]
        self._min_days = self._params["activity_threshold"]

    def _set_last_active(self):
        self._data[self.user_id]["last_active"] = dt.today().strftime('%Y-%m-%d')
        self._update_data()

    def _reset_count(self):
        self._data[self.user_id]["today_count"] = 1
        self._update_data()

    def _add_count(self):
        self._data[self.user_id]["today_count"] += 1
        self._update_data()

    def _add_day(self):
        self._data[self.user_id]["days_active"] += 1
        self._update_data()

    def _update_data(self):
        with open("data.json", mode="w", encoding="utf-8") as file:
            self._json["data"] = self._data
            json.dump(self._json, file)

    def set_threshold(self, daily=None, activity=None):
        """Updates activity tracking parameters
        :param int daily: Minimum amount of messages a user must send for it to count as a day of activity
        :param int activity: Minimum amount of days of activity for the user to be considered active"""
        def update_params():
            self._min_count = self._params["daily_threshold"]
            self._min_days = self._params["activity_threshold"]
            with open("data.json", mode="w", encoding="utf-8") as file:
                self._json["params"] = self._params
                json.dump(self._json, file)

        if daily:
            self._params["daily_threshold"] = daily
        if activity:
            self._params["activity_threshold"] = activity
        update_params()

    def get_value(self, key):
        """Retrieves a value from the user's activity data
        :param str key: The key to be retrieved from the json file
        :return: Found value or None
        :raises TypeError: The user was not specified when initializing"""
        if self.user:
            try:
                return self._data[self.user_id][key]
            except KeyError:
                return None
        else:
            raise TypeError("User is undefined.")

    def get_activity(self):
        """Retrieves all user's activity data from the json file.
                :return: Search reults or None
                :raises TypeError: The user was not specified when initializing"""
        if self.user:
            try:
                return self._data[self.user_id]
            except KeyError:
                return None
        else:
            raise TypeError("User is undefined.")

    def get_params(self):
        """Retrieves threshold parameters from the json file
        :return: Search results or None"""
        try:
            return self._params
        except KeyError:
            return None

    def is_active(self):
        """Evaluates if the user has been active, i.e. Total days active exceed or equal the minimum activity threshold
        :return bool: True if user is active
        :raises TypeError: The user was not specified when initializing"""
        if self.user:
            return self.get_value("days_active") >= self._min_days
        else:
            raise TypeError("User is undefined.")

    def log_msg(self):
        """Logs new user activity. If the user doesn't exist, it creates one. Message count will increase as long as the daily message count threshold hasn't been reached, if it has, then the days active counter will increase by one
        :raises TypeError: The user was not specified when initializing"""
        if self.user:
            if self.user_id in self._data:
                if self.get_value("last_active") == dt.today().strftime('%Y-%m-%d'):
                    if self.get_value("today_count") < self._min_count:
                        self._add_count()
                    if self.get_value("today_count") == self._min_count:
                        self._add_day()
                else:
                    self._set_last_active()
                    self._reset_count()
            else:
                self._data[self.user_id] = {
                    "days_active": 0,
                    "last_active": dt.today().strftime('%Y-%m-%d'),
                    "today_count": 1,
                }
                self._update_data()
        else:
            raise TypeError("User is undefined.")
