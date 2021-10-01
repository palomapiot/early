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

from behave import given, then, when

from app.test.factories.user import UserFactory


@when('I submit a valid email')
def step_impl(context):
    br = context.browser
    br.get(context.base_url + '/account/password_reset/')

    # Checks for Cross-Site Request Forgery protection input
    assert br.find_element_by_name('csrfmiddlewaretoken').is_enabled()

    # Fill login form and submit it (valid version)
    br.find_element_by_name('email').send_keys('foo@foo.foo')
    br.find_element_by_name('submit').click()


@then('I am redirected to the reset password success page')
def step_impl(context):
    br = context.browser

    # Checks success status
    assert br.current_url.endswith('/account/password_reset/done/')


@when('I submit an empty email')
def step_impl(context):
    br = context.browser

    br.get(context.base_url + '/account/password_reset/')

    # Checks for Cross-Site Request Forgery protection input (once again)
    assert br.find_element_by_name('csrfmiddlewaretoken').is_enabled()

    # Fill login form and submit it (invalid version)
    br.find_element_by_name('email').send_keys('')
    br.find_element_by_name('submit').click()


@then('I am redirected to the reset password fail page')
def step_impl(context):
    br = context.browser

    # Checks redirection URL
    assert br.current_url.endswith('/account/password_reset/')
    assert br.find_element_by_class_name(
        'errorlist').text == "This field is required."
