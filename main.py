from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash 

app = Flask(__name__) 
app.secret_key = "your_secret_key"  # Needed for flash messages

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

# Route to start a test
@app.route('/take_test/<int:test_id>', methods=['GET', 'POST'])
def take_test(test_id):
    # Get student_id (assuming session or login, for now, we use a test user)
    student_id = 3  # You should replace this with actual logged-in student's ID

    # Fetch the test details
    test_result = conn.execute(text("SELECT name FROM test WHERE test_id = :test_id"), {'test_id': test_id})
    test = test_result.fetchone()
    if not test:
        return "Test not found", 404

    # Fetch all questions for the test
    question_result = conn.execute(text("SELECT question_id, question_text FROM question WHERE test_id = :test_id"), {'test_id': test_id})
    questions = question_result.fetchall()

    if request.method == 'POST':
        # Get all answers from the form
        answers = request.form.getlist('answers')

        for i, question in enumerate(questions):
            question_id = question[0]
            answer_text = answers[i].strip() if answers[i].strip() else None  # Store NULL if unanswered

            conn.execute(
                text('INSERT INTO Answer (student_test_id, question_id, answer_text) VALUES (:student_test_id, :question_id, :answer_text)'),
                {'student_test_id': student_id, 'question_id': question_id, 'answer_text': answer_text}
            )

        conn.commit()
        flash("Test submitted successfully!", "success")
        return redirect(url_for('home'))

    return render_template('take_test.html', test=test, questions=questions, test_id=test_id)


# Run the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)