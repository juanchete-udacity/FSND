import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks(*args, **kwargs):

    try:
        drinks = [drink.long() for drink in Drink.query.all()]
       # print(drinks)
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
       print(sys.exc_info())
       abort (404)
'''
    DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def show_drinks_detail(jwt):
    try:
        drinks = [drink.long() for drink in Drink.query.all()]
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
       abort (404)

'''
DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_new_drink(jwt):
    # {id: -1, title: "TITULO", recipe: [{name: "Nombre Ingrediente", color: "red", parts: 2},…]}
    try:
        req_data = request.get_json()
        new_title = req_data.get('title', None)
        new_recipe = req_data.get('recipe', None)
        new_drink = Drink(
            title=new_title,
            recipe=json.dumps(new_recipe)
        )
        new_drink.insert()
        return jsonify({
            'success': True,
            'drinks': [new_drink.long()]
    })
    except:
        db.session.rollback()
        abort(422)


'''
DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(jwt, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        body = request.get_json()

        if None == drink:
            abort(404)

        drink.title = body.get('title')
        drink.recipe = json.dumps(body.get('recipe'))
        drink.update()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except:
        db.session.rollback()
        abort(422)


'''
DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    try:
        body = request.get_json()
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if None == drink:
            abort(404)
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink_id
        })
    except:
        db.session.rollback()
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
DONE implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
DONE implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def authorizationerror(error):
    
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Authorization error"
    }), 401
