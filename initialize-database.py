import pymongo
import datetime
import os
from dotenv import load_dotenv

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

#adds roles
def add_role(role_name):
    role_data = {
        'role_name': role_name
    }
    return roles.insert_one(role_data)

#adds user
def add_user(first_name, last_name, email, password, role):
    user_data = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': password,
        'role': role,
        'date_added': datetime.datetime.now(),
        'date_modified': datetime.datetime.now()
    }
    return users.insert_one(user_data)

#adds when an employee is available
#the user_id input corresponds with IDs in the users field
def add_employee_availability(user_id, day_available, time_slot)
    availablility_data = {
        'user_id': user_id,
        'day_available': day_available,
        'time_slot': time_slot
    }
    return employee_availability.insert_one(availablility_data)

#adds a schedule slot
#needs to addend user ids to list as they schedule
def add_schedule(user_list, day_available, time_slot)
    schedule_data = {
        'user_list': user_list,
        'day_available': day_available,
        'time_slot': time_slot
    }
    return schedule.insert_one(schedule_data)

def init_db():
    #add roles
    admin = add_role('admin')
    scheduler = add_role('scheduler')
    user = add_role('user')

    #add users
    admin = add_user('Aidan', 'Gorny', 'aidan-gorny@uiowa.edu', 'abc123', 'admin')
    scheduler = add_user('Meredith', 'Grey', 'meredith-grey@uiowa.edu', 'abc123', 'scheduler')
    user1 = add_user('Christina', 'Yang', 'christina-yang@uiowa.edu', 'abc123', 'user')
    user2 = add_user('Alex', 'Karev', 'alex-karev@uiowa.edu', 'abc123', 'user')

    #add availability
    #add alex userID??
    alex_monday1 = add_employee_availability(users['_id'], 'Monday', '1100')
    alex_monday2 = add_employee_availability(users['_id'], 'Monday', '1200')
    alex_monday3 = add_employee_availability(users['_id'], 'Monday', '1300')
    christina_monday1 = add_employee_availability(users['_id'], 'Monday', '1100')

    #add schedule time
    monday1 = add_schedule(['AlexID', 'ChristinaID'], 'Monday', '1100')

def main()
    init_db()

main()
