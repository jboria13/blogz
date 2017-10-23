from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:finalwork@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup','blog','index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    encoded_username_error = request.args.get("username_error")
    encoded_password_error = request.args.get("password_error")
    username_error=""
    password_error=""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            username_error = "That user does not exist"
            return redirect("/login?username=" + username + "&username_error=" + username_error +"&password_error=" +password_error)
        if user.password != password:
            password_error = "That is not the correct password"
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            return redirect("/login?username=" + username + "&username_error=" + username_error +"&password_error=" +password_error)


    return render_template('login.html', username_error=encoded_username_error,password_error=encoded_password_error)

@app.route("/signup", methods=['GET','POST'])
def signup():
    encoded_username_error = request.args.get("username_error")
    encoded_password_error = request.args.get("password_error")
    encoded_verify_error = request.args.get("verify_error")

    username_error=""
    password_error=""
    verify_error=""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        user = User.query.filter_by(username=username).first()

        if user:
            username_error = "That username is not available"
        elif len(username) > 20:
            username_error = "That's not a valid username"
        elif len(username) < 3:
            username_error = "That's not a valid username"
        elif (' ' in username) == True:
            username_error = "That's not a valid username"
        else:
            pass

        if len(password) > 20:
            password_error = "That's not a valid password"
        elif len(password) < 3:
            password_error = "That's not a valid password"
        elif (' ' in password) == True:
            password_error = "That's not a valid password"
        else:
            pass
    
        if password != verify:
            verify_error = "Passwords don't match"
        else:
            pass

        if not username_error and not password_error and not verify_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            return redirect("/signup?username=" + username + "&username_error=" + username_error +"&password_error=" +password_error + "&verify_error=" + verify_error)

    return render_template('signup.html',username_error=encoded_username_error,password_error=encoded_password_error,verify_error=encoded_verify_error)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/newpost', methods = ['POST', 'GET'])
def new_post():
    
    encoded_title_error = request.args.get("title_error")
    encoded_body_error = request.args.get("body_error")
    title_error = ""
    body_error = ""


    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()

        if not title:
            title_error = "You did not enter a title for your blog post."
        
        if not body:
            body_error = "You did not enter any content for your blog post."

        if not title_error and not body_error:
            new_post = Blog(title, body, owner)
            db.session.add(new_post)
            db.session.commit()

            blog_id = str(new_post.id)
            return redirect("/blog?id=" + blog_id)
        else:
            
            return redirect("/newpost?title_error=" + title_error + "&body_error=" + body_error)

    return render_template('newpost.html',title_error=encoded_title_error, body_error=encoded_body_error)


@app.route('/blog', methods=['GET'])
def blog():
    blog_post = Blog.query.all()
    users = User.query.all()
    blog_id = request.args.get("id")
    user_id = request.args.get("user_id")
    
    if blog_id:
        blog_post = Blog.query.filter_by(id=blog_id).all()
        for blog in blog_post:
            user_id = blog.owner_id
            user = User.query.filter_by(id=user_id).first()

        return render_template('post.html',blog_post=blog_post,user=user)
    if user_id:
        user = User.query.filter_by(id=user_id).first()
        blog_post = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('post.html',blog_post=blog_post,user=user)

    return render_template('blog.html', blog_post=blog_post,users=users)


@app.route("/", methods=['GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run()