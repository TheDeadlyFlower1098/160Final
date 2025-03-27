from flask import Flask, render_template, request
from sqlalchemy import create_engine, text

app = Flask(__name__) 

con_str = "mysql://root:cset155@localhost/testing"
engine = create_engine(con_str, echo=True)
conn = engine.connect() 

# Home route - displays the home page
@app.route('/')
def hello():
    return render_template('signup.html')
@app.route('/signup', methods = ['GET'])
def getBoat():
    return render_template('signup.html')

@app.route('/signup', methods = ['POST'])
def createBoat():
    try:
        conn.execute(text('INSERT INTO  VALUES ()'), request.form)
        conn.commit
        return render_template('signup.html', error=None, success='successful')
    
    except:
        return render_template('signup.html.html', error = "fail", success = None)


@app.route('/accounts')
def accounts():
    return render_template('accounts.html')

# Run the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)