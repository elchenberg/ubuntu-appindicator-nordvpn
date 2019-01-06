#!/usr/bin/env python3

import signal
import subprocess
import threading
import time

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
from gi.repository import Gtk, AppIndicator3, GObject


class Indicator():
    def __init__(self):
        self.app = "nordvpn-status"
        iconpath = ""
        self.indicator = AppIndicator3.Indicator.new(
            self.app, iconpath,
            AppIndicator3.IndicatorCategory.OTHER)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.create_menu())
        self.indicator.set_label("NordVPN Status: Unknown", self.app)
        self.update = threading.Thread(target=self.show_status)
        self.update.setDaemon(True)
        self.update.start()

    def show_status(self):
        while True:
            cmd = ["nordvpn", "status"]
            nordvpn_status_message = subprocess.check_output(cmd)
            nordvpn_status_message = nordvpn_status_message.decode("utf-8")
            nordvpn_status_message_lines = nordvpn_status_message.splitlines()
            nordvpn_status_message_lines = nordvpn_status_message_lines[3:]
            mention = "NordVPN " + nordvpn_status_message_lines[0]
            GObject.idle_add(
                self.indicator.set_label,
                mention, self.app,
                priority=GObject.PRIORITY_DEFAULT
            )
            time.sleep(60)

    def create_menu(self):
        menu = Gtk.Menu()
        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', self.stop)
        menu.append(item_quit)

        menu.show_all()
        return menu

    def stop(self, source):
        Gtk.main_quit()


Indicator()
GObject.threads_init()
signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()
