import json
from flask import Blueprint, abort, jsonify, request
from sqlalchemy import exc

from .database.models import Drink
from .auth.auth import requires_auth
from .helpers import validate_create_drink_request


drinks = Blueprint('drinks', __name__)

'''
Retrieves an undetailed list of drinks.
'''
@drinks.route('/drinks', methods=['GET'])
def retrieve_drinks():
    try:
        data = Drink.query.all()
        if not data:
            abort(404)
        drinks = [drink.short() for drink in data]
        return jsonify({
                    'success': True,
                    'drinks': drinks
                }), 200
    except Exception:
        abort(503)


'''
Retrieves a detailed list of drinks.
'''
@drinks.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def retrieve_drinks_detail(payload):
    try:
        data = Drink.query.all()
        if not data:
            abort(404)
        drinks = [drink.long() for drink in data]
        return jsonify({
                    'success': True,
                    'drinks': drinks
                }), 200
    except Exception:
        abort(503)


'''
Creates a new drink.
'''
@drinks.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    validate_create_drink_request(request)
    try:
        recipe = json.loads(request.data)['recipe']
        drink = Drink(
            title=json.loads(request.data)['title'],
            recipe=json.dumps(recipe)
        )
        drink.insert()
        return jsonify({
            'success': True,
            'drinks': drink.long()
        }), 201
    except exc.SQLAlchemyError:
        abort(422)
    except Exception:
        abort(503)
