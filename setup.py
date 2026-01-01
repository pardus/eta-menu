#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 14:53:13 2024

@author: fatihaltun
"""

import os
import subprocess

from setuptools import setup, find_packages


def create_mo_files():
    podir = "po"
    mo = []
    for po in os.listdir(podir):
        if po.endswith(".po"):
            os.makedirs("{}/{}/LC_MESSAGES".format(podir, po.split(".po")[0]), exist_ok=True)
            mo_file = "{}/{}/LC_MESSAGES/{}".format(podir, po.split(".po")[0], "eta-menu.mo")
            msgfmt_cmd = 'msgfmt {} -o {}'.format(podir + "/" + po, mo_file)
            subprocess.call(msgfmt_cmd, shell=True)
            mo.append(("/usr/share/locale/" + po.split(".po")[0] + "/LC_MESSAGES",
                       ["po/" + po.split(".po")[0] + "/LC_MESSAGES/eta-menu.mo"]))
    return mo

def create_applet_mo_files():
    podir = "applet/po"
    mo = []
    for po in os.listdir(podir):
        if po.endswith(".po"):
            os.makedirs("{}/{}/LC_MESSAGES".format(podir, po.split(".po")[0]), exist_ok=True)
            mo_file = "{}/{}/LC_MESSAGES/{}".format(podir, po.split(".po")[0], "menu@etap.org.tr.mo")
            msgfmt_cmd = 'msgfmt {} -o {}'.format(podir + "/" + po, mo_file)
            subprocess.call(msgfmt_cmd, shell=True)
            mo.append(("/usr/share/locale/" + po.split(".po")[0] + "/LC_MESSAGES",
                       [podir + "/" + po.split(".po")[0] + "/LC_MESSAGES/menu@etap.org.tr.mo"]))
    return mo

changelog = "debian/changelog"
if os.path.exists(changelog):
    head = open(changelog).readline()
    try:
        version = head.split("(")[1].split(")")[0]
    except:
        print("debian/changelog format is wrong for get version")
        version = "0.0.0"
    f = open("src/__version__", "w")
    f.write(version)
    f.close()

data_files = [
                 ("/usr/bin", ["eta-menu"]),
                 ("/usr/share/pardus/eta-menu/ui",
                  ["ui/MainWindow.glade"]),
                 ("/usr/share/pardus/eta-menu/src",
                  ["src/Main.py",
                   "src/MainWindow.py",
                   "src/UserSettings.py",
                   "src/Utils.py",
                   "src/__version__"]),
                 ("/usr/share/pardus/eta-menu/data",
                  ["data/eta-menu.svg",
                   "data/eta-menu-panel-symbolic.svg",
                   "data/tr.org.pardus.eta-menu.desktop",
                   "data/tr.org.pardus.eta-menu-autostart.desktop"]),
                 ("/usr/share/pardus/eta-menu/data/css",
                  ["data/css/adw.css",
                   "data/css/all.css",
                   "data/css/base.css"]),
                 ("/usr/share/icons/hicolor/scalable/apps/",
                  ["data/eta-menu.svg",
                   "data/eta-menu-panel-symbolic.svg"]),
                   
                 ("/usr/share/cinnamon/applets/eta-menu@karahan/",
                  ["data/eta-menu@karahan/metadata.json"]),
                  
                  ("/usr/share/cinnamon/applets/eta-menu@karahan/",
                  ["data/eta-menu@karahan/settings-schema.json"]),
                  
                     ("/usr/share/cinnamon/applets/eta-menu@karahan/",
                  ["data/eta-menu@karahan/applet.js"]),
               
                     ("/usr/share/applications/",
                  ["data/eta-menu.desktop"]),
              
                 ("/etc/eta/eta-menu/",
                  ["data/favorites.json"]),
                 ("/etc/xdg/autostart/",
                  ["data/tr.org.pardus.eta-menu-autostart.desktop"]),
                  ("/usr/share/cinnamon/applets/menu@etap.org.tr",
                  ["applet/applet.js",
                  "applet/metadata.json",
                  "applet/settings-schema.json"])
             ] + create_mo_files() + create_applet_mo_files()

setup(
    name="eta-menu",
    version=version,
    packages=find_packages(),
    scripts=["eta-menu"],
    install_requires=["PyGObject"],
    data_files=data_files,
    author="Fatih Altun",
    author_email="fatih.altun@pardus.org.tr",
    description="ETA Menu application.",
    license="GPLv3",
    keywords="eta-menu",
    url="https://github.com/pardus/eta-menu",
)
