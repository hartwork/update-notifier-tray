# Copyright (C) 2015 Sebastian Pipping <sebastian@pipping.org>
# Licensed under GPL v3 or later

from __future__ import print_function

import signal
import subprocess

from update_notifier_tray.distro import Distro


class Debian(Distro):
	def describe_update_gui_action(self):
		return 'Run gpk-&update-viewer'

	def get_updateable_package_count(self):
		import apt

		count = 0
		cache = apt.Cache()
		for package_name in cache.keys():
				if cache[package_name].is_upgradable:
						count += 1
		return count

	def start_update_gui(self):
		subprocess.Popen(['gpk-update-viewer'])
		signal.signal(signal.SIGCHLD, signal.SIG_IGN)  # So the kernel takes care of the zombie
