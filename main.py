from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "It's_a_secret_to_everyone" 

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, body, owner):
        self.name = name
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'full_blog', 'home', 'register']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', title="Blogz for the People", users=users)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash("Either your password was typed incorrectly or the username doesn't exist", 'error')

        return render_template('login.html', title="Login")

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/new_post')
        else:
            flash ('User already exists', 'error')

        if username == "" or " " in username or len(username) < 3 or len(username) > 20:
            flash  ("Invalid username", 'error')
    
        if password == "" or " " in password or len(password) < 3 or len(password) > 20:
            flash ("Invalid password", 'error')

        if verify == "" or verify != password:
            flash ("Passwords do not match", 'error')

        if len(username) > 3 and len(password) > 3 and password == verify and not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/new_post')
    else:
        return render_template('register.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/blog', methods=['GET'])
def full_blog():
    post_id = request.args.get('id')
    user_id = request.args.get('user_id')
    if post_id:
        post = Blog.query.get(post_id)
        return render_template("one_post.html", title="One Post", post=post)
    if user_id:
        user = User.query.filter_by(username=username).first
        user_post = Blog.query.filter_by(owner_id=user.id)
        return render_template('one_user.html', title="User's Post", user=user, post=user_post)


    return render_template('full_blog.html', post=post)

@app.route('/new_post', methods = ['GET', 'POST'])
def new_post():
    if request.method == 'POST':    
        new_name = request.form['name']
        new_body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()

        if new_name == "":
            flash ("You forgot a title", 'error')

        if new_body == "":
            flash("You forgot to write something", 'error')
    
    else: 
        new_post = Blog(new_name, new_body, owner)
        db.session.add(new_post)
        db.session.commit()
    
    return render_template('newpost.html', title="New Posts", post_name=post_name, post_body=post_body)

if __name__ == '__main__':
    app.run()

