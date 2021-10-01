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
import time
from app.test.factories.user import UserFactory
from app.test.factories.profile import ProfileFactory
from selenium.common.exceptions import NoSuchElementException


@given('a logged user')
def step_impl(context):
    # Creates a dummy user for our tests (user is not authenticated at this point)
    u = UserFactory(username='foo', email='foo@example.com')
    u.set_password('bar')
    u.save()

    # Log user
    br = context.browser
    br.get(context.base_url + '/account/login/')
    br.find_element_by_name('username').send_keys('foo')
    br.find_element_by_name('password').send_keys('bar')
    br.find_element_by_name('submit').click()

@given('an existing profile')
def step_impl(context):
    # Creates a dummy user for our tests (user is not authenticated at this point)
    context.experiment = ProfileFactory()
    context.experiment.save()

@when('I load the profiles page')
def step_impl(context):
    br = context.browser
    br.get(context.base_url + '/profiles/')

	# Checks success status
    assert br.current_url.endswith('/profiles/')

@then('I get a list of profiles')
def step_impl(context):
    br = context.browser

	# Checks success status
    assert br.current_url.endswith('/profiles/')
    assert br.find_element_by_name('profiles').text == 'Profiles'
    assert br.find_element_by_class_name(
        'card-header').text == "behave_test_1"

@when('I load the profile detail page')
def step_impl(context):
    br = context.browser
    br.get(context.base_url + '/profiles/1/')

	# Checks success status
    assert br.current_url.endswith('/profiles/1/')

@then('I get the profile details')
def step_impl(context):
    br = context.browser

	# Checks success status
    assert br.current_url.endswith('/profiles/1/')
    assert br.find_element_by_tag_name(
        'h1').text == "Profile: behave_test_1"

@when('I validate an existing profile')
def step_impl(context):
    br = context.browser
    br.get(context.base_url + '/profiles/1/')

    assert br.find_element_by_class_name(
        'badge-pill').text == 'Not processed'

    # Open validation modal
    br.find_element_by_class_name('btn-outline-primary').click()

    time.sleep(1)

	# Fill validation form and submit it (valid version)
    br.find_element_by_name('gender').send_keys('Female')
    br.find_element_by_name('depressed').click()
    br.find_element_by_name('submit').click()
        

@then('I am redirected to the success edit page')
def step_impl(context):
    br = context.browser

	# Checks success status
    assert br.current_url.endswith('/profiles/1/edit/')
    assert br.find_element_by_tag_name(
        'h1').text == "Profile: behave_test_1"
    assert br.find_element_by_class_name(
        'fa-check-circle') is not None
    assert br.find_element_by_class_name(
        'badge-pill').text == 'Depression'

@when('I validate with wrong values an existing profile')
def step_impl(context):
    br = context.browser
    br.get(context.base_url + '/profiles/1/')

    # Open validation modal
    br.find_element_by_class_name('btn-outline-primary').click()

    time.sleep(1)

	# Fill validation form and submit it (valid version)
    br.find_element_by_name('age').send_keys('55')
    br.find_element_by_name('submit').click()
        

@then('I get a submission error')
def step_impl(context):
    br = context.browser

	# Checks validation wasnt done
    try:
        element = br.find_element_by_class_name('fa-check-circle')
    except NoSuchElementException:
        pass
    