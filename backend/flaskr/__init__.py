import sys
import babel
import os
from flask import (
    Flask,
    request,
    abort,
    jsonify,
    render_template,
    flash
)
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_paginate import Pagination, get_page_args
import random
from .models import (
    setup_db,
    Question,
    Category,
    db
)
from typing import List
from functools import reduce

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    app.config.from_envvar('FLASK_CONFIG')

    # CORS(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/')
    def index():
        return 'Web App with Python Flask!'

    '''
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
    @app.route('/categories', methods=['GET'])
    def get_categories():
        result = categories_dao()
        return jsonify(categories=result)

    def categories_dao():
        result: List[Category] = Category.query.all()
        raw_categories = [i.format() for i in result]
        result = {i['id']: i['type'] for i in raw_categories}
        return result
    '''
  Create an endpoint to handle GET requests for questions, 
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
        page, per_page, offset = get_page_args(page_parameter='page',
                                               per_page_parameter='per_page')
        result = Question.query.order_by(Question.id.desc()).paginate(
            page, per_page, error_out=False)

        questions = [i.format() for i in result.items]
        result = {
            'questions': questions,
            'totalQuestions': result.total,
            'categories': categories_dao(),
            'currentCategory': result.total
        }
        return jsonify(result)
    '''
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            Question.query.filter_by(id=question_id).delete()
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return jsonify({'success': True})

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
    def create_question():
        try:
            input = request.json
            print(input)
            question = Question(
                input['question'],
                input['answer'],
                input['difficulty'],
                input['category']
            )

            db.session.add(question)
            db.session.commit()
            flash('Question was successfully added!')
        except:
            db.session.rollback()
            flash('An error occurred. Question could not be listed.', 'error')
            print(sys.exc_info())
        finally:
            db.session.close()
        return jsonify({'success': True})

    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

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

    '''
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
    @app.errorhandler(401)
    def unauthorized__error(error):
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def no_permission_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return render_template('errors/422.html'), 422

    @app.errorhandler(500)
    def server_error(error):
        return render_template('errors/500.html'), 500

    return app
