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
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['blog_entries','login', 'index', 'register']
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
            return render_template('login.html')

    return render_template('login.html', title="Login")

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        
        if username == "" or " " in username or len(username) < 3 or len(username) > 20:
            flash  ("Invalid username", 'error')
            return render_template('register.html', username=username)

        if password == "" or " " in password or len(password) < 3 or len(password) > 50:
            flash ("Invalid password", 'error')
            return render_template('register.html', username=username)

        if verify == "" or verify != password:
            flash ("Passwords do not match", 'error')
            return render_template('register.html')

        if len(username) > 3 and len(password) > 3 and password == verify and not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        
        else:
            flash ('User already exists', 'error')
            return render_template('register.html')

    else:
        return render_template('register.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/blog', methods=['GET'])
def blog_entries():
    post_id = request.args.get('id')
    user_id = request.args.get('user_id')

    if post_id:
        post = Blog.query.filter_by(id=post_id).first()
        return render_template("one_post.html", new_post=post)
    elif user_id:
        user = User.query.get(user_id)
        return render_template('one_user.html', title="User's Post",user=user)
    else:
        full_blog = Blog.query.all()
        return render_template('full_blog.html', full_blog=full_blog)

@app.route('/newpost', methods = ['GET', 'POST'])
def newpost():
    post_id = request.args.get('id')
    if request.method == 'POST':    
        new_name = request.form['name']
        new_body = request.form['body']
        user = User.query.filter_by(username=session['username']).first()
    
        if new_name == "":
            flash ("You forgot a title", 'error')
            return render_template("new_post.html")

        if new_body == "":
            flash ("You forgot to write something", 'error')
            return render_template("new_post.html")

        else:
            new_entry = Blog(new_name, new_body, user)
            db.session.add(new_entry)
            db.session.commit()
            return render_template("one_post.html", new_post=new_entry)

    else:
        return render_template("new_post.html")

if __name__ == '__main__':
    app.run()

