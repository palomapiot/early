"""
    Copyright 2020-2021 Paloma Piot Pérez-Abadín
	
	This file is part of early.
    early is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    early is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with early.  If not, see <https://www.gnu.org/licenses/>.
"""

from selenium import webdriver

def before_all(context):
	# PhantomJS is used there (headless browser - meaning we can execute tests in a command-line environment, which is what we want for use with SemaphoreCI
	# For debugging purposes, you can use the Firefox driver instead.

	context.browser = webdriver.PhantomJS()
	context.browser.implicitly_wait(1)
	context.server_url = 'http://localhost:8000'

def after_all(context):
	# Explicitly quits the browser, otherwise it won't once tests are done
	context.browser.quit()

def before_feature(context, feature):
	# Code to be executed each time a feature is going to be tested
	pass