from flask import Blueprint, abort, jsonify

from .database.models import Drink


drinks = Blueprint('drinks', __name__)


'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
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
