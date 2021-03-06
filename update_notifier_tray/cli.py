# Copyright (C) 2014 Sebastian Pipping <sebastian@pipping.org>
# Licensed under GPL v3 or later

from __future__ import print_function

import argparse
import os
import signal
import subprocess
import sys
from threading import Event, Lock, Thread
import time

import pynotify
from PySide import QtGui, QtCore

from update_notifier_tray.distros.debian import Debian
from update_notifier_tray.distros.gentoo import Gentoo
from update_notifier_tray.distros.ubuntu import Ubuntu


_DISTRO_CLASSES = (
		Debian,
		Gentoo,
		Ubuntu,
		)


class _UpdateNotifierTrayIcon(QtGui.QSystemTrayIcon):
	def __init__(self, icon, parent, distro):
		super(_UpdateNotifierTrayIcon, self).__init__(icon, parent)

		menu = QtGui.QMenu(parent)
		update_action = QtGui.QAction(
				distro.describe_update_gui_action(),
				self,
				triggered=distro.start_update_gui,
				)
		menu.addAction(update_action)
		exit_action = QtGui.QAction('&Exit', self, triggered=self.handle_exit)
		menu.addAction(exit_action)
		self.setContextMenu(menu)

		self.activated.connect(self.handle_activated)
		self._previous_count = 0
		self._previous_count_lock = Lock()
		self._distro = distro

	def handle_activated(self, reason):
		if reason in (QtGui.QSystemTrayIcon.Trigger, QtGui.QSystemTrayIcon.DoubleClick, QtGui.QSystemTrayIcon.MiddleClick):
			self._distro.start_update_gui()

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

	def __init__(self, distro):
		Thread.__init__(self)
		QtCore.QObject.__init__(self)
		self._exit_wanted = Event()
		self._distro = distro

	def set_tray_icon(self, tray_icon):
		self._count_changed.connect(tray_icon.handle_count_changed)

	def stop(self):
		self._exit_wanted.set()

	def run(self):
		while not self._exit_wanted.isSet():
			count = self._distro.get_updateable_package_count()
			self._count_changed.emit(count)
			for i in xrange(self._distro.get_check_interval_seconds()):
				if self._exit_wanted.isSet():
					break
				time.sleep(1)


def main():
	signal.signal(signal.SIGINT, signal.SIG_DFL)  # To make killable using Ctrl+C

	parser = argparse.ArgumentParser()
	distros = parser.add_mutually_exclusive_group()
	for clazz in _DISTRO_CLASSES:
		name = clazz.get_command_line_name()
		distros.add_argument('--%s' % name, dest='distro_callable', action='store_const',
				const=clazz, help='force %s mode (default: distribution auto-detected)'
					% name.title())
	options = parser.parse_args()

	if options.distro_callable is None:
		with open('/dev/null', 'w') as dev_null:
			lsb_release_minus_a_output = subprocess.check_output([
					'lsb_release', '-a'], stderr=dev_null)
		for clazz in _DISTRO_CLASSES:
			if clazz.detected(lsb_release_minus_a_output):
				options.distro_callable = clazz
				print('INFO: %s detected for a distribution.'
						% clazz.get_command_line_name().title())
				break
		else:
			print('No supported distribution was detected, please check --help output.',
					file=sys.stderr)
			sys.exit(1)
	distro = options.distro_callable()

	app = QtGui.QApplication(sys.argv)
	dummy_widget = QtGui.QWidget()
	icon = QtGui.QIcon('/usr/share/icons/Tango/scalable/status/software-update-available.svg')
	tray_icon = _UpdateNotifierTrayIcon(icon, dummy_widget, distro)
	check_thread = _UpdateCheckThread(distro)
	pynotify.init(os.path.basename(sys.argv[0]))

	check_thread.set_tray_icon(tray_icon)
	tray_icon.set_thread(check_thread)

	check_thread.start()
	sys.exit(app.exec_())
