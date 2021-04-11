from flask import Flask, render_template, url_for, request, redirect
import os

app = Flask(__name__)
port = int(os.environ.get('PORT', 5000))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/output')
def output():
    return render_template('output.html')


if __name__ == '__main__':
    app.run(debug=True)