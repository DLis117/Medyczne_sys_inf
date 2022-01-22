from crypt import methods
from flask import Flask, render_template,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager,login_user, current_user,logout_user,login_required
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm


app=Flask(__name__)
db=SQLAlchemy()
login_manager=LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin,db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(25))
    password=db.Column(db.String(100))

    def __init__(self, name, password):
        self.name = name
        self.password = password

class Lekarze(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    imie=db.Column(db.String(25))
    nazwisko=db.Column(db.String(50))
    adres=db.Column(db.String(200))
    email=db.Column(db.String(100))
    telefon=db.Column(db.Integer)#telefon - integer, usuniety username!
    password=db.Column(db.String(150))

    def __init__(self, imie,nazwisko,adres,email,telefon,password):
        self.imie = imie
        self.nazwisko=nazwisko
        self.adres=adres
        self.email=email
        self.telefon=telefon
        self.password=password

class Pacjenci(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    imie=db.Column(db.String(25))
    nazwisko=db.Column(db.String(50))
    data_ur=db.Column(db.String(50))
    adres=db.Column(db.String(200))
    pesel=db.Column(db.Integer)
    email=db.Column(db.String(100))
    telefon=db.Column(db.Integer)
    password=db.Column(db.String(150))

    def __init__(self, imie,nazwisko,data_ur,adres,pesel,email,telefon,password):
        self.imie = imie
        self.nazwisko=nazwisko
        self.data_ur=data_ur
        self.adres=adres
        self.pesel=pesel
        self.email=email
        self.telefon=telefon
        self.password=password

class Specjalizacje(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nazwa=db.Column(db.String(150))
    id_lekarza=db.Column(db.Integer, db.ForeignKey(Lekarze.id))

    def __init__(self, nazwa, id_lekarza):
        self.nazwa=nazwa
        self.id_lekarza=id_lekarza


class Wizyty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String(150))
    id_lekarza = db.Column(db.Integer, db.ForeignKey(Lekarze.id))
    id_pacjenta = db.Column(db.Integer, db.ForeignKey(Pacjenci.id))
    godzina=db.Column(db.String(150))
    data=db.Column(db.String(50))
    sala=db.Column(db.Integer)

    def __init__(self, nazwa, id_lekarza,id_pacjenta,godzina,data,sala):
        self.nazwa = nazwa
        self.id_lekarza = id_lekarza
        self.id_pacjenta=id_pacjenta
        self.godzina=godzina
        self.data=data
        self.sala=sala

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
@app.route("/home")
def main():
    return render_template('home.html')

# @app.route("/visits")
# @login_required
# def visits():
#     return render_template('visits.html')

@app.route("/register")
def register():
    form = RegistrationForm()
    return render_template('register.html', form=form)

@app.route("/trytoregister",methods=['POST','GET'])
def trytoregister():
    if (request.method == 'POST'):
        name = request.form.get('name')
        surname = request.form.get('surname')
        date_of_birth=request.form.get('date_of_birth')
        adress  = request.form.get('adress')
        pesel = request.form.get('pesel')#unique
        email = request.form.get('email')#unique
        phone_number =request.form.get('phone_number')#unique
        password=request.form.get('password')
        confirm_password=request.form.get('confirm_password')

        gituwa=True
        gr = Pacjenci.query.filter(Pacjenci.pesel == pesel).first()
        if (gr != None):
            flash("podany pesel juz istnieje!")
            gituwa = False
        gr = Pacjenci.query.filter(Pacjenci.email == email).first()
        if (gr != None):
            flash("konto zalozone na podany email juz istnieje!")
            gituwa = False
        gr = Pacjenci.query.filter(Pacjenci.telefon == phone_number).first()
        if (gr != None):
            flash("konto z tym numerem telefonu jest juz w systemie!")
            gituwa = False
        if(password!=confirm_password):#czy hasla sa takie same
            flash("podane hasla nie sa takie same!")
            gituwa=False
        if(gituwa==False):
            form = RegistrationForm()
            return render_template('register.html', form=form)
        password_h = generate_password_hash(password)
        #utworzenie konta
        Pacjent = Pacjenci(name,surname,date_of_birth,adress,pesel,email,phone_number,password_h)
        db.session.add(Pacjent)
        db.session.commit()
        flash("Konto utworzone pomyślnie!")
        return render_template('home.html')

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Pacjenci.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            #login_user(user, remember=form.remember.data)
            return redirect(url_for('main'))
        else:
            flash('Logowanie nieudane, sprawdź email i hasło', 'danger')
    return render_template('login.html', form=form)

if __name__=="__main__":
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.sqlite'
    app.config['SECRET_KEY']='XDDDDD'
    db.init_app(app)
    login_manager.login_view='login'
    login_manager.init_app(app)
    db.create_all(app=app)
    app.run(host='0.0.0.0', debug=True)
