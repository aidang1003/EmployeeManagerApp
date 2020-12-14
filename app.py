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
employee_availability = db['employee_availability']

login = LoginManager()
login.init_app(app)
login.login_view = 'login'

@login.user_loader
def load_user(email):
    u = users.find_one({"email": email})
    if not u:
        return None
    return User(email=u['email'], role=u['role'], id=u['_id'], first_name=u["first_name"], last_name=u['last_name'])

class User:
    def __init__(self, id, email, role, first_name, last_name):
        self._id = id
        self.email = email
        self.role = role
        self.first_name = first_name
        self.last_name = last_name

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
        return self.email



### custom wrap to determine role access  ### 
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


@app.route('/')
def index():
    return render_template('index.html', pageTitle='Homepage')




############# Login and Register ################
@app.route('/register')
def register():
    return 'self register for an account'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        user = users.find_one({"email": request.form['email']})
        if user and user['password'] == request.form['password']:
            user_obj = User(email=user['email'], role=user['role'], id=user['_id'], first_name=user["first_name"], last_name=user['last_name'])
            login_user(user_obj)
            next_page = request.args.get('next')

            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
                return redirect(next_page)
            flash("Logged in successfully!", category='success')
            return redirect(request.args.get("next") or url_for("index"))

        flash("Wrong email or password!", category='danger')
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('login'))

############# Account Management ################
@app.route('/account', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'scheduler', 'user')
def account():
    user = users.find_one({'_id': current_user._id})
    return render_template('account.html', all_users=users.find(), all_roles=roles.find(), user=user)

@app.route('/account/edit-user/<user_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'scheduler', 'user')
def edit_user(user_id):
    user = users.find_one({'_id': ObjectId(user_id)})
    if user:
        return render_template('edit-user.html', user=user, all_roles=roles.find())
    flash('User not found.', 'warning')
    return redirect(url_for('account'))

@app.route('/account/update-user/<user_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'scheduler', 'user')
def update_user(user_id):
    if request.method == 'POST':
        form = request.form
        print('entered')
        users.update({'_id': ObjectId(user_id)},
            {'first_name': form['first_name'],
            'last_name': form['last_name'],
            'email': form['email'],
            'password': form['password'],
            'role': form['role'],
            'date_added': form['date_added'],
            'date_modified': datetime.datetime.now()})
            
        update_user = users.find_one({'_id': ObjectId(user_id)})
        flash(update_user['email'] + ' has been updated.', 'success')
        return redirect(url_for('account'))

    return render_template('account.html', all_users=users.find(), all_roles=roles.find())





####### Availablility #######
@app.route('/availability')
def availability():
    return render_template('availability.html', all_users=users.find(), your_availability=employee_availability.find({'email': current_user.email}))

@app.route('/availability/add-availability', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'scheduler', 'user')
def add_availability():
    if request.method == 'POST':
        form = request.form
        
        email = employee_availability.find_one({"email": form['email']})
        day_available = employee_availability.find_one({"day_available": form['day_available']})
        time_slot = employee_availability.find_one({"time_slot": form['time_slot']})

        if email and day_available and time_slot:
            flash("You're already scheudled for the time.", 'warning')
            return render_template('availability.html', all_users=users.find()) 


        new_availability = {
            'email': form['email'],
            'day_available': form['day_available'],
            'time_slot': form['time_slot'],
            'date_added': datetime.datetime.now(),
            'date_modified': datetime.datetime.now()
        }
        employee_availability.insert_one(new_availability)
        flash('availability for ' + new_availability['day_available'] + ' has been added.', 'success')
        return redirect(url_for('availability'))
    return render_template('availability.html', all_users=users.find(), your_availability=employee_availability.find()) 

@app.route('/availability/delete-availability/<employee_availability_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'scheduler', 'user')
def delete_availability(employee_availability_id):
    delete_availability = employee_availability.find_one({'_id': ObjectId(employee_availability_id)})
    if delete_availability:
        
        employee_availability.delete_one(delete_availability)
        flash('availability for ' + delete_availability['day_available'] + ' has been deleted.', 'warning')
        return redirect(url_for('availability'))


######### Schedule ###########    
@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

@app.route('/schedule/tuesday')
def schedule_tuesday():
    return render_template('schedule-tuesday.html')

if __name__ == '__main__':
    app.run(debug=True)