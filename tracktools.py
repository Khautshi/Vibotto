import json
from datetime import datetime as dt


def load_data():
    with open("data.json", mode="r", encoding="utf-8") as file:
        return json.load(file)


class BaseTracker:

    def __init__(self):
        self.today = dt.today().strftime('%Y-%m-%d')
        self._json = load_data()
        self._params = self._json["params"]
        self._data = self._json["data"]
        self.daily_thres = self._params["daily_threshold"]
        self.activity_thres = self._params["activity_threshold"]
        self.inactivity_thres = self._params["inactivity_threshold"]
        self.active_role = self._params["perms_role"]

    def _active_today(self, user_id, active):
        if active:
            self._data[user_id]["days_active"] += 1
            self._data[user_id]["days_inactive"] = 0
        else:
            self._data[user_id]["days_inactive"] += 1
        self._update_data()

    def _update_data(self):
        with open("data.json", mode="w", encoding="utf-8") as file:
            self._json["data"] = self._data
            json.dump(self._json, file)


class ServerTracker(BaseTracker):

    def __init__(self):
        super().__init__()

    def _purge_users(self, users):
        for user in users:
            del self._data[user]
        self._update_data()

    def set_params(self, daily=None, activity=None, inactivity=None, role=None):
        """Updates activity tracking parameters
        :param int daily: Minimum amount of messages a user must send for it to count as a day of activity
        :param int activity: Minimum amount of days a user must be active
        :param int inactivity: Maximum amount of days a user can be inactive
        :param str role: Active user role"""
        def update_params():
            self.daily_thres = self._params["daily_threshold"]
            self.activity_thres = self._params["activity_threshold"]
            self.inactivity_thres = self._params["inactivity_threshold"]
            with open("data.json", mode="w", encoding="utf-8") as file:
                self._json["params"] = self._params
                json.dump(self._json, file)

        if daily:
            self._params["daily_threshold"] = daily
        if activity:
            self._params["activity_threshold"] = activity
        if inactivity:
            self._params["inactivity_threshold"] = inactivity
        if role:
            self._params["perms_role"] = role
        update_params()

    def get_params(self):
        """Retrieves threshold parameters from the json file
        :return: Search results or None"""
        try:
            return json.dumps(self._params, indent=4)
        except KeyError:
            return None

    def activity_scan(self):
        inactive_users = []

        def not_enough():
            was_active = user_data["last_active"] == self.today
            low_count = user_data["today_count"] < self.daily_thres
            return (was_active and low_count) or not was_active

        for user_id, user_data in self._data.items():
            if user_data["days_inactive"] >= self.inactivity_thres:
                inactive_users.append(user_id)    # remove data, user is inactive, role must be revoked, return list of inactive users (ID)
            else:
                if not_enough():
                    self._active_today(user_id, False)
                else:
                    self._data[user_id]["today_count"] = 0
                    self._update_data()
        self._purge_users(inactive_users)
        return [int(user) for user in inactive_users]


class UserTracker(BaseTracker):

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = str(user_id)

    def _set_last_active(self):
        self._data[self.user_id]["last_active"] = dt.today().strftime('%Y-%m-%d')
        self._update_data()

    def _reset_count(self):
        self._data[self.user_id]["today_count"] = 1
        self._update_data()

    def _add_count(self):
        self._data[self.user_id]["today_count"] += 1
        self._update_data()

    def get_value(self, key):                                                   # Might remove this later
        """Retrieves a value from the user's activity data
        :param str key: The key to be retrieved from the json file
        :return: Found value or None"""
        try:
            return self._data[self.user_id][key]
        except KeyError:
            return None

    def get_activity(self):
        """Retrieves all user's activity data from the json file.
                :return: Search reults or None"""
        try:
            return json.dumps(self._data[self.user_id], indent=4)
        except KeyError:
            return None

    def is_active(self):
        """Evaluates if the user has been active, i.e. Total days active exceed or equal the minimum activity threshold
        :return bool: True if user is active"""
        return self.get_value("days_active") >= self.activity_thres

    def log_message(self):
        """Logs new user activity. If the user doesn't exist, it creates one. Message count will increase as long as the daily message count threshold hasn't been reached, if it has, then the days active counter will increase by one"""
        if self.user_id in self._data:
            if self.get_value("last_active") == self.today:
                if self.get_value("today_count") < self.daily_thres:
                    self._add_count()
                    if self.get_value("today_count") == self.daily_thres:
                        self._active_today(self.user_id, True)
            else:
                self._set_last_active()
                self._reset_count()
        else:
            self._data[self.user_id] = {
                "days_active": 0,
                "days_inactive": 0,
                "last_active": self.today,
                "today_count": 1,
            }
            self._update_data()


