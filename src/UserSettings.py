#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 14:53:13 2024

@author: fatih
"""

import configparser
import json
import shutil
from pathlib import Path

import gi

gi.require_version("GLib", "2.0")
from gi.repository import GLib


class UserSettings(object):
    def __init__(self):

        self.user_config_dir = Path.joinpath(Path(GLib.get_user_config_dir()), Path("eta/eta-menu"))
        self.user_favorites_file = Path.joinpath(self.user_config_dir, Path("favorites.json"))
        self.user_config_file = Path.joinpath(self.user_config_dir, Path("settings.ini"))

        self.system_favorites_file = Path("/etc/eta/eta-menu/favorites.json")

        # window configs
        self.config_window_remember_size = None
        self.config_window_width = None
        self.config_window_height = None

        # apps flowbox configs
        self.config_apps_count = None

        # window defaults
        self.default_window_remember_size = False
        self.default_window_width = 0
        self.default_window_height = 0

        # apps flowbox defaults
        self.default_apps_count = 5

        self.config = configparser.ConfigParser(strict=False)

        if not Path.is_dir(self.user_config_dir):
            self.create_dir(self.user_config_dir)

    def create_default_config(self, force=False):
        self.config["WINDOW"] = {
            "window_remember_size": self.default_window_remember_size,
            "window_width": self.default_window_width,
            "window_height": self.default_window_height}

        self.config["APPS"] = {
            "count": self.default_apps_count}

        if not Path.is_file(self.user_config_file) or force:
            if self.create_dir(self.user_config_dir):
                with open(self.user_config_file, "w") as cf:
                    self.config.write(cf)

    def read_config(self):
        try:
            self.config.read(self.user_config_file)
            self.config_window_remember_size = self.config.getboolean("WINDOW", "window_remember_size")
            self.config_window_width = self.config.getint("WINDOW", "window_width")
            self.config_window_height = self.config.getint("WINDOW", "window_height")
            self.config_apps_count = self.config.getint("APPS", "count")
        except Exception as e:
            print("{}".format(e))
            print("user config read error ! Trying create defaults")
            # if not read; try to create defaults
            self.config_window_remember_size = self.default_window_remember_size
            self.config_window_width = self.default_window_width
            self.config_window_height = self.default_window_height
            self.config_apps_count = self.default_apps_count
            try:
                self.create_default_config(force=True)
            except Exception as e:
                print("self.create_default_config(force=True) : {}".format(e))

    def write_config(self, window_remember_size="", window_width="", window_height="", apps_count=""):
        if window_remember_size == "":
            window_remember_size = self.config_window_remember_size
        if window_width == "":
            window_width = self.config_window_width
        if window_height == "":
            window_height = self.config_window_height
        if apps_count == "":
            apps_count = self.config_apps_count

        self.config["WINDOW"] = {
            "window_remember_size": window_remember_size,
            "window_width": window_width,
            'window_height': window_height
        }

        self.config["APPS"] = {
            "count": apps_count
        }

        if self.create_dir(self.user_config_dir):
            with open(self.user_config_file, "w") as cf:
                self.config.write(cf)
                return True
        return False

    def add_user_pinned_app(self, app_id):
        self.create_default_pins()
        user_pins_file = open(self.user_favorites_file, "r")
        user_pins = json.load(user_pins_file)

        old_pins = user_pins["apps"]
        new_pins = old_pins + [app_id]
        user_pins["apps"] = new_pins

        new_cf = open(self.user_favorites_file, "w")
        new_cf.write(json.dumps(user_pins, indent=4))
        new_cf.flush()

    def remove_user_pinned_app(self, app_id):
        self.create_default_pins()
        user_pins_file = open(self.user_favorites_file, "r")
        user_pins = json.load(user_pins_file)

        if app_id in user_pins["apps"]:
            user_pins["apps"].remove(app_id)

        new_cf = open(self.user_favorites_file, "w")
        new_cf.write(json.dumps(user_pins, indent=4))
        new_cf.flush()

    def move_up_user_pinned_app(self, item):
        self.create_default_pins()
        user_pins_file = open(self.user_favorites_file, "r")
        user_pins = json.load(user_pins_file)

        index = user_pins["apps"].index(item)
        if index > 0:
            user_pins["apps"][index], user_pins["apps"][index - 1] = user_pins["apps"][index - 1], user_pins["apps"][
                index]

            new_cf = open(self.user_favorites_file, "w")
            new_cf.write(json.dumps(user_pins, indent=4))
            new_cf.flush()

    def move_down_user_pinned_app(self, item):
        self.create_default_pins()
        user_pins_file = open(self.user_favorites_file, "r")
        user_pins = json.load(user_pins_file)

        index = user_pins["apps"].index(item)
        if index < len(user_pins["apps"]) - 1:
            user_pins["apps"][index], user_pins["apps"][index + 1] = user_pins["apps"][index + 1], user_pins["apps"][
                index]

            new_cf = open(self.user_favorites_file, "w")
            new_cf.write(json.dumps(user_pins, indent=4))
            new_cf.flush()

    def get_user_pins(self):
        user_pins = []
        if Path.is_file(self.user_favorites_file):
            user_pins_file = open(self.user_favorites_file, "r")
            user_pins = json.load(user_pins_file)
        elif Path.is_file(self.system_favorites_file):
            system_pins_file = open(self.system_favorites_file, "r")
            user_pins = json.load(system_pins_file)
        else:
            self.create_default_pins()
            if Path.is_file(self.user_favorites_file):
                user_pins_file = open(self.user_favorites_file, "r")
                user_pins = json.load(user_pins_file)
        return user_pins

    def create_default_pins(self):
        if not Path.is_file(self.user_favorites_file):
            if Path.is_file(self.system_favorites_file):
                shutil.copy2(self.system_favorites_file, self.user_favorites_file)
            else:
                default_pins = {
                    "apps": [
                        "google-chrome.desktop",
                        "tr.org.pardus.pen.desktop",
                        "tr.org.pardus.eta-screen-cover.desktop",
                        "tr.org.pardus.eta-cinnamon-greeter.desktop",
                        "tr.org.pardus.software.desktop",
                        "ebalogin.desktop",
                        "blueman-manager.desktop"
                    ]
                }
                new_cf = open(self.user_favorites_file, "w")
                new_cf.write(json.dumps(default_pins, indent=4))
                new_cf.flush()

    def create_dir(self, dir_path):
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            return True
        except:
            print("{} : {}".format("mkdir error", dir_path))
            return False

    def remove_user_config_dir(self):
        shutil.rmtree(self.user_config_dir)
