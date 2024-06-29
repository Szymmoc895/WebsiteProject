import os
from flask import Flask, get_flashed_messages, render_template, request, send_from_directory, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import bcrypt
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "abc"
db = SQLAlchemy(app)

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

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = Users.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            login_user(user)
            flash('Zalogowano pomyślnie!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Błędne dane logowania. Spróbuj ponownie.', 'error')

    flashes = list(get_flashed_messages(with_categories=True))
    return render_template('login.html', flashes=flashes)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route('/generate_plots', methods=['GET', 'POST'])
def generate_plots():
    file_path = '/home/szym/Documents/Github/WebsiteProject/BAZA/dane.csv'

    data = pd.read_csv(file_path, sep=';')

    data['wartosc'] = pd.to_numeric(data['wartosc'], errors='coerce')
    data['rok'] = pd.to_numeric(data['rok'], errors='coerce')

    data = data.dropna(subset=['wartosc', 'rok'])

    przystepujacy = data[data['status_zdajacych'].str.contains('przystąpił', case=False, na=False)]

    avg_values = przystepujacy.groupby('wojewodztwo')['wartosc'].mean().reset_index()

    plt.figure(figsize=(15, 7))
    sns.barplot(data=avg_values, x='wojewodztwo', y='wartosc', palette='viridis')
    plt.title('Średnia liczba osób przystępujących do egzaminu maturalnego w poszczególnych województwach')
    plt.xlabel('Województwo')
    plt.ylabel('Średnia liczba osób')
    plt.xticks(rotation=45)
    plt.grid(True)
    main_plot_path = 'static/plots/wszystkie_plot.png'
    plt.savefig(main_plot_path)
    plt.close()

    wojewodztwa = data['wojewodztwo'].unique()

    if not os.path.exists('static/plots'):
        os.makedirs('static/plots')

    for wojewodztwo in wojewodztwa:
        dane_wojewodztwo = data[data['wojewodztwo'] == wojewodztwo]

        przystepujacy_woj = dane_wojewodztwo[dane_wojewodztwo['status_zdajacych'].str.contains('przystąpił', case=False, na=False)]
        
        plt.figure(figsize=(10, 5))
        sns.lineplot(data=przystepujacy_woj, x='rok', y='wartosc', marker='o', label='Przystępujący')
        
        zdajacy_woj = dane_wojewodztwo[dane_wojewodztwo['status_zdajacych'].str.contains('zdał', case=False, na=False)]
        
        sns.lineplot(data=zdajacy_woj, x='rok', y='wartosc', marker='o', label='Zdający')
        
        plt.title(f'Liczba osób przystępujących i zdających w województwie {wojewodztwo}')
        plt.xlabel('Rok')
        plt.ylabel('Liczba osób')
        plt.legend()
        plt.grid(True)
        
        plot_path = f'static/plots/{wojewodztwo}_plot.png'
        plt.savefig(plot_path)
        plt.close()
    
    for wojewodztwo in wojewodztwa:
        # Dane dla wybranego województwa
        dane_wojewodztwo = data[data['wojewodztwo'] == wojewodztwo]

        # Wykres dla przystępujących ogółem, mężczyzn i kobiet
        przystepujacy_woj = dane_wojewodztwo[dane_wojewodztwo['status_zdajacych'].str.contains('przystąpił', case=False, na=False)]

        plt.figure(figsize=(10, 5))
        sns.lineplot(data=przystepujacy_woj, x='rok', y='wartosc', hue='plec', style='plec', markers=True, palette='tab10')

        plt.title(f'Liczba osób przystępujących w województwie {wojewodztwo}')
        plt.xlabel('Rok')
        plt.ylabel('Liczba osób')
        plt.legend(title='Płeć', loc='upper right')
        plt.grid(True)
        
        plot_path = f'static/plots/{wojewodztwo}_przys.png'
        plt.savefig(plot_path)
        plt.close()

        # Wykres dla zdających ogółem, mężczyzn i kobiet
        zdajacy_woj = dane_wojewodztwo[dane_wojewodztwo['status_zdajacych'].str.contains('zdał', case=False, na=False)]

        plt.figure(figsize=(10, 5))
        sns.lineplot(data=zdajacy_woj, x='rok', y='wartosc', hue='plec', style='plec', markers=True, palette='tab10')

        plt.title(f'Liczba osób zdających w województwie {wojewodztwo}')
        plt.xlabel('Rok')
        plt.ylabel('Liczba osób')
        plt.legend(title='Płeć', loc='upper right')
        plt.grid(True)
        
        plot_path = f'static/plots/{wojewodztwo}_zdaj.png'
        plt.savefig(plot_path)
        plt.close()

    return redirect(url_for('index'))

@app.route('/')
def index():
    #generate_plots()
    
    wojewodztwa = [file.split('_')[0] for file in os.listdir('static/plots') if file.endswith('_plot.png')]
    return render_template('home.html', wojewodztwa=wojewodztwa)

@app.route('/plot/<wojewodztwo>')
def plot(wojewodztwo):
    filename = f'{wojewodztwo}_plot.png'
    return send_from_directory('static/plots', filename)

@app.route('/plot/<wojewodztwo>-2')
def plot2(wojewodztwo):
    filename = f'{wojewodztwo}_przys.png'
    return send_from_directory('static/plots', filename)

@app.route('/plot/<wojewodztwo>-3')
def plot3(wojewodztwo):
    filename = f'{wojewodztwo}_zdaj.png'
    return send_from_directory('static/plots', filename)

@app.route('/main_plot')
def main_plot():
    return send_from_directory('static/plots', 'main_plot.png')

if __name__ == "__main__":
    app.run(debug=True)