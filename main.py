from flask import Flask, render_template, request, redirect, url_for, flash, session
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash

# Initialize Flask application
app = Flask(__name__) 

# Database connection string and engine setup
con_str = "mysql://root:cset155@localhost/testing"
engine = create_engine(con_str, echo=True)
conn = engine.connect() 

# Set a secret key for session management (ensure this is secure in production)
app.secret_key = 'your_secret_key'

# Route for the home page
@app.route('/home')
def home():
    # Check if the user is logged in, otherwise redirect to login page
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('home.html')

# Default route (also home page)
@app.route('/')
def hello():
    # Check if the user is logged in, otherwise redirect to login page
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('home.html')

# Route to view and manage user accounts
@app.route('/accounts', methods=['GET'])
def accounts():
    # Retrieve role filter and sorting preference from query parameters
    role_filter = request.args.get('role', 'All')
    sort_by = request.args.get('sort_by', 'name')  # Default sorting by name

    # Ensure the sort_by parameter is valid (either name, email, or user_id)
    if sort_by not in ['name', 'email', 'user_id']:
        sort_by = 'name'

    # Build SQL query based on role filter and sorting option
    if role_filter == 'All':
        query = text(f'SELECT * FROM user ORDER BY {sort_by}')
        users = conn.execute(query).fetchall()
    else:
        query = text(f'SELECT * FROM user WHERE role = :role ORDER BY {sort_by}')
        users = conn.execute(query, {'role': role_filter}).fetchall()

    # Render the accounts page with the filtered and sorted user data
    return render_template('accounts.html', users=users, role_filter=role_filter, sort_by=sort_by)

# Route to show the signup page
@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

# Route to handle the signup form submission
@app.route('/signup', methods=['POST'])
def create_user():
    try:
        # Extract form data (user details)
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        user_id = request.form['user_id'] 
        role = request.form['role']
        
        # Ensure all fields are filled
        if not name or not email or not password or not user_id or not role:
            return render_template('signup.html', error="All fields are required", success=None)
        
        print(f"Inserting user data: {name}, {email}, {user_id}, {role}")
        
        # Insert user into the database
        conn.execute(
            text('INSERT INTO user (name, email, password, user_id, role) VALUES (:name, :email, :password, :user_id, :role)'),
            {'name': name, 'email': email, 'password': password, 'user_id': user_id, 'role': role}
        )
        conn.commit()

        # Return a success message
        return render_template('signup.html', error=None, success='Signup successful')

    except Exception as e:
        # In case of error, print the error and show a failure message
        print(f"Error occurred during signup: {e}")
        return render_template('signup.html', error=f"Signup failed: {e}", success=None)

# Route to show the login page
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')
 
# Route to handle the login form submission
@app.route('/login', methods=['POST'])
def login_user():
    try:
        # Extract form data (email and password)
        email = request.form['email']
        password = request.form['password']

        print(f"Received email: '{email}'")
        print(f"Received password: '{password}'")

        # Check if the user exists in the database
        result = conn.execute(
            text('SELECT * FROM user WHERE email = :email'),
            {'email': email}
        ).fetchone()

        print(f"Query result: {result}")

        if result:
            # Retrieve stored password and other user details
            stored_password = result[3]
            user_id = result[0]
            name = result[1]
            role = result[4]

            print(f"Stored password: '{stored_password}'")

            # Check if the passwords match
            if stored_password.strip() == password.strip():
                print("Login successful")
                
                # Store user information in session for persistence
                session['user_id'] = user_id
                session['name'] = name
                session['email'] = email
                session['role'] = role

                # Redirect to home page after successful login
                return redirect(url_for('home'))
            else:
                # Incorrect password
                print("Password mismatch")
                return render_template('login.html', error="Invalid password", success=None)
        else:
            # User not found
            print("User not found")
            return render_template('login.html', error="User not found", success=None)

    except Exception as e:
        # In case of error, print the error and show a failure message
        print(f"Error occurred during login: {e}")
        return render_template('login.html', error="Login failed. Please try again.", success=None)

# Route to handle user logout (clear session data)
@app.route('/logout')
def logout():
    session.clear()  # Clears all session data
    return redirect(url_for('login_page'))  # Redirect to login page

# Route to show the page for creating a test
@app.route('/create_test', methods=['GET'])
def create_test():
    try:
        # Fetch all users with the role of Teacher
        result = conn.execute(
            text("SELECT user_id AS teacher_id, name FROM user WHERE role = 'Teacher'")
        )
        teachers = result.fetchall()
        return render_template('create_test.html', teachers=teachers)
    
    except Exception as e:
        # In case of error, print the error and show a failure message
        print(f"Error fetching teachers: {e}")
        return render_template('create_test.html', error="Failed to load teachers.")

