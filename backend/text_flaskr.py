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
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', 'str%40K!NS','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

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
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data['categories']))

    def test_get_paginated_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['total_questions'])

    # def test_get_questions_by_category(self):
    #     res = self.client().get('/categories/1/questions')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data["success", True])
    #     self.assertTrue(len(data['questions']))
    #     self.assertTrue(data['total_questions'])

    # def test_post_new_question(self):
    #     res = self.client().post('/questions', json={
    #         'question': 'What is the best food?',
    #         'answer': 'Pizza',
    #         'category': 1,
    #         'difficulty': 1
    #     })
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data["success", True])
    #     self.assertTrue(data['question_id'])

    # def test_delete_question_id(self):
    #     res = self.client().delete('/questions/1')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data["success", True])
    #     self.assertEqual(data['deleted'], 1)

    # def test_search_questions(self):
    #     res = self.client().post('/questions', json={
    #         'searchTerm': 'What'
    #     })
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data["success", True])
    #     self.assertTrue(len(data['questions']))
    #     self.assertTrue(data['total_questions'])

    # def test_get_questions_by_category(self):
    #     res = self.client().get('/questions?page=2')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data["success", True])
    #     self.assertTrue(len(data['questions']))
    #     self.assertTrue(data['total_questions'])
    
    # def test_404_if_question_does_not_exist(self):
    #     res = self.client().get('/questions/1000')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 404)
    #     self.assertEqual(data["success", False])
    #     self.assertEqual(data['message'], 'Resource not found')

    # def test_422_if_question_creation_fails(self):
    #     res = self.client().post('/questions', json={
    #         'question': 'What is the best food?',
    #         'answer': 'Pizza',
    #         'category': 1,
    #         'difficulty': 1
    #     })
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 422)
    #     self.assertEqual(data["success", False])
    #     self.assertEqual(data['message'], 'Unprocessable Entity')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()