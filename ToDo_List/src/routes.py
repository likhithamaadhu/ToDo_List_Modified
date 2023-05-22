# import app, db
from datetime import timezone, datetime 
from dateutil import parser as dparser
from flask import Blueprint, request
from src.models import Todo
from src import db
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy import insert

todo_list_api = Blueprint("todo_list_api", __name__, url_prefix="/api/todo_list")

class ToDoException(Exception):
    def __init__(self, message, code=400):
        self.message = message
        self.code = code


# --------------------ToDo LIST APIs----------------------

@todo_list_api.route('/',  methods=['GET'])
@todo_list_api.route('/<task_id>',  methods=['GET'])
def get_task_list(task_id=None):
    """
    To list tasks.
    Payload:
        task: str
        due_date: date
    """
    to_do=Todo.query
    
    if task_id:
        to_do = to_do.filter_by(id=task_id).first()
        # print(str(task_list))

        if not to_do:
            return {"error":"Tasks not found"}, 404
        
        record = {"id" : to_do.id,
                    "task" : to_do.task, 
                    "due_date" : str(to_do.due_date), 
                    "complete" : to_do.complete}
        
        return {
            "success": True,
            "task_list": record,
            "message": "tasks retrieved sucessfully.",
            }, 200
    
    args = request.args

    sort = args.get('sort','task')
    order = args.get('order','asc')
    search =  args.get("search")
    # search_by = args.get("search_by",'task')
    limit = args.get("limit", 10, type=int)
    page_num = args.get("page", 1, type=int)
    due_date = args.get('due_date')
    is_complete = args.get('is_complete', 'false') #Defaults to incomplete tasks

    # print(is_complete, type(is_complete))
    try:

        if order not in ("asc", "desc"):
            raise ValueError("Invalid order by argument, only allowed 'asc', 'desc'")
        
        if is_complete not in ("true", "false"):
            raise ValueError("Invalid is_complete argument, only allowed 'true', 'false'")
        
        if sort not in ('id','task','due_date'):
            raise ValueError("Invalid sort argument, only allowed 'id','task','due_date'")

        if is_complete=="false": #List pending tasks only
            to_do = to_do.filter(Todo.complete == False)

        if search:
            to_do = to_do.filter(Todo.task.ilike(f"%{search}%"))

        if due_date: #Get all the tasks for a given date
            date = dparser.parse(due_date).date()
            to_do = to_do.filter(Todo.due_date == date)
        
        #Sorting Data based on given colum in given order
        to_do = to_do.order_by(getattr(getattr(Todo, sort), order)())
        # print(page_num, limit)
        to_do = to_do.paginate(page=page_num, 
                                per_page=limit, error_out=False)

        now = datetime.now(timezone.utc)

        # print(to_do.items)
        task_list = [{"id" : i.id,
                    "task" : i.task, 
                    "due_date" : str(i.due_date), 
                    "complete" : i.complete} 
                    for i in to_do.items]

        data = dict(
            Tasks=task_list,
            total=to_do.total,
            current_page=to_do.page,
            per_page=to_do.per_page,
            timestamp=str(now)
        )

    except Exception as error:
        return {"error": str(error)}, 404

    return (
    {
        "success": True,
        "task_list": data,
        "timestamp": now,
        "message": "tasks retrieved sucessfully.",
    },
    200,
    )
    
    
@todo_list_api.route('/bulk_add', methods=['POST'])
def add_task():
    """
    To add tasks.
    Payload:
        task: str
        due_date: date
    """
    task_list = request.json
    task_list = task_list.get('data')

    if not task_list:
        return {'error': 'data not found'}, 404

    # print(task_data)
    # task_list = []
    # for record in task_data:
    #     task = record.get('task')
    #     due_date =  record.get('due_date')  

    #     print(task, due_date)

    #     if not task or not due_date:
    #         return {
    #             "error" : "Invalid data"
    #         }, 404
        
    #     due_date =dparser.parse(due_date).date()

    #     task_list.append(Todo(task=task, 
    #                     due_date=due_date,
    #                     complete=False))

    try:
        # db.session.add_all(task_list)
        db.session.execute(insert(Todo), task_list)
        db.session.commit()
    except Exception as error:
        return {"error": str(error)}, 404
    
    now = datetime.now(timezone.utc)

    return {
            "success": True,
            "timestamp": now,
            "message": "Task(s) added sucessfully.",
            }, 200


@todo_list_api.route('/bulk_update',methods=['PUT'])
@todo_list_api.route('/<task_id>',methods=['PUT'])
def edit_task(task_id=None):
    """
    To update tasks.
    Payload:
        task: str
        due_date: date
    """
    # task = request.json.get("task")
    # due_date = request.json.get("due_date")
    # complete= request.json.get("complete")

    if task_id:
        record= request.json
        record["id"]=task_id
        # print(record,type(record))
        data =[record]
        # print(data)

    else:
        data = request.json.get('data')
    

    if not data:
        return {'error': 'Data not found'}, 404
    
    try:
        query = upsert(Todo).values(data)
        # print(str(query))
        query = query.on_conflict_do_update(
                        index_elements=[Todo.id], 
                        set_=dict(task=query.excluded.task,
                                due_date=query.excluded.due_date,
                                complete=query.excluded.complete))
        
        # print(str(query))
        
        db.session.execute(query)
        db.session.commit()
    except Exception as error:
        return {'error': str(error)}, 404

    return {
            "success": True,
            "message": "Task(s) updated sucessfully.",
            }, 200


@todo_list_api.route('/bulk_delete',methods=['DELETE'])
@todo_list_api.route('/<task_id>',methods=['DELETE'])
def delete_task(task_id=None):
    """
    To delete tasks.
    Payload:
        id : integer
    """

    if task_id:
        task=Todo.query.filter_by(id=task_id).first()

        if not task:
            return {"error":"Task not found"}, 404
        
        db.session.delete(task)
        db.session.commit()

        return{
            "success":True,
            "message":"task deleted successfully"
        }, 200

    id_list = request.json.get('data')

    if not id_list:
        return {'error': 'Data not found'}, 404
    
    task_list = Todo.query.filter(Todo.id.in_(id_list))

    count = task_list.count()

    if not count:
        return {"Error":"data not found"}, 404

    task_list.delete()
    db.session.commit()

    return {
            "success": True,
            "message": f"Deleted {count} tasks",
            }, 200
    

