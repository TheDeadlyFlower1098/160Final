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
    # Fetch only users with the role 'Teacher'
    result = conn.execute(text("SELECT user_id, name FROM user WHERE role = 'Teacher'"))
    teachers = result.fetchall()
    return render_template('create_test.html', teachers=teachers)

@app.route('/create_test', methods=['POST'])
def add_test():
    try:
        test_name = request.form['test_name']
        teacher_id = request.form['teacher_id']
        questions = request.form.getlist('questions')  # Get the list of questions
        answers = request.form.getlist('answers')  # Get the list of correct answers

        # Insert the test into the database
        result = conn.execute(
            text('INSERT INTO test (name, teacher_id) VALUES (:test_name, :teacher_id)'),
            {'test_name': test_name, 'teacher_id': teacher_id}
        )
        conn.commit()

        # Fetch the test_id of the newly created test
        test_id = conn.execute(text('SELECT LAST_INSERT_ID()')).fetchone()[0]

        # Insert questions and correct answers into the database
        for i in range(len(questions)):
            question_text = questions[i].strip()
            correct_answer = answers[i].strip()
            if question_text:
                conn.execute(
                    text('INSERT INTO question (test_id, question_text) VALUES (:test_id, :question_text)'),
                    {'test_id': test_id, 'question_text': question_text}
                )
                question_id = conn.execute(text('SELECT LAST_INSERT_ID()')).fetchone()[0]

                # Store the correct answer in the Answer table
                conn.execute(
                    text('INSERT INTO Answer (question_id, answer_text) VALUES (:question_id, :answer_text)'),
                    {'question_id': question_id, 'answer_text': correct_answer}
                )

        conn.commit()
        # Fetch teachers again so they are available in the template
        result = conn.execute(text("SELECT user_id, name FROM user WHERE role = 'Teacher'"))
        teachers = result.fetchall()

        return render_template('create_test.html', success='Test created successfully!', teachers=teachers)

    except Exception as e:
        result = conn.execute(text("SELECT user_id, name FROM user WHERE role = 'Teacher'"))
        teachers = result.fetchall()

        return render_template('create_test.html', error="Failed to create test", teachers=teachers)


# Run the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)