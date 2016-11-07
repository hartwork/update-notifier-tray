# Copyright (C) 2016 Sebastian Pipping <sebastian@pipping.org>
# Licensed under GPL v3 or later

from update_notifier_tray.distros.debian import Debian


class Ubuntu(Debian):
	@staticmethod
	def detected(lsb_release_minus_a_output):
		return 'Ubuntu' in lsb_release_minus_a_output

	@staticmethod
	def get_command_line_name():
		return 'ubuntu'
