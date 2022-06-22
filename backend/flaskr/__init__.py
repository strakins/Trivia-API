from msilib import CAB
import os
from tkinter.messagebox import QUESTION
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

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
  cors = CORS(app, resources={r'/api/*': {'origins': '*'}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response): 
    response.headers.add('Access-control-Headers', 'Content-Type,Authorization,True')
    response.headers.add('Access-control-Methods', 'GET,PUT,DELETE,OPTIONS')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_all_categories():
    # categories_list = Category.query.order_by(Category.id).all()
    categories_list = Category.query.order_by(Category.id).all()

    if len(categories_list) == 0:
      abort(404)
    return jsonify({
      'success': True,
      'categories': {category.id: category.type for category in categories_list}
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_list_all_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)

    categories_list = Category.query.order_by(Category.id).all()

    if len(current_questions) == 0:
        abort(404)
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'categories': {category.id: category.type for category in categories_list}
    })


    
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question_to_be_dlt = Question.query.filter(Question.id == question_id).one_or_none()

    if question_to_be_dlt is None:
      abort(404)
    question_to_be_dlt.delete()
    questions_list = Question.query.all()
    current_questions = paginate_questions(request, questions_list)

    return jsonify({
      'success': True,
      'deleted': question_id,
      'questions': current_questions,
      'total_questions': len(Question.query.all())
    })
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_new_question():
      body = request.get_json()

      new_question = body.get('question', None)
      new_answer = body.get('answer', None)
      new_category = body.get('category', None)
      new_difficulty = body.get('difficulty', None)
    
      try: 
        question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty )
        question.insert()

        selection = Question.query.order_by(Question.id).all()
        current_questions  = paginate_questions(request, selection)

        return jsonify({
          'success': True,
          'created': question.id,
          'questions': current_questions,
          'total_questions': len(Question.query.all())
        })
      except:
        abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
      body = request.get_json()
      search_input = body.get('searchTerm', None)
      if search_input:
          selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search_input)))
          current_questions = paginate_questions(request, selection)
          print(current_questions)
          return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection.all())
          })
      else: 
        abort(404)
      

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_category(category_id):
    category_list = Category.query.get(category_id)
    page = 1
    if request.args.get('page'):
      page = int(request.args.get('page'))
    categories = list(map(Category.format, Category.query.all()))
    questions_query = Question.query.filter_by(
      category = category_id).paginate(
        page, QUESTIONS_PER_PAGE, False)
    questions = list(map(Question.format, questions_query.items))
    if questions == 0:
      abort(404)
    return jsonify({
      'success': True,
      'questions': questions,
      'total_questions': questions_query.total,
      'categories': categories,
      'current_category': Category.format(category_list)
    })
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def choose_quiz():
    try:
      body = request.get_json()

      category = body.get('quiz_category', None)
      previous_questions = body.get('previous_questions', None)

      if category['id'] == 0:
        available_quizzes = Question.query.filter(Question.id.notin_(previous_questions)).all()
      else:
        available_quizzes = Question.query.filter(
          Question.category == str(category['id'])
        ).filter(Question.id.notin_(previous_questions)
        ).all()
      if len(available_quizzes) == 0:
        abort(404)
      else:
        random_question = random.choice(available_quizzes)
        return jsonify({
          'success': True,
          'question': random_question.format()
        })
    except:
      abort(404)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def page_not_found(error):
      return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
      })

  @app.errorhandler(405)
  def method_not_allowed(error):
      return jsonify({
        'success': False,
        'error': 405,
        'message': 'method not allowed'
      })

  @app.errorhandler(422)
  def request_unprocessable(error):
      return jsonify({
        'success': False,
        'error': 422,
        'message': 'request can not be processed'
      })

  @app.errorhandler(500)
  def server_errro(error):
      return jsonify({
        'success': False,
        'error': 500,
        'message': 'internal server error'
      })


  return app

    