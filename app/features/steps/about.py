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

from behave import given, when, then
from app.test.factories.user import UserFactory

@given('an anonymous user')
def step_impl(context):
    pass

@when('I submit the about page')
def step_impl(context):
    br = context.browser
    br.get(context.base_url + '/about/')

	# Checks success status
    assert br.current_url.endswith('/about/')

@then('I am redirected to the about page')
def step_impl(context):
    br = context.browser

	# Checks success status
    assert br.current_url.endswith('/about/')
    assert br.find_element_by_class_name('lead').text == "Early Risk Detection of Mental Disorders."
