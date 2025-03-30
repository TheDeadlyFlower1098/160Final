from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__) 

con_str = "mysql://root:cset155@localhost/testing"
engine = create_engine(con_str, echo=True)
conn = engine.connect() 

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/accounts', methods=['GET'])
def accounts():
    role_filter = request.args.get('role', 'All')
    
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
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        user_id = request.form['user_id'] 
        role = request.form['role']
        
        if not name or not email or not password or not user_id or not role:
            return render_template('signup.html', error="All fields are required", success=None)
        
        print(f"Inserting user data: {name}, {email}, {user_id}, {role}")
        
        conn.execute(
            text('INSERT INTO user (name, email, password, user_id, role) VALUES (:name, :email, :password, :user_id, :role)'),
            {'name': name, 'email': email, 'password': password, 'user_id': user_id, 'role': role}
        )
        conn.commit()

        return render_template('signup.html', error=None, success='Signup successful')

    except Exception as e:
        print(f"Error occurred during signup: {e}")
        return render_template('signup.html', error=f"Signup failed: {e}", success=None)

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

        # Fetch teachers again for the POST response (to pass them to the template)
        result = conn.execute(
            text("SELECT teacher.teacher_id, user.name FROM teacher INNER JOIN user ON teacher.teacher_id = user.user_id"))
        teachers = result.fetchall()

        return render_template('create_test.html', success='Test created successfully!', teachers=teachers)

    except Exception as e:
        result = conn.execute(text("SELECT user_id, name FROM user WHERE role = 'Teacher'"))
        teachers = result.fetchall()
        return render_template('create_test.html', error="Failed to create test", teachers=teachers)
    

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_user():
    try:
        email = request.form['email']
        password = request.form['password']

        print(f"Received email: '{email}'")
        print(f"Received password: '{password}'")

        result = conn.execute(
            text('SELECT * FROM user WHERE email = :email'),
            {'email': email}
        ).fetchone()

        print(f"Query result: {result}")

        if result:
            stored_password = result[3]
            print(f"Stored password: '{stored_password}'")

            if stored_password.strip() == password.strip():
                print("Login successful")
                return render_template('home.html')
            else:
                print("Password mismatch")
                return render_template('login.html', error="Invalid password", success=None)
        else:
            print("User not found")
            return render_template('login.html', error="User not found", success=None)

    except Exception as e:
        print(f"Error occurred during login: {e}")
        return render_template('login.html', error="Login failed. Please try again.", success=None)

# Run the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)