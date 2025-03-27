from flask import Flask, render_template, request
from sqlalchemy import create_engine, text

app = Flask(__name__) #Initialize the Flask app

# Database connection string (update credentials as needed)
# Formating: mysql://user:password@server/database
con_str = "mysql://root:cset155@localhost/boatdb"
engine = create_engine(con_str, echo=True)
conn = engine.connect() #creates the database engine

# Home route - displays the home page
@app.route('/')
def hello():
    return render_template('base.html')


# Run the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)