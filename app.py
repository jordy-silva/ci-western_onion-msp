import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def main():
    return render_template("base.html")

@app.route('/new_request')
def new_request():
    return render_template("new_request.html")

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)