# Route to handle the creation of a test (POST request)
@app.route('/create_test', methods=['POST'])
def add_test():
    try:
        # Extract form data (test details)
        test_name = request.form['test_name']
        teacher_id = request.form['teacher_id']
        questions = request.form.getlist('questions')  # Get a list of questions
        
        # Insert test into the database
        conn.execute(
            text('INSERT INTO test (name, teacher_id) VALUES (:test_name, :teacher_id)'),
            {'test_name': test_name, 'teacher_id': teacher_id}
        )
        conn.commit()

        # Get the ID of the inserted test
        test_id = conn.execute(text('SELECT LAST_INSERT_ID()')).fetchone()[0]

        # Insert questions associated with the test into the database
        for question_text in questions:
            if question_text.strip():
                conn.execute(
                    text('INSERT INTO question (test_id, question_text) VALUES (:test_id, :question_text)'),
                    {'test_id': test_id, 'question_text': question_text.strip()}
                )

        conn.commit()

        # Fetch teacher list again to repopulate the dropdown
        result = conn.execute(
            text("SELECT user_id AS teacher_id, name FROM user WHERE role = 'Teacher'")
        )
        teachers = result.fetchall()

        # Return a success message
        return render_template('create_test.html', success='Test created successfully!', teachers=teachers)

    except Exception as e:
        # In case of error, rollback the transaction and show a failure message
        conn.rollback()
        print(f"Error occurred while creating test: {e}")
        result = conn.execute(
            text("SELECT user_id AS teacher_id, name FROM user WHERE role = 'Teacher'")
        )
        teachers = result.fetchall()
        return render_template('create_test.html', error="Failed to create test", teachers=teachers)

# Route to view all tests (pagination can be implemented here)
@app.route('/test')
def test():
   # Fetch the first 10 tests
   tests = conn.execute(text('SELECT * FROM test')).all()
   return render_template('test.html', tests = tests[:10])

# Route to delete a test by its ID
@app.route('/deleteTest/<int:test_id>', methods=['POST'])
def delete_test(test_id):
    try:
        # Delete all questions associated with the test
        conn.execute(
            text('DELETE FROM question WHERE test_id = :test_id'),
            {'test_id': test_id}
        )
        # Delete the test itself
        conn.execute(
            text('DELETE FROM test WHERE test_id = :test_id'),
            {'test_id': test_id}
        )
        conn.commit()
        return redirect(url_for('test', success='Test deleted successfully'))
    
    except Exception as e:
        # In case of error, rollback and show failure message
        conn.rollback()
        print(f"Error occurred while deleting test: {e}")
        return redirect(url_for('test', error="Failed to delete test"))
    
# Route to show the page for updating a test
@app.route('/updateTest/<int:test_id>', methods=['GET'])
def update_test_page(test_id):
    test = conn.execute(
        text("SELECT * FROM test WHERE test_id = :test_id"),
        {'test_id': test_id}
    ).fetchone()
    if test:
        return render_template('update_test.html', test=test)
    else:
        return "Test not found", 404
    
# Route to handle updating a test
@app.route('/updateTest/<int:test_id>', methods=['POST'])
def update_test(test_id):
    # Extract form data (updated test details)
    name = request.form['name']
    create_date = request.form['create_date']
    teacher_id = request.form['teacher_id']
    
    try:
        # Update test in the database
        conn.execute(
            text('UPDATE test SET name = :name, create_date = :create_date, teacher_id = :teacher_id WHERE test_id = :test_id'),
            {'name': name, 'create_date': create_date, 'teacher_id': teacher_id, 'test_id': test_id}
        )
        conn.commit()
        return redirect(url_for('test', success='Test updated successfully'))
    
    except Exception as e:
        # In case of error, rollback and show failure message
        conn.rollback()
        print(f"Error occurred while updating test: {e}")
        return render_template('update_test.html', error="Failed to update test")
    
# Route for students to take a test
@app.route('/take_test/<int:test_id>', methods=['GET', 'POST'])
def take_test(test_id):
    try:
        # Fetch students who have NOT taken this specific test
        students = conn.execute(
            text("""
                SELECT user_id, name 
                FROM user 
                WHERE role = 'Student'
                AND user_id NOT IN (
                    SELECT student_id FROM student_answers 
                    WHERE test_id = :test_id
                )
            """),
            {'test_id': test_id}
        ).fetchall()

        # Fetch questions for this test
        questions = conn.execute(
            text("SELECT question_id, question_text FROM question WHERE test_id = :test_id"),
            {'test_id': test_id}
        ).fetchall()

        if request.method == 'POST':
            # Extract student ID, answers, and question IDs from the form
            student_id = request.form['student_id']
            answers = request.form.getlist('answers[]')
            question_ids = request.form.getlist('question_ids[]')

            # Ensure student hasn't taken the test before
            previous_attempt = conn.execute(
                text("""
                    SELECT 1 FROM student_answers 
                    WHERE student_id = :student_id AND test_id = :test_id
                    LIMIT 1
                """),
                {'student_id': student_id, 'test_id': test_id}
            ).fetchone()

            if previous_attempt:
                # If student has already taken the test, redirect
                return redirect(url_for('take_test', test_id=test_id, error="You have already taken this test."))

            # Insert student answers into the database
            for i in range(len(question_ids)):
                conn.execute(
                    text("""
                        INSERT INTO student_answers (student_id, test_id, question_id, answer_text) 
                        VALUES (:student_id, :test_id, :question_id, :answer_text)
                    """),
                    {
                        'student_id': student_id,
                        'test_id': test_id,
                        'question_id': question_ids[i],
                        'answer_text': answers[i] if answers[i].strip() else None
                    }
                )

            conn.commit()

            # Refresh the page after submission
            return redirect(url_for('take_test', test_id=test_id, success="Test submitted successfully!"))

        return render_template('take_test.html', students=students, questions=questions)

    except Exception as e:
        # In case of error, print the error and show failure message
        print(f"Error occurred while taking test: {e}")
        return redirect(url_for('take_test', test_id=test_id, error="Failed to take test."))

# Run the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)
