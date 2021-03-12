# pylint: disable=no-member  
# pylint: disable=import-error
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category, db
from flaskr.__init__ import paginate
from flask import request

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql:///{}".format(self.database_name)
        setup_db(self.app, self.database_path)
        
        self.new_question = {
            'question': 'How old is the Earth',
            'answer': '4.543 billion years',
            'difficulty': 4,
            'category': 1
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
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    #route(/questions)
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))
        self.assertEqual(data['current_category'], "None")

    
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=10')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Sorry, couldn't find a resource matching your request.\nPlease check the URL and the parameters if entered")
    

    #route('/questions/<int:question_id>', methods = ['DELETE'])
    def test_delete_question(self):
        res = self.client().delete('/questions/3')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_question'], 3)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
    

    def test_404_if_questions_does_not_exist(self):
        res = self.client().get('/questions/500')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Sorry, couldn't find a resource matching your request.\nPlease check the URL and the parameters if entered")
    

    #route('/search_questions', methods = ['POST'])
    def test_search_question(self):
        res = self.client().post('/search_questions', json = {'search_term': 'title'})
        data = json.loads(res.data)
        search_term = 'title'
        selection = Question.query.filter(Question.question.ilike("%{}%".format(search_term))).order_by('id').all()
        current_questions = paginate(request, selection)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['questions'], current_questions)
        self.assertEqual(len(data['total_questions']), len(selection))


    def test_search_error(self):
        res = self.client().post('/search_questions/30', json = {'search_term': 'title'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertSeEqual(data['message'], "Sorry, couldn't process your request. Please make sure\nyou have the credentials for such a reuest or try again later")

    #route("/categories/<int:category_id>/questions")
    def test_retrieve_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        selection = Question.query.filter(Question.category == 1).order_by('id').all()
        current_questions = paginate(request, selection)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['questions'], current_questions)
        self.assertEqual(len(data['total_questions']), len(selection))
        self.assertEqual(data['current_category'], 1)


    def test_failing_get_questions_by_category(self):
        res = self.client().get('/categories/500/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Sorry, couldn't find a resource matching your request.\nPlease check the URL and the parameters if entered")

    #route('/quizzes', methods = ['POST'])
    def test_play_quiz(self):
        #assuming previous_questions are all questions in the db except one (required_question)
        previous_questions = db.session.query(Question.question).order_by(Question.id).limit(18).all()
        message ={
            'previous_questions': previous_questions,
            'quiz_category': 4
        }
        res = self.client().get('/quizzes', json = message)
        data = json.loads(res.data)
        required_question = db.session.query(Question).filter(Question.id == 23).first().format()
       
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], required_question)
        self.assertEqual(data['play_category'], 4)



    def test_404_play_quiz(self):
        message = {
            'previous_questions': 'whatever',
            'quiz_category': 100
        }
        res = self.client().get('/quizzes', json = message)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Sorry, couldn't find a resource matching your request.\nPlease check the URL and the parameters if entered")


    #route('/questions', methods = ['POST'])
    def test_post_new_question(self):
        res = self.client().post('/questions', json = self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['posted'])
        self.assertTrue(len(data['current_questions']))
        self.assertTrue(data['total_questions'])
    

    def test_creation_not_possible(self):
        res = self.client().post('/questions/30', json = self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertSeEqual(data['message'], "Sorry, couldn't process your request. Please make sure\nyou have the credentials for such a reuest or try again later")
#Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()