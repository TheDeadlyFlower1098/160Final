from flask import Flask, render_template, request
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash 

app = Flask(__name__) 

con_str = "mysql://root:cset155@localhost/testing"
engine = create_engine(con_str, echo=True)
conn = engine.connect() 

# Home route - displays the home page
@app.route('/')
def hello():
    return render_template('base.html')
@app.route('/accounts')
def accounts():
   # Retrieve the first 10 users from the 'user' table
   users = conn.execute(text('SELECT * FROM user')).fetchall()
   return render_template('accounts.html', users=users[:10])
@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def createUser():
    try:
        # Get form data
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        user_id = request.form['user_id']  # Ensure this matches the database column
        role = request.form['role']
        
        # Check if all fields are filled out
        if not name or not email or not password or not user_id or not role:
            return render_template('signup.html', error="All fields are required", success=None)
        
        # Hash the password before storing it in the database
        # hashed_password = generate_password_hash(password)
        
        # Insert the new user into the database
        conn.execute(
            text('INSERT INTO user (name, email, password, user_id, role) VALUES (:name, :email, :password, :user_id, :role)'),
            {'name': name, 'email': email, 'password': password, 'user_id': user_id, 'role': role}
        )
        conn.commit()

        return render_template('signup.html', error=None, success='Signup successful')

    except Exception as e:

        # Log the error for debugging
        print(f"Error occurred during signup: {e}")
        return render_template('signup.html', error="Signup failed", success=None)



# Run the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)