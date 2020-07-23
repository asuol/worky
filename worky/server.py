"""
MIT License

Copyright (c) 2020 André Lousa Marques <andre.lousa.marques at gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from flask import Flask, request, redirect
from flask.templating import render_template
from datetime import datetime, timedelta
from worky.models.index_model import IndexModel
from worky.models.completed_model import CompletedModel
from worky.models.create_task_model import CreateTaskModel
from worky.models.update_task_model import UpdateTaskModel
from worky.models.confirm_form_model import ConfirmFormModel
from worky.storage import Storage
from waitress import serve

app = Flask(__name__)


def run(db, host, port):
    app.config['STORAGE'] = Storage(db)
    serve(app, host=host, port=port)


@app.route('/')
def index():
    storage = app.config['STORAGE']

    overdue_tasks = storage.get_overdue_tasks()
    active_tasks = storage.get_active_tasks()

    index_model = IndexModel(active_tasks, overdue_tasks)

    return render_template("index.html", model=index_model)


@app.route('/createForm')
def create_form():

    default_due_date = datetime.utcnow() + timedelta(weeks=2)
    default_due_date = datetime.strftime(default_due_date, '%Y-%m-%d')

    create_task_model = CreateTaskModel("/createTask", default_due_date)

    return render_template("createTask.html", model=create_task_model)


@app.route('/createTask')
def create_task():
    storage = app.config['STORAGE']

    description = request.args.get('description')
    due_date = request.args.get('dueDate')

    storage.create_task(description, due_date)

    return redirect("/", code=302)


@app.route('/updateForm')
def update_form():
    storage = app.config['STORAGE']

    task_id = request.args.get('id')

    task = storage.get_task(task_id)

    update_task_model = UpdateTaskModel("/updateTask", task.due_date, task)

    return render_template("updateTask.html", model=update_task_model)


@app.route('/updateTask')
def update_task():
    storage = app.config['STORAGE']

    task_id = request.args.get('id')
    description = request.args.get('description')
    due_date = request.args.get('dueDate')

    storage.update_task(task_id, description, due_date)

    return redirect("/", code=302)


@app.route('/deleteForm')
def delete_form():
    storage = app.config['STORAGE']

    task_id = request.args.get('id')

    task = storage.get_task(task_id)
    action = "Delete"
    form_action = "/deleteTask"

    confirm_model = ConfirmFormModel(form_action, task.due_date, task, action)

    return render_template("confirmForm.html", model=confirm_model)


@app.route('/deleteTask')
def delete_task():
    storage = app.config['STORAGE']

    task_id = request.args.get('id')

    storage.delete_task(task_id)

    return redirect("/", code=302)


@app.route('/completeForm')
def complete_form():
    storage = app.config['STORAGE']

    task_id = request.args.get('id')

    task = storage.get_task(task_id)
    action = "Complete"
    form_action = "/completeTask"

    confirm_model = ConfirmFormModel(form_action, task.due_date, task, action)

    return render_template("confirmForm.html", model=confirm_model)


@app.route('/completeTask')
def complete_task():
    storage = app.config['STORAGE']

    task_id = request.args.get('id')

    storage.complete_task(task_id)

    return redirect("/", code=302)


@app.route('/completed')
def completed():
    storage = app.config['STORAGE']

    completed_tasks = storage.get_completed_tasks()

    completed_model = CompletedModel(completed_tasks)

    return render_template("completed.html", model=completed_model)
