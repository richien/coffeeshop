from flask import Blueprint, abort, jsonify

from .database.models import Drink


drinks = Blueprint('drinks', __name__)


'''
Retrieves a list of drinks
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
