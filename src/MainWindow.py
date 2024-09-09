#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 14:53:13 2024

@author: fatihaltun
"""

import os
import signal
import subprocess
import gi

gi.require_version("GLib", "2.0")
gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gtk, GObject, Gio, GLib, GdkPixbuf, Gdk
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

        self.set_desktop_apps()
        self.control_display()
        self.focus_search()

        self.ui_main_window.set_application(application)

        self.user_settings()

        self.ui_about_dialog.set_program_name(_("ETA Menu"))
        if self.ui_about_dialog.get_titlebar() is None:
            about_headerbar = Gtk.HeaderBar.new()
            about_headerbar.set_show_close_button(True)
            about_headerbar.set_title(_("About ETA Menu"))
            about_headerbar.pack_start(Gtk.Image.new_from_icon_name("eta-menu", Gtk.IconSize.LARGE_TOOLBAR))
            about_headerbar.show_all()
            self.ui_about_dialog.set_titlebar(about_headerbar)

        # Set version
        # If not getted from __version__ file then accept version in MainWindow.glade file
        try:
            version = open(os.path.dirname(os.path.abspath(__file__)) + "/__version__").readline()
            self.ui_about_dialog.set_version(version)
        except:
            pass

        def sighandler(signum, frame):
            if self.ui_about_dialog.is_visible():
                self.ui_about_dialog.hide()
            self.ui_main_window.get_application().quit()

        signal.signal(signal.SIGINT, sighandler)
        signal.signal(signal.SIGTERM, sighandler)

        if "tray" in self.Application.args.keys():
            self.ui_main_window.set_visible(False)
        else:
            self.ui_main_window.set_visible(True)
            self.ui_main_window.show_all()

    def define_components(self):
        self.ui_main_window = self.GtkBuilder.get_object("ui_main_window")
        self.ui_main_window.set_skip_taskbar_hint(True)
        self.ui_about_dialog = self.GtkBuilder.get_object("ui_about_dialog")
        self.ui_apps_iconview = self.GtkBuilder.get_object("ui_apps_iconview")
        self.ui_apps_iconview.set_pixbuf_column(0)
        self.ui_apps_iconview.set_text_column(1)
        self.ui_apps_liststore = self.GtkBuilder.get_object("ui_apps_liststore")
        self.ui_myapps_treemodelfilter = self.GtkBuilder.get_object("ui_myapps_treemodelfilter")
        self.ui_myapps_treemodelfilter.set_visible_func(self.apps_filter_function)
        self.ui_apps_searchentry = self.GtkBuilder.get_object("ui_apps_searchentry")
        self.ui_apps_scrolledwindow = self.GtkBuilder.get_object("ui_apps_scrolledwindow")

    def define_variables(self):
        pass

    def user_settings(self):
        self.UserSettings = UserSettings()
        self.UserSettings.createDefaultConfig()
        self.UserSettings.readConfig()

    def control_display(self):
        try:
            display = Gdk.Display.get_default()
            monitor = display.get_primary_monitor()
            geometry = monitor.get_geometry()
            w = geometry.width
            h = geometry.height
            s = Gdk.Monitor.get_scale_factor(monitor)

            width = w / 3
            height = h / 2

            self.ui_main_window.resize(width, height)
            self.ui_main_window.move(0, h - height)

        except Exception as e:
            print("control_display: {}".format(e))

    def reset_scroll(self):
        v_adj = self.ui_apps_scrolledwindow.get_vadjustment()
        v_adj.set_value(v_adj.get_lower())

    def focus_search(self):
        self.ui_apps_searchentry.grab_focus()

    def get_desktop_apps(self):
        apps = []
        for app in Gio.DesktopAppInfo.get_all():

            id = app.get_id()
            name = app.get_name()
            executable = app.get_executable()
            nodisplay = app.get_nodisplay()
            icon = app.get_string('Icon')
            description = app.get_description() or app.get_generic_name() or app.get_name()
            filename = app.get_filename()
            keywords = " ".join(app.get_keywords())

            if executable and not nodisplay:
                apps.append({"id": id, "name": name, "icon": icon, "description": description, "filename": filename,
                             "keywords": keywords, "executable": executable})

        apps = sorted(dict((v['name'], v) for v in apps).values(), key=lambda x: locale.strxfrm(x["name"]))
        return apps

    def set_desktop_apps(self):
        desktop_apps = self.get_desktop_apps()
        GLib.idle_add(self.ui_apps_liststore.clear)


        for desktop_app in desktop_apps:

            try:
                app_icon = Gtk.IconTheme.get_default().load_icon(desktop_app["icon"], 64, Gtk.IconLookupFlags.FORCE_SIZE)
            except:
                try:
                    app_icon = GdkPixbuf.Pixbuf.new_from_file_at_size(desktop_app["icon"], 64, 64)
                except:
                    app_icon = Gtk.IconTheme.get_default().load_icon("image-missing", 64,
                                                                     Gtk.IconLookupFlags.FORCE_SIZE)

            app_name = desktop_app["name"]

            GLib.idle_add(self.add_desktop_app_to_ui, [app_icon, app_name, desktop_app["id"]])

    def add_desktop_app_to_ui(self, app_list):
        self.ui_apps_liststore.append(app_list)

    def set_autostart(self):
        self.UserSettings.set_autostart(self.UserSettings.config_autostart)

    def apps_filter_function(self, model, iteration, data):
        search_entry_text = self.ui_apps_searchentry.get_text()
        app_name = model[iteration][1]
        if search_entry_text.lower() in app_name.lower():
            return True

    def on_ui_apps_iconview_selection_changed(self, iconview):
        selected_items = iconview.get_selected_items()
        if len(selected_items) == 1:
            treeiter = self.ui_myapps_treemodelfilter.get_iter(selected_items[0])
            app_id = self.ui_myapps_treemodelfilter.get(treeiter, 2)[0]
            print("Open: {}".format(app_id))
            self.ui_main_window.hide()
            Gio.DesktopAppInfo.new(app_id).launch([], None)

    def on_ui_apps_searchentry_search_changed(self, search_entry):
        print(search_entry.get_text())
        self.ui_myapps_treemodelfilter.refilter()

    def on_ui_lock_button_clicked(self, button):
        self.ui_main_window.hide()
        subprocess.Popen(["cinnamon-screensaver-command", "--lock"])

    def on_ui_logout_button_clicked(self, button):
        self.ui_main_window.hide()
        subprocess.Popen(["cinnamon-session-quit", "--logout"])

    def on_ui_poweroff_button_clicked(self, button):
        self.ui_main_window.hide()
        subprocess.Popen(["cinnamon-session-quit", "--power-off"])

    def on_ui_about_button_clicked(self, button):
        self.ui_main_window.hide()
        subprocess.Popen(["pardus-about"])

    def on_ui_main_window_delete_event(self, widget, event):
        self.ui_main_window.hide()
        return True

    def on_ui_main_window_destroy(self, widget, event):
        if self.ui_about_dialog.is_visible():
            self.ui_about_dialog.hide()
        self.ui_main_window.get_application().quit()

    def on_ui_main_window_focus_out_event(self, widget, event):
        self.ui_main_window.hide()
        return True
