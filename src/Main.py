#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 14:53:13 2024

@author: fatih
"""
import sys

import gi

from MainWindow import MainWindow

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib


import time

class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="tr.org.pardus.eta-menu",
                         flags=Gio.ApplicationFlags(8), **kwargs)
        self.window = None
        GLib.set_prgname("tr.org.pardus.eta-menu")
        self.time = 0

        self.add_main_option(
            "tray",
            ord("t"),
            GLib.OptionFlags(0),
            GLib.OptionArg(0),
            "Start application on tray mode",
            None,
        )

        self.add_main_option(
            "quit",
            ord("q"),
            GLib.OptionFlags(0),
            GLib.OptionArg(0),
            "Quit from application",
            None,
        )

        self.add_main_option(
            "defaults",
            ord("d"),
            GLib.OptionFlags(0),
            GLib.OptionArg(0),
            "Restore default settings",
            None,
        )

        self.add_main_option(
            "refresh",
            ord("r"),
            GLib.OptionFlags(0),
            GLib.OptionArg(0),
            "Refresh",
            None,
        )

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = MainWindow(self)
        else:
            if time.time() - self.time < 1:
                return
            self.time = time.time()
            self.window.control_args()
            if self.window.ui_main_window.is_visible():
                self.window.ui_main_window.set_visible(False)
            else:
                self.window.ui_main_window.set_visible(True)
                self.window.reset_scroll()
                self.window.ui_apps_searchentry.set_text("")
                self.window.ui_apps_flowbox.unselect_all()
                self.window.ui_userpins_flowbox.unselect_all()
                # self.window.control_display()
                self.window.ui_main_window.present()
                # self.window.focus_search()
                self.window.unfocus_search()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack()
        self.args = options
        self.activate()
        return 0


app = Application()
app.run(sys.argv)
