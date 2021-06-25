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

        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', 'tgkicksass','localhost:15432', self.database_name)
        
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question':    'What is my name?',
            'answer':  'xavi',
            'difficulty':  10,
            'category':    4,
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
    def test_get_categories(self):
        res = self.client().get('/categories')
        self.assertEqual(res.status_code, 200)

    def test_get_questions(self):
        res = self.client().get('/questions')
        self.assertEqual(res.status_code, 200)

    def test_get_category_question(self):
        res = self.client().get('/categories/1/questions')
        self.assertEqual(res.status_code, 200)

    def test_get_quizzes(self):
        data = {'previous_questions': [], 'quiz_category': {'type': 'click', 'id': 0}}
        res = self.client().post('/quizzes', json=data)
        self.assertEqual(res.status_code, 200)

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/books?page=1000', json={'rating': 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)

        book = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 1)
        self.assertTrue(data['total_books'])
        self.assertTrue(len(data['books']))
        self.assertEqual(book, None)

    def test_404_if_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        pass
    
    def test_422_if_book_creation_fails(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        pass

    def test_get_entry(self):
        res = self.client().get('/')
        self.assertEqual(res.status_code, 200)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()