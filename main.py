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
@app.route('/accounts', methods=['GET'])
def accounts():
    role_filter = request.args.get('role', 'All')  # Default to 'All' if no filter is applied
    
    if role_filter == 'All':
        users = conn.execute(text('SELECT * FROM user')).fetchall()
    else:
        users = conn.execute(
            text('SELECT * FROM user WHERE role = :role'),
            {'role': role_filter}
        ).fetchall()

    return render_template('accounts.html', users=users, role_filter=role_filter)


@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def create_user():
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
        
        # Log the data to make sure everything is correct
        print(f"Inserting user data: {name}, {email}, {user_id}, {role}")
        
        # Insert the new user into the database
        conn.execute(
            text('INSERT INTO user (name, email, password, user_id, role) VALUES (:name, :email, :password, :user_id, :role)'),
            {'name': name, 'email': email, 'password': password, 'user_id': user_id, 'role': role}
        )
        conn.commit()

        return render_template('signup.html', error=None, success='Signup successful')

    except Exception as e:
        # Log the error for debugging (you could log to a file for production)
        print(f"Error occurred during signup: {e}")  # Log the full error message
        return render_template('signup.html', error=f"Signup failed: {e}", success=None)


# Run the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)