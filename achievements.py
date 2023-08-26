import logging
from optparse import TitledHelpFormatter
import os
import pwnagotchi.plugins as plugins
import datetime
import json
import random

from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts

class Achievements(plugins.Plugin):
    __author__ = 'luca.paulmann1@gmail.com'
    __version__ = '1.0.1'
    __license__ = 'GPL3'
    __description__ = 'Collect achievements for daily challenges.'
    __defaults__ = {
        'enabled': False
    }

    def __init__(self):
        self.ready = False
        self.achievement_count = 0
        self.title = ""
        self.last_claimed = None
        self.daily_target = 5

    def on_loaded(self):
        logging.info("Achievements plugin loaded")

    def on_ui_setup(self, ui):
        title = self.get_title_based_on_achievements()
        ui.add_element('showAchievements', LabeledValue(color=BLACK, label="PWND:", value=f"{self.achievement_count}/{self.daily_target} ({title})", position=(0, 83), label_font=fonts.Medium, text_font=fonts.Medium))

    def on_ui_update(self, ui):
        if self.ready:
            title = self.get_title_based_on_achievements()
            ui.set('showAchievements', f"{self.achievement_count}/{self.daily_target} ({title})")

    def on_ready(self, agent):
        _ = agent
        self.ready = True
        data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'achievements.json')
        if os.path.exists(data_path):
            with open(data_path, 'r') as file:
                data = json.load(file)
                self.achievement_count = data['achievement_count']
                self.daily_target = data['daily_target']
                self.last_claimed = datetime.datetime.strptime(data['last_claimed'], '%Y-%m-%d').date() if 'last_claimed' in data else None
        else:
            self.save_to_json()
        self.get_title_based_on_achievements

    def update_title(self):
        titles = {
            0: "Beginner",
            5: "Novice",
            10: "Apprentice",
            20: "Journeyman",
            50: "Master"
        }
        for threshold, title in titles.items():
            if self.achievement_count >= threshold:
                self.title = title
                return title

    def get_title_based_on_achievements(self):
        title = self.update_title()
        return title

    def save_to_json(self):
        data = {
            'achievement_count': self.achievement_count,
            'last_claimed': self.last_claimed.strftime('%Y-%m-%d') if self.last_claimed else None,
            'daily_target': self.daily_target
        }
        data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'achievements.json')
        with open(data_path, 'w') as file:
            json.dump(data, file)

    def on_handshake(self, agent, filename, access_point, client_station):
        self.achievement_count += 1
        self.check_and_update_daily_target()
        self.save_to_json()

    def check_and_update_daily_target(self):
        today = datetime.date.today()
        if self.last_claimed is None or self.last_claimed < today:
            self.last_claimed = today
            self.daily_target += 2
