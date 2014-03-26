from behave import given, then

@given('a dummy useless test')
def step_impl(context):
    context.dummy = True

@then('the test should run fine')
def step_impl(context):
    assert context.dummy

