# Copyright (C) 2015 Sebastian Pipping <sebastian@pipping.org>
# Licensed under GPL v3 or later

from __future__ import print_function


class Distro(object):
	def describe_update_gui_action(self):
		raise NotImplementedError()

	@staticmethod
	def detected(lsb_release_minus_a_output):
		raise NotImplementedError()

	@staticmethod
	def get_command_line_name():
		raise NotImplementedError()

	def get_updateable_package_count(self):
		raise NotImplementedError()

	def get_check_interval_seconds(self):
		raise NotImplementedError()

	def start_update_gui(self):
		raise NotImplementedError()
