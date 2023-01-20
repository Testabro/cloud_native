import os, sys, sqlite3, logging

from flask import (
    Flask,
    jsonify,
    json,
    render_template,
    request,
    url_for,
    redirect,
    flash,
)
from werkzeug.exceptions import abort

# GLOBAL VARIABLES
db_connection_count = 0
app = Flask(__name__)

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    db = "database.db"
    if os.path.isfile(db):
        connection = sqlite3.connect(db)
        connection.row_factory = sqlite3.Row
        global db_connection_count
        db_connection_count += 1
        return connection
    return None

# Function to get a post using its ID
def get_post(post_id):
    with get_db_connection() as connection:
        cursor = connection.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
        post = cursor.fetchone()
        if post is None:
            return None
        app.logger.info(' Article "%s" retrieved!', post["title"])
    return post

# Function to get a number of posts
def post_count():
    with get_db_connection() as connection:
        cursor = connection.execute("SELECT COUNT(*) FROM posts")
        post_count = cursor.fetchone()[0]
    return post_count

# Define the Flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = "your secret key"

# Define the main route of the web application
@app.route("/")
def index():
    connection = get_db_connection()
    posts = connection.execute("SELECT * FROM posts").fetchall()
    connection.close()
    return render_template("index.html", posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route("/<int:post_id>")
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.error(' Article with id "%s" does not exist!', post_id)              
        return render_template("404.html"), 404
    else:
        return render_template("post.html", post=post)


# Define the About Us page
@app.route("/about")
def about():
    app.logger.info(' About Us page is retrieved!')
    return render_template("about.html")


# Define the post creation functionality
@app.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title:
            flash("Title is required!")
        else:
            with get_db_connection() as connection:
                connection.execute(
                    "INSERT INTO posts (title, content) VALUES (?, ?)", (title, content)
                )
                connection.commit()
            app.logger.info(' Article "%s" created!', title)
            return redirect(url_for("index"))

    return render_template("create.html")


# Define the health functionality
@app.route("/healthz", methods=["GET"])
def healthcheck():
    if get_db_connection() is None:
        response = app.response_class(
        response=json.dumps({"reason": "Database connection error", "result": "Error - unhealthy" }),
        status=500,
        mimetype="application/json"
        )
        return response

    try:
        post_count()
    except sqlite3.Error:
        response = app.response_class(
        response=json.dumps({ "reason": "Database read error", "result": "Error - unhealthy" }),
        status=500,
        mimetype="application/json"
        )
        return response
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype="application/json"
    )
    
    return response

# Define the metric functionality
@app.route("/metrics", methods=["GET"])
def metrics():
    response = app.response_class(
        response=json.dumps(
            {
                "status": "Success",
                "code": 0,
                "data": {"db_connection_count": db_connection_count, "post_count": post_count()},
            }
        ),
        status=200,
        mimetype="application/json",
    )
    
    return response


# start the application on port 3111
if __name__ == "__main__":
    # set logger to handle STDOUT and STDERR 
    stdout_handler =  logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)

    stderr_handler =  logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)

    handlers = [stderr_handler, stdout_handler]
    # format output
    format_output = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logging.basicConfig(format=format_output, level=logging.DEBUG, handlers=handlers)
    
    # Start the app
    app.run(host="0.0.0.0", port="3111")
