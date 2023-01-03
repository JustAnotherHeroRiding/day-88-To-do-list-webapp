#Let's make this To-Do website project a little harder by not using bootstrap

#I will use tailwind for all elements and styling 

#What i need to do is add some sort of banner or box up top for saving lists,
# getting the date at the top

#A writing area for tasks

#After entering text it should show up as a task with a checkbox and a delete button
#add a color picker and star to each task
#Delete button should ask to confirm
#If i click the checkbox it should go away
#If there are other tasks remaining it should show the completed tasks
#Crossed out,if not it should clear the screen and say that i am done
#Allow the tasks to be moved
#So it basically 2 sections,one for current tasks and one for completed tasks


#https://flask.io/nrpuwkn2UzuU Inspo


# npx tailwindcss -i ./src/input.css -o ./static/dist/output.css --watch
#To make the css update
from flask import Flask, jsonify, render_template, request,redirect,url_for,flash,abort
from flask_sqlalchemy import SQLAlchemy
from random import choice
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm,RegisterForm,TodoForm,EditTodoForm
import dotenv,os
dotenv.load_dotenv()


os.getenv("APIKEY")
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("APIKEY") #'8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

login_manager = LoginManager()
login_manager.init_app(app)


##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String, unique = True)
    password = db.Column(db.String)
    tasks = db.relationship('Task', backref='owner')


    def __repr__(self):
        return f'User{self.first_name}{self.email}'



class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(255))
    due_date = db.Column(db.DateTime())
    status = db.Column(db.String(255))
    todo_owner = db.Column(db.Integer,db.ForeignKey('user.id'))


    def __repr__(self):
        return f'Task{self.task_name}{self.due_date}'
    
#with app.app_context():
    #db.create_all()
    
    
    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
    
    

with open('tasks.txt') as f:
    tasks = f.readlines()
deleted_tasks = []


@app.route("/", methods=["GET", "POST"])
def home_page():
    global tasks
    now = datetime.datetime.now().strftime("%d/%m/%Y")
    form = TodoForm()
    if request.method == 'POST':
        user = current_user
        if form.validate_on_submit:
            todo = Task(task_name =form.task_name.data,status =form.status.data,
                        due_date =form.due_date.data, todo_owner = user.id
                       )
            db.session.add(todo)
            db.session.commit()
            return redirect(url_for('home_page'))
    if current_user.is_authenticated:
        tasks = Task.query.filter_by(todo_owner = current_user.id)
    else:
        tasks = []
    

    with open('removed_items.txt') as f:
        deleted_tasks = f.readlines()
    return render_template("index.html", date = now, tasks = tasks, deleted=deleted_tasks, form=form)

@app.route('/remove-item', methods=["POST"])
def remove_item():
    global deleted_tasks
    content_type = request.headers.get('Content-Type')
    print(content_type)
    print(request.form)
    if (content_type == 'application/json'):
        data = request.get_json()
        item = data['item']
        now = datetime.datetime.now().strftime("%d/%m/%Y")
        if item != '':
            with open('removed_items.txt', 'a') as f:
                f.write(item + ','+now+'\n')
            with open('removed_items.txt') as f:
                deleted_tasks = f.readlines()
                return redirect(url_for('home_page'))
    else:
        return "Content type is not supported."
    
@app.route('/register', methods = ['POST','GET'])
def register():
    form = RegisterForm()
    if request.method == 'GET':
        return render_template('register.html', form=form)

    if request.method == 'POST':
            user = User(first_name =form.first_name.data,
                        last_name =form.last_name.data,
                        email =form.email.data,
                        password = generate_password_hash(form.password.data)
                        )
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
        
@app.route('/login', methods = ['POST','GET'])
def login():
        form = LoginForm()
        if form.validate_on_submit:
            user = User.query.filter_by(email = form.email.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home_page'))
            flash("Invalid details")
               
        return render_template('login.html', form=form)
    
    

@app.route('/edit_task/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    user = current_user
    form = EditTodoForm()
    task = Task.query.filter_by(id =id,todo_owner = current_user.id).first()
    
    if form.validate_on_submit():
        task.task_name = form.task_name.data
        task.due_date = form.due_date.data
        task.status = form.status.data
        db.session.commit()
        return redirect(url_for('home_page'))
        
    elif request.method == 'GET':
        form.task_name.data = task.task_name
        form.due_date.data = task.due_date
        form.status.data = task.status
    return render_template('edit_todo.html',form=form)

@app.route('/mark-complete/<int:id>', methods=['GET','POST'])
def complete(id):
    task = Task.query.filter_by(id =id,todo_owner = current_user.id).first()
    if task:
        task.status = "Complete"
        db.session.commit()
        return redirect(url_for('home_page'))
    else:
        abort(404)



@app.route('/delete_task/<int:id>', methods=['GET','POST'])
def delete(id):
    task = Task.query.filter_by(id =id,todo_owner = current_user.id).first()
    if task:
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for('home_page'))
    else:
        abort(404)
        


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have successfully logged yourself out.')
    return redirect(url_for('home_page'))

if __name__ == '__main__':
    app.run(debug=True)
