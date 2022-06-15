import os
import sys
from urllib import response
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random 

from models import *

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()
    categories_list = {category.id: category.type for category in categories}
    if len(categories_list) == 0:
      abort(404)
    return jsonify({  
      'success': True,
      'categories': categories_list
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  '''
  @app.route('/questions')
  def get_questions():
    selection = Question.query.all()
    selected_questions = paginate_questions(request, selection)
    categories = Category.query.all()

    if len(selected_questions) == 0:
      abort(404)
    return jsonify({
      'success': True,
      'questions': selected_questions,
      'total_questions': len(selection),
      'categories': {category.id: category.type for category in categories},
      'current_category': None
    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID.
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
        abort(404)
      question.delete()
      selection = Question.query.order_by(Question.id).all()
      selected_questions = paginate_questions(request, selection)
      return jsonify({
        'success': True,
        'deleted': question_id, 
        'questions': selected_questions,
        'total_questions': len(selection)
      })
    except:
      abort(422)  

  '''
  @TODO: 
  Create an endpoint to POST a new question,  
  '''
  @app.route('/questions', methods=["POST"])
  def create_question():
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    try:
      question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
      question.insert()
      selection = Question.query.order_by(Question.id).all()
      selected_questions = paginate_questions(request, selection)
      return jsonify({
        'success': True,
        'created': question.id,
        'questions': selected_questions,
        'total_questions': len(Question.query.all())
      })
    except:
      abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term.
  '''
  @app.route('/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    user_search_input = body.get('searchTerm', None)
    selection = Question.query.filter(Question.question.ilike(f'%{user_search_input}%')).all()
    selected_questions = paginate_questions(request, selection)

    if len(selected_questions) == 0:
      abort(404)  
    return jsonify({
      'success': True,
      'questions': selected_questions,
      'total_questions': len(selection)
    })  
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_question_based_on_category(category_id):
    selectedItem = Category.query.get(category_id)
    page = 1
    if request.args.get('page'):
      page = int(request.args.get('page'))
    categories = Category.query.all()
    questions = Question.query.filter(Question.category == selectedItem.id).all()
    selected_questions = paginate_questions(request, questions)
    if len(selected_questions) == 0:
      abort(404)
    return jsonify({
      'success': True,
      'questions': selected_questions,
      'total_questions': len(questions),
      'current_category': selectedItem.type,
      'categories': {category.id: category.type for category in categories}
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quiz_questions():
    body = request.get_json()
    previous_questions = body.get('previous_questions', None)
    quiz_category = body.get('quiz_category', None)
    if quiz_category['id'] == 0:
      questions = Question.query.all()  
    else:
      questions = Question.query.filter(Question.category == quiz_category['id']).all()
    quiz_questions = []
    for question in questions:
      if question.id not in previous_questions:
        quiz_questions.append(question)
    if len(quiz_questions) == 0:
      abort(404)
    random_question = quiz_questions[random.randint(0, len(quiz_questions) - 1)]
    return jsonify({
      'success': True,
      'question': random_question.format()
    })

        
  '''
  @TODO: 
  Create error handlers for all expected errors 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
    }), 400

  @app.errorhandler(404)
  def not_found(error):
        return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
        return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable request"
    }), 422

  @app.errorhandler(500) 
  def server_error(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "internal server error"
    }), 500


  return app

    