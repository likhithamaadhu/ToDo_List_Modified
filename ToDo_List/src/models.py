from dataclasses import dataclass
from src import db
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# @dataclass
class Todo(db.Model):
    #__tablename__="toDo"

    id=db.Column(db.Integer, primary_key=True)
    task = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date, default=datetime.now)
    complete = db.Column(db.Boolean,default=False)

    def __init__(self, task, due_date, complete):
        self.task = task
        self.due_date = due_date
        self.complete = complete

    def to_dict(self, rows):
        output = []
        for row in rows:
            output.append({"task" : row.task, "due_date" : str(row.due_date), "complete" : row.complete})
        return output
    # {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

    def __repr__(self):

        return  "{} - {} - {}".format(self.task, self.due_date, self.complete)
    # "{} - {} - {}".format(self.task, self.due_date, self.complete)

    # def __dict__(self):
    #     return  {'task': self.task, 'due_date':self.due_date, 'complete': self.complete}
    
