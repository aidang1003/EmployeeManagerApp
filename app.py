import os
from dotenv import load_dotenv
import pymongo
import datetime
from bson.objectid import ObjectId
from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
import bcrypt
from functools import wraps

app = Flask(__name__)
'''
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

## necessary for python-dotenv ##
APP_ROOT = os.path.join(os.path.dirname(__file__), '..')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

mongo = os.getenv('MONGO')

client = pymongo.MongoClient(mongo)

db = client['EmployeeSchedulingManager']

users = db['users']
roles = db['roles']
recipes = db['employee_availability']
categories = db['schedule']

    
# Python wrappers that determine role access 
def roles_required(*role_names):
    def decorator(original_route):
        @wraps(original_route)
        def decorated_route(*args, **kwargs):
            if not current_user.is_authenticated:
                print('The user is not authenticated.')
                return redirect(url_for('login'))
            
            print(current_user.role)
            print(role_names)
            if not current_user.role in role_names:
                print('The user does not have this role.')
                return redirect(url_for('login'))
            else:
                print('The user is in this role.')
                return original_route(*args, **kwargs)
        return decorated_route
    return decorator


@login.user_loader
def load_user(username):
    u = users.find_one({"email": username})
    if not u:
        return None
    return User(username=u['email'], role=u['role'], id=u['_id'])

class User:
    def __init__(self, id, username, role):
        self._id = id
        self.username = username
        self.role = role

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username
'''


@app.route('/')
#@login_required
#@roles_required('admin', 'scheduler', 'user')
def index():
    return render_template('index.html', pageTitle='Homepage')

@app.route('/login')
#@login_required
#@roles_required('admin', 'scheduler', 'user')
def login():
    return render_template('login.html')

@app.route('/account')
#@login_required
#@roles_required('admin', 'scheduler', 'user')
def account():
    return render_template('account.html')

####### Availablility #######
@app.route('/availability')
def availability():
    return render_template('availability.html')

@app.route('availability/add-availability', methods=['GET', 'POST'])
#@login_required
#@roles_required(user)
def add_availability():
    if request.method == 'POST':
        form = request.form
        
        #find method to ensure user is not double scheduled
        if availability:
            flash("You're already scheudled for the time.", 'warning')
            return "You're already scheudled for the time."
        

        #first_name = users.find_one({"first_name": request.form['first_name']})
        new_availability = {
            'userID': form['userID'],
            'day_available': form['day_available'],
            'time_slot': form['time_slot'],
        }
        recipes.insert_one(new_availability)
        flash('availability for' + form['day_available'] + 'has been added.', 'success')
        return redirect(url_for('availability'))
    return render_template('availability.html', all_roles=roles.find(), all_users=users.find()) #modify?



######### Schedule ###########    
@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

@app.route('/schedule/tuesday')
def schedule_tuesday():
    return render_template('schedule-tuesday.html')

if __name__ == '__main__':
    app.run(debug=True)