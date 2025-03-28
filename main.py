from flask import Flask, render_template, request
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash 

app = Flask(__name__) #Initialize the Flask app

# Database connection string (update credentials as needed)
# Formating: mysql://user:password@server/database
con_str = "mysql://root:cset155@localhost/testing"
engine = create_engine(con_str, echo=True)
conn = engine.connect() #creates the database engine

# Home route - displays the home page
@app.route('/')
def hello():
    return render_template('signup.html')
@app.route('/signup', methods = ['GET'])
def signup():
    return render_template('signup.html')

@app.route('/signup', methods = ['POST'])
def create_user():
    try:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        user_id = request.form['user_id']
        role = request.form['role'] 
        hashed_password = generate_password_hash(password)

        conn.execute(
            text('INSERT INTO user (name, email, password, user_id, role) VALUES (:name, :email, :password, :user_id, :role)'),
            {'name': name, 'email': email, 'password': hashed_password, 'user_id': user_id, 'role': role}
        )

        conn.commit()

        return render_template('signup.html', error=None, success='Signup successful')

    except Exception as e:
        return render_template('signup.html', error="Signup failed", success=None)


# Run the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)