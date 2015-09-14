# Copyright (C) 2015 Sebastian Pipping <sebastian@pipping.org>
# Licensed under GPL v3 or later

from __future__ import print_function

import signal
import subprocess

from update_notifier_tray.distro import Distro


_cache_instance = None


def _open_apt_cache():
	import apt

	if hasattr(apt.Cache, 'close'):
		cache = apt.Cache()
		cache.open()
		return cache
	else:
		global _cache_instance
		if _cache_instance is None:
			_cache_instance = apt.Cache()
		_cache_instance.open()
		return _cache_instance


def _close_apt_cache(cache):
	if hasattr(cache, 'close'):
		cache.close()


class Debian(Distro):
	def describe_update_gui_action(self):
		return 'Run gpk-&update-viewer'

	@staticmethod
	def detected(lsb_release_minus_a_output):
		return 'Debian' in lsb_release_minus_a_output

	@staticmethod
	def get_command_line_name():
		return 'debian'

	def get_updateable_package_count(self):
		count = 0
		cache = _open_apt_cache()
		try:
			for package_name in cache.keys():
					if cache[package_name].is_upgradable:
							count += 1
			return count
		finally:
			_close_apt_cache(cache)

	def get_check_interval_seconds(self):
		return 60

	def start_update_gui(self):
		subprocess.Popen(['gpk-update-viewer'])
		signal.signal(signal.SIGCHLD, signal.SIG_IGN)  # So the kernel takes care of the zombie
