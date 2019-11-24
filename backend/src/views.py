from flask import Blueprint, abort, jsonify

from .database.models import Drink
from .auth.auth import requires_auth

drinks = Blueprint('drinks', __name__)


'''
Retrieves an undetailed list of drinks.
'''
@drinks.route('/drinks')
def retrieveDrinks():
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
        abort(500)


'''
Retrieves a detailed list of drinks.
'''


@drinks.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def retrieveDrinksDetail(payload):
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
        abort(500)
