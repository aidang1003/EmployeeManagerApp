from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', pageTitle='Homepage')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/account')
def account():
    return render_template('account.html')

@app.route('/availability')
def availability():
    return render_template('availability.html')
    
@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

if __name__ == '__main__':
    app.run(debug=True)