# Copyright (C) 2014 Sebastian Pipping <sebastian@pipping.org>
# Licensed under GPL v3 or later

from __future__ import print_function

import os
import signal
import subprocess
import sys
from threading import Event, Lock, Thread
import time

import apt
import pynotify
from PySide import QtGui, QtCore


_CHECK_INTERVAL_SECONDS = 60


_cache_instance = None


def cache_open():
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


def cache_close(cache):
	if hasattr(apt.Cache, 'close'):
		cache.close()


def _get_updateable_package_count():
	cache = cache_open()

	count = 0
	for package_name in cache.keys():
		if cache[package_name].is_upgradable:
			count += 1

	cache_close(cache)

	return count


def _start_update_gui():
	subprocess.Popen(['gpk-update-viewer'])
	signal.signal(signal.SIGCHLD, signal.SIG_IGN)  # So the kernel takes care of the zombie


class _UpdateNotifierTrayIcon(QtGui.QSystemTrayIcon):
	def __init__(self, icon=None, parent=None):
		super(_UpdateNotifierTrayIcon, self).__init__(icon, parent)

		menu = QtGui.QMenu(parent)
		update_action = QtGui.QAction('Run gpk-&update-viewer', self, triggered=_start_update_gui)
		menu.addAction(update_action)
		exit_action = QtGui.QAction('&Exit', self, triggered=self.handle_exit)
		menu.addAction(exit_action)
		self.setContextMenu(menu)

		self.activated.connect(self.handle_activated)
		self._previous_count = 0
		self._previous_count_lock = Lock()

	def handle_activated(self, reason):
		if reason in (QtGui.QSystemTrayIcon.Trigger, QtGui.QSystemTrayIcon.DoubleClick, QtGui.QSystemTrayIcon.MiddleClick):
			_start_update_gui()

	@QtCore.Slot(int)
	def handle_count_changed(self, count):
		self._previous_count_lock.acquire()

		unchanged = (count == self._previous_count)
		self._previous_count = count

		self._previous_count_lock.release()

		if unchanged:
			return

		if count > 0:
			title = 'Updates available'

			if count == 1:
				message = 'There is 1 update available'
			else:
				message = 'There are %d updates available' % count

			self.setToolTip(message)
			self.show()

			notification = pynotify.Notification(title, message)
			notification.show()
		else:
			self.hide()

	def handle_exit(self):
		self._thread.stop()
		self._thread.join()
		QtGui.qApp.quit()

	def set_thread(self, check_thread):
		self._thread = check_thread


class _UpdateCheckThread(Thread, QtCore.QObject):
	_count_changed = QtCore.Signal(int)

	def __init__(self):
		Thread.__init__(self)
		QtCore.QObject.__init__(self)
		self._exit_wanted = Event()

	def set_tray_icon(self, tray_icon):
		self._count_changed.connect(tray_icon.handle_count_changed)

	def stop(self):
		self._exit_wanted.set()

	def run(self):
		while not self._exit_wanted.isSet():
			count = _get_updateable_package_count()
			self._count_changed.emit(count)
			for i in range(_CHECK_INTERVAL_SECONDS):
				if self._exit_wanted.isSet():
					break
				time.sleep(1)


def main():
	signal.signal(signal.SIGINT, signal.SIG_DFL)  # To make killable using Ctrl+C

	app = QtGui.QApplication(sys.argv)
	dummy_widget = QtGui.QWidget()
	icon = QtGui.QIcon('/usr/share/icons/Tango/scalable/status/software-update-available.svg')
	tray_icon = _UpdateNotifierTrayIcon(icon, dummy_widget)
	check_thread = _UpdateCheckThread()
	pynotify.init(os.path.basename(sys.argv[0]))

	check_thread.set_tray_icon(tray_icon)
	tray_icon.set_thread(check_thread)

	check_thread.start()
	sys.exit(app.exec_())
