from flask import Flask, render_template, request, session
import requests
from replit import db
import os

app = Flask(__name__)

app.secret_key = os.environ['flask_secret_key']

app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True

if 'total_dogs_generated' not in db:
  db['total_dogs_generated'] = 0

if 'last_dog' not in db:
  db['last_dog'] = ''

if 'users' not in db:
  db['users'] = []

@app.route('/', methods=['GET', 'POST'])
def home():
  if request.method == 'POST':
    print('You clicked the Login/Signup button!')
    user_name = request.form['user_name']
    session['user'] = user_name
    user = create_or_update_user(user_name)
  else:
    user = None
    
  return render_template('index.html',
                        dogs_generated=db['total_dogs_generated'],
                        dog_image=db['last_dog'],
                        users=enumerate(get_leaderboard(db['users'])),
                        user=user)

@app.route('/get_dog')
def get_dog():
  response = requests.get('https://dog.ceo/api/breeds/image/random')

  data = response.json()

  dog_image = data['message']

  print(db['total_dogs_generated'])

  db['last_dog'] = dog_image

  if session['user']:
    user = get_user_from_database(session['user'])
    user['dogs_generated'] += 1

  db['total_dogs_generated'] += 1
  return render_template('index.html',
                        dog_image=dog_image,
                        user=user,
                        users=enumerate(get_leaderboard(db['users'])),
                        dogs_generated=db['total_dogs_generated'])


@app.route('/logout')
def logout():
  session['user'] = None
  return render_template('index.html',
                        dogs_generated=db['total_dogs_generated'])


def create_or_update_user(user_name):
  user = get_user_from_database(user_name)

  if user:
    print('USER ALREADY EXISTS')
    user['logins'] += 1
    print(user)
      

  else:
    # new user
    print('NEW USER 🎉!')
    db['users'].append({
      'user_name': user_name,
      'logins': 1,
      'dogs_generated': 0
    })
    user = get_user_from_database(user_name)
    
  return user

# DRY - DO-NOT REPEAT YOURSELF

def get_user_from_database(user_name):
   user = [user for user in db['users'] if user['user_name'] == user_name]
   return user[0] if user else None

def get_leaderboard(users):
  return sorted(db['users'], key=lambda user: user['dogs_generated'], reverse=True)

@app.template_filter()
def trophy_or_position(index):
  return '1 🏆' if index == 0 else index + 1
  

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=81)