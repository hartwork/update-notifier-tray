#! /usr/bin/env python
# Copyright (C) 2014 Sebastian Pipping <sebastian@pipping.org>
# Licensed under GPL v3 or later

from distutils.core import setup
from update_notifier_tray.version import VERSION_STR


setup(
		name='update-notifier-tray',
		description='Tray icon notifiying of new package updates',
		license='GPL v3 or later',
		version=VERSION_STR,
		author='Sebastian Pipping',
		author_email='sebastian@pipping.org',
		url='update-notifier-tray',
		packages=[
				'update_notifier_tray',
				],
		scripts=[
				'update-notifier-tray',
				],
		)
