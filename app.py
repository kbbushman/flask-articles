from flask import Flask, render_template
from data import Articles

app = Flask(__name__)

Articles = Articles()

# Home Route
@app.route('/')
def index():
  return render_template('home.html')


# About Route
@app.route('/about')
def about():
  return render_template('about.html')


# All Articles Route
@app.route('/articles')
def articles():
  return render_template('articles.html', articles=Articles)


# Single Article Route
@app.route('/articles/<string:id>/')
def article(id):
  return render_template('article.html', id=id)


if __name__ == '__main__':
  # Add debug=True for server to detect changes and restart
  app.run(debug=True)
