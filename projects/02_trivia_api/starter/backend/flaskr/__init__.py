import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.sql import func
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

#Function to paginate questions and return them in JSON format
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions
#Helper function to format categories
def format_categories(categories):    
    return {category.id:category.type for category in categories}

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    # DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    cors = CORS(app)

    # CORS Headers
    '''
    DONE: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response
    

    '''
    DONE: Create an endpoint to handle GET requests 
    for all available categories.
    '''
    @app.route('/categories', methods=['GET'])
    def show_categories():

        selection = Category.query.order_by(Category.id).all()
        # we need the formatted json
        categories = format_categories(selection)
        #If no categories, we return 404
        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': categories,
            'total_categories': len(categories)
        })

    '''
    DONE: Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 
      
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    @app.route('/questions', methods=['GET'])
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        paginated_questions = paginate_questions(request, selection)
        # current_category=request.args['category']
        categories = format_categories(Category.query.order_by(Category.id).all())
        if len(paginated_questions) == 0 or len(categories) == 0:
            abort(404)

        return jsonify({
            'questions': paginated_questions,
            'total_questions': len(selection),
            'categories': categories,
            'current_category': 'ALL'
        })
    '''
    DONE: Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(selection)
            })

        except:
            print(sys.exc_info())
            abort(422)

    '''
    DONE: Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        question_text = body.get('question')
        answer = body.get('answer')
        difficulty = body.get('difficulty')
        category = body.get('category')
        search = body.get('searchTerm')

        if search:
            selection = Question.query.order_by(Question.id).filter(
                Question.question.ilike('%{}%'.format(search)))
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection.all())
            })
        else:
            question = Question(question=question_text, answer=answer,
                                difficulty=difficulty, category=category)
            selection = Question.query.order_by(Question.id).all()
            paginated_questions = paginate_questions(request, selection)
            try:
                question.insert()
            except:
                print(sys.exc_info())
                abort(422)

            return jsonify({
                'success': True,
                'created': question.format(),
                'questions': paginated_questions,
                'total_questions': len(selection)

            })

    '''
    DONE: Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''

    '''
    DONE: Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        
        category = Category.query.filter(Category.id==category_id).one_or_none()
        if category == None:
              abort(404)
        
        selection = Question.query.filter(Question.category==category_id).order_by(Question.id).all()
        paginated_questions = paginate_questions(request, selection)
                     
        if len(paginated_questions) == 0:
            abort(404)  
        
        categories =format_categories(Category.query.order_by(Category.id).all())
        
        return jsonify({
            'questions': paginated_questions,
            'total_questions': len(paginated_questions),
            'categories': categories,
            'current_category': category.type
        })
    
    
    '''
    DONE: Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    @app.route('/quizzes', methods=['POST'])
    def get_question():
         
        body = request.get_json()
        previous_questions = body.get('previous_questions')
        quiz_category = body.get('quiz_category')
        #If the category is ALL, we need other query
        if quiz_category['id'] == 0:
            question = Question.query.filter(Question.id.notin_(previous_questions)).order_by(func.random()).first()
        else:
            question = Question.query.filter(Question.id.notin_(previous_questions), Question.category == quiz_category['id']).order_by(func.random()).first()

        if question == None:
          abort(404)
          
        return jsonify({
            'success': True,
            'question': question.format(),
        })     
    
    
    '''DONE: Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500
    return app
