#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 14:53:13 2024

@author: fatihaltun
"""

import os
import signal

import gi

gi.require_version("GLib", "2.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject
from UserSettings import UserSettings

import locale
from locale import gettext as _

locale.bindtextdomain('eta-menu', '/usr/share/locale')
locale.textdomain('eta-menu')


class MainWindow(object):
    def __init__(self, application):
        self.Application = application

        self.main_window_ui_filename = os.path.dirname(os.path.abspath(__file__)) + "/../ui/MainWindow.glade"
        try:
            self.GtkBuilder = Gtk.Builder.new_from_file(self.main_window_ui_filename)
            self.GtkBuilder.connect_signals(self)
        except GObject.GError:
            print("Error reading GUI file: " + self.main_window_ui_filename)
            raise

        self.define_components()
        self.define_variables()
        self.main_window.set_application(application)

        self.user_settings()

        self.about_dialog.set_program_name(_("ETA Menu"))
        if self.about_dialog.get_titlebar() is None:
            about_headerbar = Gtk.HeaderBar.new()
            about_headerbar.set_show_close_button(True)
            about_headerbar.set_title(_("About ETA Menu"))
            about_headerbar.pack_start(Gtk.Image.new_from_icon_name("eta-menu", Gtk.IconSize.LARGE_TOOLBAR))
            about_headerbar.show_all()
            self.about_dialog.set_titlebar(about_headerbar)

        # Set version
        # If not getted from __version__ file then accept version in MainWindow.glade file
        try:
            version = open(os.path.dirname(os.path.abspath(__file__)) + "/__version__").readline()
            self.about_dialog.set_version(version)
        except:
            pass

        def sighandler(signum, frame):
            if self.about_dialog.is_visible():
                self.about_dialog.hide()
            self.main_window.get_application().quit()

        signal.signal(signal.SIGINT, sighandler)
        signal.signal(signal.SIGTERM, sighandler)

        if "tray" in self.Application.args.keys():
            self.main_window.set_visible(False)
        else:
            self.main_window.set_visible(True)
            self.main_window.show_all()

    def define_components(self):
        self.main_window = self.GtkBuilder.get_object("ui_main_window")
        self.about_dialog = self.GtkBuilder.get_object("ui_about_dialog")

    def define_variables(self):
        pass

    def user_settings(self):
        self.UserSettings = UserSettings()
        self.UserSettings.createDefaultConfig()
        self.UserSettings.readConfig()

    def set_autostart(self):
        self.UserSettings.set_autostart(self.UserSettings.config_autostart)

    def on_ui_about_button_clicked(self, button):
        self.about_dialog.run()
        self.about_dialog.hide()

    def on_ui_main_window_delete_event(self, widget, event):
        self.main_window.hide()
        return True

    def on_ui_main_window_destroy(self, widget, event):
        if self.about_dialog.is_visible():
            self.about_dialog.hide()
        self.main_window.get_application().quit()
