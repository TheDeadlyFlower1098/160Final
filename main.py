from flask import Flask, render_template, request
from sqlalchemy import create_engine, text

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
    return render_template('accounts.html')

# Run the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)