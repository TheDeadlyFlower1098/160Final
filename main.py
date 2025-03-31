from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash 

app = Flask(__name__) 

con_str = "mysql://root:cset155@localhost/testing"
engine = create_engine(con_str, echo=True)
conn = engine.connect() 

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/')
def hello():
    return render_template('loghome.html')
@app.route('/logtest')
def logtest():
   tests = conn.execute(text('SELECT * FROM test')).all()
   return render_template('logtest.html', tests = tests[:10])
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
    try:
        # Fetch only teachers (you can adjust this query if necessary)
        result = conn.execute(
            text("SELECT teacher.teacher_id, user.name FROM teacher INNER JOIN user ON teacher.teacher_id = user.user_id"))
        teachers = result.fetchall()

        return render_template('create_test.html', teachers=teachers)
    
    except Exception as e:
        print(f"Error fetching teachers: {e}")
        return render_template('create_test.html', error="Failed to load teachers.")

@app.route('/create_test', methods=['POST'])
def add_test():
    try:
        test_name = request.form['test_name']
        teacher_id = request.form['teacher_id']
        questions = request.form.getlist('questions') 
        result = conn.execute(
            text('INSERT INTO test (name, teacher_id) VALUES (:test_name, :teacher_id)'),
            {'test_name': test_name, 'teacher_id': teacher_id}
        )
        conn.commit()
        test_id = conn.execute(text('SELECT LAST_INSERT_ID()')).fetchone()[0]
        for question_text in questions:
            if question_text.strip():
                conn.execute(
                    text('INSERT INTO question (test_id, question_text) VALUES (:test_id, :question_text)'),
                    {'test_id': test_id, 'question_text': question_text.strip()}
                )

        conn.commit()
        result = conn.execute(
            text("SELECT teacher.teacher_id, user.name FROM teacher INNER JOIN user ON teacher.teacher_id = user.user_id"))
        teachers = result.fetchall()
        return render_template('create_test.html', success='Test created successfully!', teachers=teachers)

    except Exception as e:
        conn.rollback()
        print(f"Error occurred while creating test: {e}")
        result = conn.execute(
            text("SELECT teacher.teacher_id, user.name FROM teacher INNER JOIN user ON teacher.teacher_id = user.user_id"))
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

@app.route('/test')
def test():
   tests = conn.execute(text('SELECT * FROM test')).all()
   return render_template('test.html', tests = tests[:10])



@app.route('/deleteTest/<int:test_id>', methods=['POST'])
def delete_test(test_id):
    try:
        conn.execute(
            text('DELETE FROM question WHERE test_id = :test_id'),
            {'test_id': test_id}
        )
        conn.execute(
            text('DELETE FROM test WHERE test_id = :test_id'),
            {'test_id': test_id}
        )
        conn.commit()
        return redirect(url_for('test', success='Test deleted successfully'))
    
    except Exception as e:
        conn.rollback()
        print(f"Error occurred while deleting test: {e}")
        return redirect(url_for('test', error="Failed to delete test"))
    
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
    
@app.route('/updateTest/<int:test_id>', methods=['POST'])
def update_test(test_id):
    name = request.form['name']
    create_date = request.form['create_date']
    teacher_id = request.form['teacher_id']
    
    try:
        conn.execute(
            text('UPDATE test SET name = :name, create_date = :create_date, teacher_id = :teacher_id WHERE test_id = :test_id'),
            {'name': name, 'create_date': create_date, 'teacher_id': teacher_id, 'test_id': test_id}
        )
        conn.commit()
        return redirect(url_for('test', success='Test updated successfully'))
    
    except Exception as e:
        conn.rollback()
        print(f"Error occurred while updating test: {e}")
        return render_template('update_test.html', error="Failed to update test")
    
@app.route('/take_test/<int:test_id>', methods=['GET', 'POST'])
def take_test(test_id):
    try:
        # Fetch students
        students = conn.execute(
            text("SELECT user_id, name FROM user WHERE role = 'Student'")
        ).fetchall()

        # Fetch test questions
        questions = conn.execute(
            text("SELECT question_id, question_text FROM question WHERE test_id = :test_id"),
            {'test_id': test_id}
        ).fetchall()

        if request.method == 'POST':
            student_id = request.form['student_id']
            answers = request.form.getlist('answers[]')
            question_ids = request.form.getlist('question_ids[]')

            # Ensure student hasn't taken the test before
            previous_attempt = conn.execute(
                text("SELECT * FROM student_answers WHERE student_id = :student_id AND test_id = :test_id"),
                {'student_id': student_id, 'test_id': test_id}
            ).fetchone()

            if previous_attempt:
                return render_template('take_test.html', error="You have already taken this test.", students=students, questions=questions)

            # Store responses, allowing null values
            for i in range(len(question_ids)):
                answer_text = answers[i].strip() if answers[i].strip() else None  # Convert empty string to None (NULL)
                conn.execute(
                    text("INSERT INTO student_answers (student_id, test_id, question_id, answer_text) VALUES (:student_id, :test_id, :question_id, :answer_text)"),
                    {
                        'student_id': student_id,
                        'test_id': test_id,
                        'question_id': question_ids[i],
                        'answer_text': answer_text
                    }
                )

            conn.commit()
            return render_template('take_test.html', success="Test submitted successfully!", students=students, questions=questions)

        return render_template('take_test.html', students=students, questions=questions)

    except Exception as e:
        print(f"Error occurred while taking test: {e}")
        return render_template('take_test.html', error="Failed to take test")



# Run the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)