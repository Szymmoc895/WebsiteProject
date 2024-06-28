
from flask import Flask, get_flashed_messages, render_template, request, send_file, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user
import bcrypt
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
 
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


@app.route('/generate_plot')
def generate_plot():
    # Użycie surowego ciągu znaków (raw string) do ścieżki pliku CSV
    file_path =  '/home/szym/Documents/Github/WebsiteProject/BAZA/dane.csv'

    # Wczytanie pliku CSV z odpowiednim separatorem
    data = pd.read_csv(file_path, sep=';')

    # Wyświetlenie kolumn i podgląd danych
    print("Kolumny w danych:")
    print(data.columns)

    print("\nPodgląd danych:")
    print(data.head())

    # Konwersja kolumn do odpowiednich typów
    data['wartosc'] = pd.to_numeric(data['wartosc'], errors='coerce')
    data['rok'] = pd.to_numeric(data['rok'], errors='coerce')

    # Usunięcie wierszy z brakującymi danymi
    data = data.dropna(subset=['wartosc', 'rok'])

    # Filtracja danych tylko dla przystępujących
    przystepujacy = data[data['status_zdajacych'].str.contains('przystąpił', case=False, na=False)]

    # Główny wykres: średnia liczba osób przystępujących do egzaminu w poszczególnych województwach
    avg_values = przystepujacy.groupby('wojewodztwo')['wartosc'].mean().reset_index()

    plt.figure(figsize=(15, 7))
    sns.barplot(data=avg_values, x='wojewodztwo', y='wartosc', palette='viridis')
    plt.title('Średnia liczba osób przystępujących do egzaminu maturalnego w poszczególnych województwach')
    plt.xlabel('Województwo')
    plt.ylabel('Średnia liczba osób')
    plt.xticks(rotation=45)
    plt.grid(True)
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    return send_file(img, mimetype='image/png')
    
 
if __name__ == "__main__":
    app.run()
