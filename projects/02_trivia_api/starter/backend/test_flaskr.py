import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_user = os.environ.get("PSQL_USER")
        self.database_password = os.environ.get("PSQL_PWD")
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(self.database_user, self.database_password,'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        
        self.new_question = {
            'question':'Test Question',
            'answer': 'Test Answer',
            'difficulty': 1,
            'category':1
        }
        self.new_question_bad_category = {
            'question':'Test Question',
            'answer': 'Test Answer',
            'difficulty': 1,
            'category':9
        }
        
        self.new_search = {
            'searchTerm': 'title'
        }
        
        self.quizz_post = {
            "previous_questions": [33],
            "quiz_category": {
                "type": "Science",
                "id": "1"}
        }
        self.quizz_post_bad = {
            "previous_questions": [],
            "quiz_category": {
                "type": "Science", 
                "id": "9"
            }
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    DONE
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])
        self.assertTrue(len(data['categories']))
        
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
    
    def test_404_get_paginated_questions_beyond_limits(self):
        res = self.client().get('/questions/?page=300')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')
    
    #@app.route('/questions/<int:question_id>', methods=['DELETE'])
    def test_delete_question(self):
        
        question = Question.query.first()
        question_id = question.id

        res = self.client().delete('/questions/'+str(question_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
    
    def test_422_delete_question_not_found(self):
               
        res = self.client().delete('/questions/90000000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],"Unprocessable")
       
    #@app.route('/questions', methods=['POST'])
    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(data['success'], True)
        self.assertDictContainsSubset(self.new_question,data['created'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        
    def test_422_if_question_creation_fails(self):
        res = self.client().post('/questions', json=self.new_question_bad_category)
        data = json.loads(res.data)
        
        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'],"Unprocessable")
        
    #search
    def test_search_questions_by_text(self):
        res = self.client().post('/questions', json=self.new_search)
        data = json.loads(res.data)
        
        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
            
    #@app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def test_get_questions_of_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
        self.assertTrue(len(data['questions']))
    
    def test_404_get_questions_from_empty_category(self):
        res = self.client().get('/categories/9/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')
        
    #@app.route('/quizzes', methods=['POST'])
    def test_get_question_for_quizz(self):
        res = self.client().post('/quizzes', json=self.quizz_post)
        data = json.loads(res.data)
        
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        
    def test_404_get_question_for_quizz(self):
        res = self.client().post('/quizzes', json=self.quizz_post_bad)
        data = json.loads(res.data)
        
        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Resource not found')
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()