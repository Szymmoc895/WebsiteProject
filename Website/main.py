
from flask import Flask, get_flashed_messages, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user
import bcrypt
 
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "abc"
db = SQLAlchemy()
 
login_manager = LoginManager()
login_manager.init_app(app)
 
 
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password_hash = db.Column(db.String(250), nullable=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

 
 
db.init_app(app)
 
 
with app.app_context():
    db.create_all()
 
 
@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)
 
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user = Users(username=username, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        flash('Rejestracja przebiegła pomyślnie!', 'success')
        return redirect(url_for("login"))
    
    return render_template("sign_up.html")
 
 
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         user = Users.query.filter_by(
#             username=request.form.get("username")).first()
#         if user.password == request.form.get("password"):
#             login_user(user)
#             return redirect(url_for("home"))
#     return render_template("login.html")
 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = Users.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            login_user(user)
            flash('Zalogowano pomyślnie!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Błędne dane logowania. Spróbuj ponownie.', 'error')

    flashes = list(get_flashed_messages(with_categories=True))
    return render_template('login.html', flashes=flashes)
 
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))
 
 
@app.route("/")
def home():
    return render_template("home.html")
 
 
if __name__ == "__main__":
    app.run()
