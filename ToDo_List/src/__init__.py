from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():

    app=Flask(__name__)

    # app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///todo.sqlite'
    app.config['SQLALCHEMY_DATABASE_URI']= \
        'postgresql://postgres:1234567890@localhost:5432/todo'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False

    db.init_app(app)

    with app.app_context():
        from . import models
        db.create_all()

    app.app_context().push()

    from src import routes

    app.register_blueprint(routes.todo_list_api)

    return app
