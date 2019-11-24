import json
from flask import abort


def validate_create_drink_request(request):
    '''Validates the request body for a create drink request.

    Args:
        request (obj):  The request object
    Returns:
        bool: True if successfull.
    '''
    # checks that the request body has the expected shape
    expected_request_body = [
            'title',
            'recipe'
    ]
    for field in expected_request_body:
        if field not in json.loads(request.data).keys():
            abort(400)
    # checks that the recipe list is not empty and that
    #  the items in the list have the expected shape
    recipe = json.loads(request.data)['recipe']
    if not isinstance(recipe, list) or len(recipe) == 0:
        abort(400)
    expected_recipe_fields = [
        'name',
        'color',
        'parts'
    ]
    for item in recipe:
        for field in expected_recipe_fields:
            if field not in item.keys():
                abort(400)
    return True