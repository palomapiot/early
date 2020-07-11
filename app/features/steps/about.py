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
