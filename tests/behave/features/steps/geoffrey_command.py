import os
import subprocess

PROJECT_BASE = os.path.realpath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..', '..'))

@given('a command shell')
def step_impl(context):
    pass


@when('I execute "{command}"')
def step_impl(context, command):

    # Set some environment variables for coverage to work.
    env = os.environ.copy()
    env.update({
        'PYTHONPATH': PROJECT_BASE,  # sitecustomize.py is here
        'COVERAGE_PROCESS_START': os.path.join(PROJECT_BASE, '.coveragerc')})

    call = subprocess.Popen(
        args=command.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env)

    context.stdout, context.stderr = call.communicate()
    context.retval = call.returncode


@then('I can see "{text}" in "{stream_}"')
def step_impl(context, text, stream_):
    stream = getattr(context, stream_)
    assert text.encode('utf-8') in stream


@then('the command return value is "{retval}"')
def step_impl(context, retval):
    assert context.retval == int(retval)

