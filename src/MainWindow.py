#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 14:53:13 2024

@author: fatihaltun
"""
import json
import os
import signal
import subprocess

import gi

gi.require_version("GLib", "2.0")
gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gtk, GObject, Gio, GLib, GdkPixbuf, Gdk
from UserSettings import UserSettings
from Utils import ErrorDialog

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

        self.ui_main_window.set_application(application)

        self.set_css()
        self.set_desktop_apps()
        self.focus_search()
        self.set_username()

        self.user_settings()

        # self.control_display()

        self.create_user_pinned_apps_from_file()

        self.start_monitoring()

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
        self.ui_about_button = self.GtkBuilder.get_object("ui_about_button")

        self.ui_apps_searchentry = self.GtkBuilder.get_object("ui_apps_searchentry")
        self.ui_apps_scrolledwindow = self.GtkBuilder.get_object("ui_apps_scrolledwindow")
        self.ui_username_label = self.GtkBuilder.get_object("ui_username_label")

        self.ui_apps_popover = self.GtkBuilder.get_object("ui_apps_popover")
        self.ui_userpins_popover = self.GtkBuilder.get_object("ui_userpins_popover")

        self.ui_apps_flowbox = self.GtkBuilder.get_object("ui_apps_flowbox")
        self.ui_userpins_flowbox = self.GtkBuilder.get_object("ui_userpins_flowbox")

        self.ui_apps_flowbox.set_filter_func(self.apps_filter_function)

        self.ui_apps_flowbox.get_style_context().add_class("eta-menu-flowbox")
        self.ui_userpins_flowbox.get_style_context().add_class("eta-menu-flowbox")

    def define_variables(self):
        self.trigger_in_progress = False
        self.monitoring_id = None
        self.right_clicked_app = None

    def user_settings(self):
        self.UserSettings = UserSettings()
        self.UserSettings.create_default_config()
        self.UserSettings.read_config()

    def control_display(self):
        print("in control_display")
        try:
            display = Gdk.Display.get_default()
            monitor = display.get_primary_monitor()
            geometry = monitor.get_geometry()
            w = geometry.width
            h = geometry.height

            width = int(w / 3)
            height = int(h / 1.45)

            if self.UserSettings.config_window_remember_size:
                if self.UserSettings.config_window_width == 0 and self.UserSettings.config_window_height == 0:
                    print("first run without config, so setting the window size as dynamically {} {}".format(width, height))
                    self.ui_main_window.resize(width, height)
                    self.UserSettings.write_config(window_width=width, window_height=height)
                    self.user_settings()
                else:
                    self.ui_main_window.resize(self.UserSettings.config_window_width,
                                               self.UserSettings.config_window_height)
            else:
                self.ui_main_window.resize(width, height)

            self.ui_main_window.move(0, h)
        except Exception as e:
            print("control_display: {}".format(e))

    def set_css(self):
        settings = Gtk.Settings.get_default()
        theme_name = "{}".format(settings.get_property('gtk-theme-name')).lower().strip()

        cssProvider = Gtk.CssProvider()
        if theme_name.startswith("pardus") or theme_name.startswith("adwaita"):
            cssProvider.load_from_path(os.path.dirname(os.path.abspath(__file__)) + "/../data/css/all.css")
        elif theme_name.startswith("adw-gtk3") or theme_name.startswith("eta"):
            cssProvider.load_from_path(os.path.dirname(os.path.abspath(__file__)) + "/../data/css/adw.css")
        else:
            cssProvider.load_from_path(os.path.dirname(os.path.abspath(__file__)) + "/../data/css/base.css")
        screen = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def set_username(self):
        username = GLib.get_user_name()
        user_real_name = GLib.get_real_name()

        if user_real_name == "" or user_real_name == "Unknown":
            user_real_name = username

        self.ui_username_label.set_markup("<b>{}</b>".format(user_real_name))
        self.ui_username_label.set_tooltip_text("{}".format(username))

    def reset_scroll(self):
        v_adj = self.ui_apps_scrolledwindow.get_vadjustment()
        v_adj.set_value(v_adj.get_lower())

    def focus_search(self):
        GLib.idle_add(self.ui_about_button.grab_focus)
        GLib.idle_add(self.ui_apps_searchentry.grab_focus)

    def start_monitoring(self):
        data_dirs = []

        system_dirs = GLib.get_system_data_dirs()
        user_dir = GLib.get_user_data_dir()

        for sys_dir in system_dirs:
            data_dirs.append(os.path.join(sys_dir, "applications"))
        data_dirs.append((os.path.join(user_dir, "applications")))

        data_dirs_with_subs = data_dirs

        for data_dir in data_dirs:
            sub_dirs = [x[0] for x in os.walk(data_dir)]
            for sub in sub_dirs:
                if sub not in data_dirs_with_subs:
                    data_dirs_with_subs.append(sub)

        self.gdir = {}
        count = 1
        for data_dir in data_dirs_with_subs:
            self.gdir["monitor-{}".format(count)] = Gio.file_new_for_path(data_dir).monitor_directory(0, None)
            self.gdir["monitor-{}".format(count)].connect('changed', self.on_app_info_changed)
            count += 1

        print("Monitoring: {}".format(data_dirs_with_subs))

    def on_app_info_changed(self, file_monitor, file, other_file, event_type):
        print("App Info Changed: {} {}".format(file.get_path(), event_type))

        if event_type in [Gio.FileMonitorEvent.CHANGES_DONE_HINT, Gio.FileMonitorEvent.DELETED]:
            if "{}".format(file.get_path()).endswith(".desktop"):
                print("App Info Trigger: {} {}".format(file.get_path(), event_type))
                if not self.trigger_in_progress:
                    self.trigger_in_progress = True
                    if self.monitoring_id is not None:
                        GLib.source_remove(self.monitoring_id)
                    self.monitoring_id = GLib.timeout_add_seconds(5, self.set_desktop_apps)

    def create_user_pinned_apps_from_file(self):
        user_pins = self.UserSettings.get_user_pins()
        if not user_pins:
            print("user pins empty")
            return
        for user_app_id in user_pins["apps"]:
            try:
                app = Gio.DesktopAppInfo.new(user_app_id)
            except Exception as e:
                print("{} {}".format(user_app_id, e))
                continue
            app_id = app.get_id()
            app_name = app.get_name()
            app_icon_name = app.get_string('Icon')
            app_filename = app.get_filename()

            self.add_user_pinned_app_to_ui(app_id, app_name, app_icon_name, app_filename)

    def add_user_pinned_app_to_ui(self, app_id, app_name, app_icon_name, app_filename):
        icon = Gtk.Image.new()
        try:
            app_icon = Gtk.IconTheme.get_default().load_icon(app_icon_name, 32, Gtk.IconLookupFlags.FORCE_SIZE)
        except:
            try:
                app_icon = GdkPixbuf.Pixbuf.new_from_file_at_size(app_icon_name, 32, 32)
            except:
                app_icon = Gtk.IconTheme.get_default().load_icon("image-missing", 32,
                                                                 Gtk.IconLookupFlags.FORCE_SIZE)
        icon.set_from_pixbuf(app_icon)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.pack_start(icon, False, True, 0)

        listbox = Gtk.ListBox.new()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        listbox.connect("button-release-event", self.on_userpins_listbox_released, listbox)
        listbox.name = {"id": app_id, "name": app_name, "icon_name": app_icon_name, "icon": app_icon,
                        "filename": app_filename}
        listbox.get_style_context().add_class("eta-menu-listbox")
        GLib.idle_add(listbox.add, box)

        GLib.idle_add(self.ui_userpins_flowbox.insert, listbox, GLib.PRIORITY_DEFAULT_IDLE)
        GLib.idle_add(self.ui_userpins_flowbox.show_all)

    def get_desktop_apps(self):
        apps = []
        for app in Gio.DesktopAppInfo.get_all():

            app_id = app.get_id()
            app_name = app.get_name()
            executable = app.get_executable()
            nodisplay = app.get_nodisplay()
            icon_name = app.get_string('Icon')
            description = app.get_description() or app.get_generic_name() or app.get_name()
            filename = app.get_filename()
            keywords = " ".join(app.get_keywords())
            categories = app.get_categories() if app.get_categories() else ""
            if executable and not nodisplay:
                apps.append(
                    {"id": app_id, "name": app_name, "icon_name": icon_name, "description": description,
                     "filename": filename, "keywords": keywords, "executable": executable,
                     "categories": categories})

        apps = sorted(dict((v['name'], v) for v in apps).values(), key=lambda x: locale.strxfrm(x["name"]))
        return apps

    def set_desktop_apps(self):
        print("in set_desktop_apps")
        desktop_apps = self.get_desktop_apps()
        for row in self.ui_apps_flowbox:
            GLib.idle_add(self.ui_apps_flowbox.remove, row)

        for desktop_app in desktop_apps:

            app_name = desktop_app["name"]
            icon = Gtk.Image.new()
            try:
                app_icon = Gtk.IconTheme.get_default().load_icon(desktop_app["icon_name"], 64,
                                                                 Gtk.IconLookupFlags.FORCE_SIZE)
            except:
                try:
                    app_icon = GdkPixbuf.Pixbuf.new_from_file_at_size(desktop_app["icon_name"], 64, 64)
                except:
                    app_icon = Gtk.IconTheme.get_default().load_icon("image-missing", 64,
                                                                     Gtk.IconLookupFlags.FORCE_SIZE)
            icon.set_from_pixbuf(app_icon)

            label = Gtk.Label.new()
            label.set_text(app_name)
            label.set_line_wrap(True)
            label.set_justify(Gtk.Justification.CENTER)
            label.set_max_width_chars(10)

            box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)
            box.pack_start(icon, False, True, 0)
            box.pack_start(label, False, True, 0)

            listbox = Gtk.ListBox.new()
            listbox.set_selection_mode(Gtk.SelectionMode.NONE)
            listbox.connect("button-release-event", self.on_apps_listbox_released, listbox)
            listbox.name = {"id": desktop_app["id"], "name": desktop_app["name"], "icon_name": desktop_app["icon_name"],
                            "icon": app_icon, "filename": desktop_app["filename"],
                            "description": desktop_app["description"],
                            "keywords": desktop_app["keywords"],
                            "executable": desktop_app["executable"],
                            "categories": desktop_app["categories"]}
            listbox.get_style_context().add_class("eta-menu-listbox")
            GLib.idle_add(listbox.add, box)

            GLib.idle_add(self.ui_apps_flowbox.insert, listbox, GLib.PRIORITY_DEFAULT_IDLE)

        GLib.idle_add(self.ui_apps_flowbox.show_all)

        self.trigger_in_progress = False
        if self.monitoring_id is not None:
            GLib.source_remove(self.monitoring_id)
            self.monitoring_id = None

    def on_apps_listbox_released(self, widget, event, listbox):
        # if event.button == 1:
        #     print(f"Sol tıklandı: {listbox.name}")
        #     GLib.idle_add(self.ui_apps_flowbox.unselect_all)
        #     self.ui_main_window.hide()
        #     Gio.DesktopAppInfo.new(listbox.name["id"]).launch([], None)
        if event.button == 3:
            print(f"Right clicked: {listbox.name}")
            self.right_clicked_app = listbox.name
            self.ui_apps_flowbox.select_child(listbox.get_parent())
            self.ui_apps_popover.set_relative_to(listbox)
            self.ui_apps_popover.popup()

    def on_ui_apps_flowbox_child_activated(self, flowbox, child):
        print(f"Left clicked: {child.get_children()[0].name}")
        GLib.idle_add(self.ui_apps_flowbox.unselect_all)
        self.ui_main_window.hide()
        Gio.DesktopAppInfo.new(child.get_children()[0].name["id"]).launch([], None)

    def set_autostart(self):
        self.UserSettings.set_autostart(self.UserSettings.config_autostart)

    def apps_filter_function(self, row):
        search = self.ui_apps_searchentry.get_text().lower()
        app = row.get_children()[0].name
        if (search in app["name"].lower() or search in app["description"].lower()
                or search in app["executable"].lower() or search in app["categories"].lower()
                or search in app["keywords"].lower()):
            return True

    def on_ui_add_to_userpins_button_clicked(self, button):
        for row in self.ui_userpins_flowbox:
            if self.right_clicked_app["id"] == row.get_children()[0].name["id"]:
                print("{} already in pinned apps".format(self.right_clicked_app["id"]))
                self.ui_apps_popover.popdown()
                self.ui_apps_flowbox.unselect_all()
                return

        self.add_user_pinned_app_to_ui(self.right_clicked_app["id"], self.right_clicked_app["name"],
                                       self.right_clicked_app["icon_name"], self.right_clicked_app["filename"])

        self.UserSettings.add_user_pinned_app(self.right_clicked_app["id"])

        self.ui_apps_popover.popdown()
        self.ui_apps_flowbox.unselect_all()

    def on_userpins_listbox_released(self, widget, event, listbox):
        # if event.button == 1:
        #     print(f"Sol tıklandı: {listbox.name}")
        #     GLib.idle_add(self.ui_userpins_flowbox.unselect_all)
        #     self.ui_main_window.hide()
        #     Gio.DesktopAppInfo.new(listbox.name["id"]).launch([], None)
        if event.button == 3:
            print(f"Right clicked: {listbox.name}")
            self.ui_userpins_flowbox.select_child(listbox.get_parent())
            self.ui_userpins_popover.set_relative_to(listbox)
            self.ui_userpins_popover.popup()

    def on_ui_userpins_flowbox_child_activated(self, flowbox, child):
        print(f"Left clicked: {child.get_children()[0].name}")
        GLib.idle_add(self.ui_userpins_flowbox.unselect_all)
        self.ui_main_window.hide()
        Gio.DesktopAppInfo.new(child.get_children()[0].name["id"]).launch([], None)

    def on_ui_remove_from_userpins_button_clicked(self, button):
        app_id = self.ui_userpins_flowbox.get_selected_children()[0].get_children()[0].name["id"]
        self.UserSettings.remove_user_pinned_app(app_id)
        self.ui_userpins_flowbox.remove(self.ui_userpins_flowbox.get_selected_children()[0])

    def on_ui_add_to_panel_button_clicked(self, button):

        config_file = "{}/cinnamon/spices/grouped-window-list@cinnamon.org/2.json".format(GLib.get_user_config_dir())

        if os.path.exists(config_file):
            cf = open(config_file, "r")
            panel = json.load(cf)

            app_id = self.ui_apps_flowbox.get_selected_children()[0].get_children()[0].name["id"]

            old_pinned_value = panel["pinned-apps"]["value"]
            new_pinned_value = old_pinned_value + [app_id]
            panel["pinned-apps"]["value"] = new_pinned_value

            new_cf = open(config_file, "w")
            new_cf.write(json.dumps(panel, indent=4))
            new_cf.flush()

            try:
                subprocess.run("dbus-send --session --dest=org.Cinnamon.LookingGlass --type=method_call"
                               " /org/Cinnamon/LookingGlass org.Cinnamon.LookingGlass.ReloadExtension"
                               " string:'grouped-window-list@cinnamon.org' string:'APPLET'", shell=True)
            except Exception as e:
                print("{}".format(e))
        else:
            print("{} not exists.".format(config_file))
            ErrorDialog(_("Error"), "{} not exists.".format(config_file))

        self.ui_apps_popover.popdown()
        self.ui_apps_flowbox.unselect_all()

    def on_ui_add_to_desktop_button_clicked(self, button):
        source = Gio.File.new_for_path(
            self.ui_apps_flowbox.get_selected_children()[0].get_children()[0].name["filename"])
        dest = Gio.File.new_for_path(
            GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DESKTOP) + "/" + source.get_basename())

        source.copy(dest, Gio.FileCopyFlags.OVERWRITE, None, None, None)

        file_info = Gio.FileInfo.new()
        file_info.set_attribute_uint32("unix::mode", 0o755)
        dest.set_attributes_from_info(file_info, Gio.FileQueryInfoFlags.NONE, None)

        if os.path.isfile(source.get_path()) and os.path.isfile(dest.get_path()):
            print("{} copied to {}".format(source.get_path(), dest.get_path()))

        self.ui_apps_popover.popdown()
        self.ui_apps_flowbox.unselect_all()

    def on_ui_main_window_key_release_event(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.ui_main_window.hide()
            return True

    def on_ui_apps_searchentry_search_changed(self, search_entry):
        self.ui_apps_flowbox.invalidate_filter()

    def on_ui_lock_button_clicked(self, button):
        self.ui_main_window.hide()
        subprocess.Popen(["cinnamon-screensaver-command", "--lock"])

    def on_ui_logout_button_clicked(self, button):
        self.ui_main_window.hide()
        subprocess.Popen(["cinnamon-session-quit", "--logout"])

    def on_ui_poweroff_button_clicked(self, button):
        self.ui_main_window.hide()
        subprocess.Popen(["cinnamon-session-quit", "--power-off"])

    def on_ui_browser_button_clicked(self, button):
        self.ui_main_window.hide()
        subprocess.Popen(["xdg-open", "http:"])

    def on_ui_cinnamonsettings_button_clicked(self, button):
        self.ui_main_window.hide()
        subprocess.Popen(["cinnamon-settings"])

    def on_ui_terminal_button_clicked(self, button):
        self.ui_main_window.hide()
        subprocess.Popen(["x-terminal-emulator"])

    def on_ui_filemanager_button_clicked(self, button):
        self.ui_main_window.hide()
        subprocess.Popen(["xdg-open", GLib.get_home_dir()])

    def on_ui_username_button_clicked(self, button):
        self.ui_main_window.hide()
        subprocess.Popen(["cinnamon-settings", "user"])

    def on_ui_about_button_clicked(self, button):
        self.ui_main_window.hide()
        subprocess.Popen(["pardus-about"])

    def on_ui_main_window_delete_event(self, window, event):
        current_width, current_height = window.get_size()
        try:
            self.UserSettings.write_config(window_width=current_width, window_height=current_height)
            self.user_settings()
        except Exception as e:
            print("{}".format(e))

        self.ui_main_window.hide()
        return True

    def on_ui_main_window_destroy(self, widget, event):
        if self.ui_about_dialog.is_visible():
            self.ui_about_dialog.hide()
        self.ui_main_window.get_application().quit()

    def on_ui_main_window_focus_out_event(self, window, event):
        current_width, current_height = window.get_size()
        try:
            self.UserSettings.write_config(window_width=current_width, window_height=current_height)
            self.user_settings()
        except Exception as e:
            print("{}".format(e))

        self.ui_main_window.hide()
        return True

    def on_ui_main_window_show(self, window):
        self.control_display()
