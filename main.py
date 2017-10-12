from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/newpost', methods = ['POST', 'GET'])
def new_post():
    
    encoded_title_error = request.args.get("title_error")
    encoded_body_error = request.args.get("body_error")
    title_error = ""
    body_error = ""


    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if not title:
            title_error = "You did not enter a title for your blog post."
        
        if not body:
            body_error = "You did not enter any content for your blog post."

        if not title_error and not body_error:
            new_post = Blog(title, body)
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
    blog_id = request.args.get("id")

    if blog_id:
        blog_post = Blog.query.filter_by(id=blog_id).all()
        return render_template('post.html',blog_post=blog_post)

    return render_template('blog.html', blog_post=blog_post)


@app.route("/")
def index():
    
    return redirect("/blog")

if __name__ == '__main__':
    app.run()