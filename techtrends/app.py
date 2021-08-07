import logging
import sqlite3

from flask import (Flask, flash, json, jsonify, redirect, render_template,
                   request, url_for)
from werkzeug.exceptions import abort

COUNT = 0


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global COUNT
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    COUNT += 1
    return connection

# Function to get a post using its ID


def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute(
        'SELECT * FROM posts WHERE id = ?',
        (post_id,)
    ).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.error(
            'A non-existing article is accessed and a 404 page is returned')
        return render_template('404.html'), 404
    else:
        app.logger.info('{} article is retrieved'.format(post['title']))
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('The "About Us" page is retrieved')
    return render_template('about.html')


# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute(
                'INSERT INTO posts (title, content) VALUES (?, ?)',
                (title, content)
            )
            connection.commit()
            connection.close()

            app.logger.info('{}, A new article is created'.format(title))
            return redirect(url_for('index'))

    return render_template('create.html')


# Define the health check endpoint
@app.route('/healthz', methods=('GET', ))
def health_check():
    try:
        connection = get_db_connection()
        posts = connection.execute('SELECT * FROM posts').fetchall()
        connection.close()

        response = {'result': 'OK - healthy'}
        return app.response_class(
            response=json.dumps(response),
            status=200,
            mimetype='application/json'
        )
    except Exception as ex:
        response = {'result': 'ERROR - unhealthy'}
        return app.response_class(
            response=json.dumps(response),
            status=500,
            mimetype='application/json'
        )    


# Define the metrics endpoint
@app.route('/metrics', methods=('GET', ))
def metrics():
    # get total number of post count
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    total_post_count = len(posts)
    connection.close()

    # get total number of database connection
    total_db_connection = COUNT

    # preper response and return values
    response = {
        'db_connection_count': total_db_connection,
        'post_count': total_post_count
    }
    return app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )


# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(host='0.0.0.0', port='3111')
