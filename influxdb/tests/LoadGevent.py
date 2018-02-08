# -*- coding: utf-8 -*-
"""
Copyright (C) 2013/2016 Laurent Labatut / Laurent Champagnac.

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU General Public License
 as published by the Free Software Foundation; either version 2
 of the License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
 ===============================================================================
"""

import os
import unittest
force_gevent = False
if os.environ.get('LOAD_GEVENT', False) == 'True':
    force_gevent = True

skipIfNotGevent = unittest.skipIf(
    force_gevent,
    "Skipping this test on no gevent environement.")
skipIfGevent = unittest.skipIf(
    not force_gevent,
    "Skipping this test on gevent environement.")


def patch():
    """Import gevent and dependencie."""
    if force_gevent:
        from pythonsol.SolBase import SolBase
        SolBase.voodoo_init()
        SolBase.logging_init(force_reset=True, log_to_syslog=False, log_to_console=True)
