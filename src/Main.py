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


class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="tr.org.pardus.eta-menu",
                         flags=Gio.ApplicationFlags(8), **kwargs)
        self.window = None
        GLib.set_prgname("tr.org.pardus.eta-menu")

        self.add_main_option(
            "tray",
            ord("t"),
            GLib.OptionFlags(0),
            GLib.OptionArg(0),
            "Start application on tray mode",
            None,
        )

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = MainWindow(self)
        else:
            self.window.main_window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack()
        self.args = options
        self.activate()
        return 0


app = Application()
app.run(sys.argv)
