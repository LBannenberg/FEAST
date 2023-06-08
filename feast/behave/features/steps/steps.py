import feast.tree as tree
from behave import *
import math


@given('a recipe {recipe}')
def step_implementation(context, recipe):
    context.recipe = recipe


@when('we inflate a tree from that recipe')
def step_implementation(context):
    context.tree = tree.create(context.recipe)


@then('the deflate is equal to the recipe')
def step_implementation(context):
    assert context.recipe == context.tree.deflate()


@then('it evaluates to to the correct result: {result}')
def step_implementation(context, result):
    if result.isnumeric():
        result = float(result)
        assert math.isclose(context.tree.evaluate({}), result)
    if result in ['true', 'false']:
        assert context.tree.evaluate() is (result == 'true')


@then('it reports the correct height: {height:d}')
def step_implementation(context, height):
    assert context.tree.height == height, f'{context.tree.height} is not equal to {height}'
