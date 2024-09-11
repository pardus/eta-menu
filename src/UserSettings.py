#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 14:53:13 2024

@author: fatih
"""

import json
from pathlib import Path

import gi

gi.require_version("GLib", "2.0")
from gi.repository import GLib


class UserSettings(object):
    def __init__(self):

        self.user_config_dir = Path.joinpath(Path(GLib.get_user_config_dir()), Path("eta-menu"))
        self.user_pins_file = Path.joinpath(self.user_config_dir, Path("user-pins.json"))

        if not Path.is_dir(self.user_config_dir):
            self.create_dir(self.user_config_dir)

        if not Path.is_file(self.user_pins_file):
            self.create_default_pins()

    def add_user_pinned_app(self, app_id):
        user_pins_file = open(self.user_pins_file, "r")
        user_pins = json.load(user_pins_file)

        old_pins = user_pins["apps"]
        new_pins = old_pins + [app_id]
        user_pins["apps"] = new_pins

        new_cf = open(self.user_pins_file, "w")
        new_cf.write(json.dumps(user_pins, indent=4))
        new_cf.flush()

    def remove_user_pinned_app(self, app_id):
        user_pins_file = open(self.user_pins_file, "r")
        user_pins = json.load(user_pins_file)

        if app_id in user_pins["apps"]:
            user_pins["apps"].remove(app_id)

        new_cf = open(self.user_pins_file, "w")
        new_cf.write(json.dumps(user_pins, indent=4))
        new_cf.flush()

    def get_user_pins(self):
        user_pins = []
        if Path.is_file(self.user_pins_file):
            user_pins_file = open(self.user_pins_file, "r")
            user_pins = json.load(user_pins_file)
        return user_pins

    def create_dir(self, dir_path):
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            return True
        except:
            print("{} : {}".format("mkdir error", dir_path))
            return False

    def create_default_pins(self):
        default_pins = {
            "apps": [
                "tr.org.pardus.pen.desktop",
                "tr.org.pardus.eta-cinnamon-greeter.desktop"
            ]
        }

        new_cf = open(self.user_pins_file, "w")
        new_cf.write(json.dumps(default_pins, indent=4))
        new_cf.flush()
