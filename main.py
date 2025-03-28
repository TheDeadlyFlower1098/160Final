from flask import Flask, render_template, request
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash 

app = Flask(__name__) 

con_str = "mysql://root:cset155@localhost/testing"
engine = create_engine(con_str, echo=True)
conn = engine.connect() 

# Home route - displays the home page
@app.route('/')
def home():
    return render_template('home.html')

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

@app.route('/accounts', methods=['GET', 'POST'])
def accounts():
    # Handle the filtering logic
    role_filter = request.args.get('role', 'All')  # Get role filter from query parameters
    if role_filter == 'Teacher':
        query = text("SELECT * FROM user WHERE role = 'Teacher'")
    elif role_filter == 'Student':
        query = text("SELECT * FROM user WHERE role = 'Student'")
    else:
        query = text("SELECT * FROM user")  # Default: show all users

    # Execute the query
    result = conn.execute(query)
    users = result.fetchall()  # Get all rows from the query

    return render_template('accounts.html', users=users, role_filter=role_filter)

@app.route('/create_test', methods=['GET'])
def create_test():
    # Fetch teachers from the database to associate with the test
    result = conn.execute(text("SELECT * FROM teacher"))
    teachers = result.fetchall()
    return render_template('create_test.html', teachers=teachers)

@app.route('/create_test', methods=['POST'])
def add_test():
    try:
        test_name = request.form['test_name']
        teacher_id = request.form['teacher_id']
        questions = request.form.getlist('questions')  # Get a list of questions

        # Insert the test into the database
        result = conn.execute(
            text('INSERT INTO test (name, teacher_id) VALUES (:test_name, :teacher_id)'),
            {'test_name': test_name, 'teacher_id': teacher_id}
        )
        conn.commit()

        # Fetch the test_id of the newly created test
        test_id = conn.execute(text('SELECT LAST_INSERT_ID()')).fetchone()[0]

        # Insert questions into the database
        for question_text in questions:
            if question_text.strip():  # Ensure no empty questions
                conn.execute(
                    text('INSERT INTO question (test_id, question_text) VALUES (:test_id, :question_text)'),
                    {'test_id': test_id, 'question_text': question_text}
                )

        conn.commit()

        return render_template('create_test.html', success='Test created successfully!', teachers=teachers)

    except Exception as e:
        return render_template('create_test.html', error="Failed to create test", teachers=teachers)


# Run the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)