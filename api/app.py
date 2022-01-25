# from crypt import methods
from flask import Flask, render_template,request,redirect,url_for,flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager,login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm,VisitForm
from datetime import datetime
#from wtforms.fields.html5 import DateField

app=Flask(__name__)
db=SQLAlchemy()
login_manager=LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Musisz być zalogowany, by zobaczyć tę stronę.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin,db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(25))
    surname=db.Column(db.String(50))
    birthdate=db.Column(db.Date())
    address=db.Column(db.String(100))
    pesel=db.Column(db.Integer)
    email=db.Column(db.String(100))
    phone_number=db.Column(db.String(25))
    password=db.Column(db.String(150))
    class_type=db.Column(db.Integer)                #domyslnie 3 a potem admin zmienia : 0-pacjent 1-lekarz 2-admin
    jwt_token=db.Column(db.String(200))
    account_confirmed=db.Column(db.Integer)

    def __init__(self, name, surname,birthdate,address,pesel,email,phone_number,password,class_type,jwt_token,account_confirmed):
        self.name = name
        self.surname=surname
        self.birthdate=birthdate
        self.address=address
        self.pesel=pesel
        self.email=email
        self.phone_number=phone_number
        self.password = password
        self.class_type=class_type
        self.jwt_token=jwt_token
        self.account_confirmed=account_confirmed

    def __str__(self):
        return self.name + ' ' + self.surname

class Specializations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(150))
    doctor_id=db.Column(db.Integer, db.ForeignKey(User.id))#        zrob dodatkowe sprawdzenie czy lekarz!

    def __init__(self, name, doctor_id):
        self.name=name
        self.doctor_id=doctor_id
    
    def __str__(self):
        return self.name


class Visits(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey(User.id))#        zrob dodatkowe sprawdzenie czy lekarz!
    patient_id = db.Column(db.Integer, db.ForeignKey(User.id))#        zrob dodatkowe sprawdzenie czy pacjent!
    date_and_time=db.Column(db.String(150))
    room=db.Column(db.Integer)
    note = db.Column(db.String(150))
    visit_confirmed=db.Column(db.Integer)

    def __init__(self, doctor_id, patient_id,date_and_time,room,note,visit_confirmed):
        self.doctor_id=doctor_id
        self.patient_id=patient_id
        self.date_and_time=date_and_time
        self.room=room
        self.note=note
        self.visit_confirmed=visit_confirmed

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
@app.route("/home")
def main():
    return render_template('home.html')



@app.route("/register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = RegistrationForm()
    return render_template('register.html', form=form)

@app.route("/trytoregister",methods=['POST','GET'])
def trytoregister():
    if (request.method == 'POST'):
        name = request.form.get('name')
        surname = request.form.get('surname')
        birthdate=request.form.get('date_of_birth')
        date_of_birth = datetime.strptime(birthdate, '%Y-%m-%d')
        adress  = request.form.get('adress')
        pesel = request.form.get('pesel')#unique
        email = request.form.get('email')#unique
        phone_number =request.form.get('phone_number')#unique
        password=request.form.get('password')
        confirm_password=request.form.get('confirm_password')

        gituwa=True
        gr = User.query.filter(User.pesel == pesel).first()
        if (gr != None):
            flash("podany pesel juz istnieje!")
            gituwa = False
        gr = User.query.filter(User.email == email).first()
        if (gr != None):
            flash("konto zalozone na podany email juz istnieje!")
            gituwa = False
        gr = User.query.filter(User.phone_number == phone_number).first()
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
        Pacjent = User(name,surname,date_of_birth,adress,pesel,email,phone_number,password_h,3,"jwt_token_default",0)
        db.session.add(Pacjent)
        db.session.commit()
        flash("Konto utworzone pomyślnie, poczekaj na weryfikacje!")
        return render_template('home.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = LoginForm()
    if form.validate_on_submit():
         user = User.query.filter_by(email=form.email.data).first()
         if user and check_password_hash(user.password, form.password.data):
             login_user(user, remember=form.remember.data)
             next_page = request.args.get('next')
             return redirect(next_page) if next_page else redirect(url_for('main'))
         else:
             flash('Logowanie nieudane, sprawdź email i hasło', 'danger')
    return render_template('login.html', form=form)

@app.route('/logut')
def logout():
    logout_user()
    return redirect(url_for('main'))

@app.route('/account')
@login_required
def account():
    return render_template('account.html')

@app.route("/visits", methods=['GET', 'POST'])
@login_required
def new_visit():
    baza=[]
    bazaa=[]
    user = User.query.filter(User.class_type==1)    #bierze wszytkich lekarzy
    for i in user:
        spec=Specializations.query.filter(Specializations.doctor_id==i.id)  #wszystkie specjalizacje danego lekarza
        for j in spec:
            record=(i.id,i.name,i.surname,j.name)
            bazaa.append(record)
    # form = VisitForm()
    baza.append(current_user.id)
    baza.append(bazaa)
    return render_template('visits.html',baza=baza)

@app.route("/submit_visit", methods=['GET', 'POST'])
@login_required
def submit_visit():
    if (request.method == 'POST'):
        id=current_user.id
        selected = request.form.get('selected')
        l = selected.split(' ')
        doctor_id=l[0]
        date_and_time = request.form.get('date_and_time')
        note = request.form.get('note')
        n_visit = Visits(doctor_id,id,date_and_time,-1,note,2) #2 == do potwierdzenia 0=odrzucona 1=potiwerdzona
        db.session.add(n_visit)
        db.session.commit()
        flash('pomyslnie dodano wizyte, poczekaj na jej akceptacje przez lekarza', 'danger')
        return render_template('account.html')

if __name__=="__main__":
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.sqlite'
    app.config['SECRET_KEY']='XDDDDD'
    db.init_app(app)
    login_manager.login_view='login'
    login_manager.init_app(app)
    db.create_all(app=app)
    app.run(host='0.0.0.0', debug=True)
