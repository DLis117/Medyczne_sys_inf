from lib2to3.pgen2 import token
import os
from flask import Flask, render_template,request,redirect,url_for,flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager,login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm,VisitForm, DeleteUserForm, RequestResetForm, ResetPasswordForm
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_mail import Mail, Message

app=Flask(__name__)
db=SQLAlchemy()
login_manager=LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Musisz być zalogowany, by zobaczyć tę stronę.'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD')
mail = Mail(app)

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

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

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
        date_of_birth=request.form.get('date_of_birth')
        birthdate=date_of_birth.replace("T"," ")
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

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Reset hasła',
                    sender='noreply@demo.com', 
                    recipients=[user.email])
    msg.body = '''By zresetować swoje hasło, wejdź w poniższy link:
{}

Jeśli nie chcesz zresetować swojego hasła, zignoruj ten email, żadne zmiany nie zostaną wprowadzone.
'''.format(url_for('reset_token', token=token, _external=True))
    mail.send(msg)

@app.route('/reset_password', methods=['GET','POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # if not user:
        #     flash("Konto założone na podany email nie istnieje!")
        #     return redirect(url_for('reset_password'))
        send_reset_email(user)
        flash("Email z instrukcjami został wysłany.")
        return redirect(url_for('login'))
    return render_template('reset_request.html',title='Reset hasła', form=form)
    

@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("Nieprawidłowy lub wygasły token")
        return redirect(url_for('reset_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        password_h = generate_password_hash(form.password)
        user.password = password_h
        db.session.commit()
        flash("Hasło zostało zmienione!")
        return redirect(url_for('login'))
    return render_template('reset_token.html',title='Reset hasła', form=form)

@app.route('/delete_account', methods = ['GET','POST'])             #DO POPRAWY, MA USUWAC TEZ WIZYTY! zmienilem nazwy bo kolidowaly.
@login_required
def delete_account():
    form = DeleteUserForm()
    if form.validate_on_submit():
        user_to_delete = User.query.filter(id == current_user.id).first()
        try:
            logout_user()
            db.session.delete(user_to_delete)
            db.session.commit()
            flash(user_to_delete)
            return redirect(url_for('main'))
        except:
            flash("Nie udało się usunąć konta", 'danger')
    return render_template('account.html',form=form)

@app.route('/account')
@login_required
def account():
    baza=[]
    user = User.query.filter(User.id == current_user.id).first()
    if ((user.account_confirmed == 1) and (user.class_type==0 or user.class_type==2)):
        visits=Visits.query.filter(Visits.patient_id==current_user.id)
        for i in visits:
            user=User.query.filter(User.id==i.doctor_id)

            for j in user:
                x = j.email
                print(x)
                if (i.visit_confirmed == 1):
                    o1="hidden"
                    o2="submit"
                    o3="submit"
                    confirmation = "potwierdzona!"
                elif (i.visit_confirmed == 0):
                    o1 = "hidden"
                    o2 = "submit"
                    o3 = "submit"
                    confirmation = "odrzucona!"
                elif (i.visit_confirmed == 2):
                    o1 = "hidden"
                    o2 = "submit"
                    o3 = "submit"
                    confirmation = "oczekuje na potwierdzenie przez lekarza!"
                else:
                    o1 = "submit"
                    o2 = "submit"
                    o3 = "submit"
                    confirmation = "potwierdz / usun / zmien"
                baza.append((i.id,j.name,j.surname,i.date_and_time,i.room,confirmation,"lekarzem",o1,o2,o3,i.note))
        return render_template('account.html',baza=baza)
    elif(user.account_confirmed==1) and (user.class_type==1):
        visits = Visits.query.filter(Visits.doctor_id == current_user.id)
        for i in visits:
            user=User.query.filter(User.id==i.patient_id)
            for j in user:
                if (i.visit_confirmed == 1):
                    o1 = "hidden"
                    o2 = "submit"
                    o3 = "submit"
                    confirmation = "potwierdzona!"
                elif (i.visit_confirmed == 0):
                    o1 = "hidden"
                    o2 = "hidden"
                    o3 = "submit"
                    confirmation = "odrzucona!"
                elif (i.visit_confirmed == 2):
                    o1 = "submit"
                    o2 = "submit"
                    o3 = "submit"
                    confirmation = "potwierdz / usun / zmien"
                else:
                    o1 = "hidden"
                    o2 = "hidden"
                    o3 = "submit"
                    confirmation = "oczekuje na potwierdzenie przez pacjenta!"
                baza.append((i.id,j.name,j.surname,i.date_and_time,i.room,confirmation,"pacjentem",o1,o2,o3,i.note,current_user.id))
        return render_template('account.html', baza=baza)
    else:
        return "poczekaj na weryfikacje konta!"

@app.route('/visit_accept',methods=['POST','GET'])
@login_required
def visit_accept():
    if (request.method == 'POST'):
        visit=Visits.query.filter(Visits.id==int(request.form.get('id'))).first()
        visit.visit_confirmed=1
        db.session.commit()
        return redirect("account")

@app.route('/visit_deny',methods=['POST','GET']) #lekarz jedynie oznacza ze termin odrzucony a pacjent usuwa
@login_required
def visit_deny():
    if (request.method == 'POST'):
        visit=Visits.query.filter(Visits.id==int(request.form.get('id'))).first()
        user=User.query.filter(User.id==current_user.id).first()
        if(user.class_type==1):
            visit.visit_confirmed=0
            db.session.commit()
            return redirect("account")
        else:
            db.session.delete(visit)
            db.session.commit()
            return redirect("account")


@app.route('/visit_edit',methods=['POST','GET'])
@login_required
def visit_edit():
    if (request.method == 'POST'):
        visit=Visits.query.filter(Visits.id==int(request.form.get('id'))).first()
        user=User.query.filter(User.id==current_user.id).first()
        nrp=""
        if (user.class_type == 1):
            nrp="nr pokoju"

        id=visit.id
        name = request.form.get('name')
        surname = request.form.get('surname')
        specialization = request.form.get('specialization')
        date_and_time = request.form.get('date_and_time')
        datetime_object = datetime.strptime(date_and_time, '%Y-%m-%d %H:%M:%S')
        room = request.form.get('room')
        note = request.form.get('note')
        bazaaa=[]
        bazaaa.append(id)
        bazaaa.append(name)
        bazaaa.append(surname)
        bazaaa.append(specialization)
        bazaaa.append(datetime_object)
        bazaaa.append(room)
        bazaaa.append(note)


        visibility = []
        if(user.class_type==1):
            visibility.append("number")
        else:
            visibility.append("hidden")

        baza = []
        bazaa = []
        user = User.query.filter(User.class_type == 1)  # bierze wszytkich lekarzy
        for i in user:
            spec = Specializations.query.filter(
                Specializations.doctor_id == i.id)  # wszystkie specjalizacje danego lekarza
            for j in spec:
                record = (i.id, i.name, i.surname, j.name)
                bazaa.append(record)

        user=User.query.filter(User.id==visit.patient_id).first()
        baza.append((user.name,user.surname))
        baza.append(bazaa)
        baza.append(bazaaa)
        baza.append(visibility)
        baza.append(nrp)
        return render_template('visit_edit2.html', baza=baza)


@app.route('/try_to_edit_visit',methods=['POST','GET'])
@login_required
def try_to_edit_visit():
    if (request.method == 'POST'):
        idd=request.form.get('idxx')
        date_and_time = request.form.get('date_and_time')
        date_and_time=date_and_time.replace("T"," ")
        date_and_time+=":00"
        datetime_object = datetime.strptime(date_and_time, '%Y-%m-%d %H:%M:%S')
        room = request.form.get('room')
        note = request.form.get('note')
        selected=request.form.get('selected')
        l = selected.split(' ')

        doctor_id=User.query.filter(User.name==l[1], User.surname==l[2]).first()
        doctor_id=doctor_id.id
        visit=Visits.query.filter(Visits.id==idd).first()
        visit.doctor_id=doctor_id
        visit.date_and_time=datetime_object
        visit.room=room
        if(note!=None and note!=""):
            visit.note=note
        else:
            visit.note=""
        if(current_user.class_type==0):
            visit.visit_confirmed=2
        else:
            visit.visit_confirmed=3

        db.session.commit()
        return redirect("account")

@app.route("/visits", methods=['GET', 'POST'])                          #PACJENT/LEKARZ
@login_required
def new_visit():
    form = VisitForm()
    if form.validate_on_submit():
        flash('Wizyta została umówiona!')
        return redirect(url_for('main'))
    baza = []
    bazaa = []
    user = User.query.filter(User.class_type == 1)  # bierze wszytkich lekarzy
    for i in user:
        spec = Specializations.query.filter(Specializations.doctor_id == i.id)  # wszystkie specjalizacje danego lekarza
        for j in spec:
            record = (i.id, i.name, i.surname, j.name)
            bazaa.append(record)
    # form = VisitForm()
    baza.append(current_user.id)
    baza.append(bazaa)
    return render_template('visits.html', baza=baza)

#---------------------------------------------------
@app.route("/admin_index")
def admin_main():
    return render_template("admin_index.html")

@login_required
@app.route('/admin__chose')
def admin__chose():
    x=User.query.filter(User.id ==current_user.id).first()
    if(x.class_type!=2):
        flash( "nie masz uprawnien administratora!")
        return redirect("admin_index")
    baza = []
    unverified = []
    patients = []
    doctors = []
    Unverified = User.query.filter(User.class_type == 3)  # bierzemy tylko niezweryfikowanych PACJENTOW!!!
    for i in Unverified:
        unverified.append(i)

    Patients = User.query.filter(User.class_type == 0)  # bierzemy tylko lekarzy
    for i in Patients:
        patients.append(i.id)

    Doctors = User.query.filter(User.class_type == 1)  # bierzemy tylko lekarzy
    for i in Doctors:
        doctors.append(i.id)

    baza.append(unverified)
    baza.append(patients)
    baza.append(doctors)
    return render_template(('admin_chose.html'), baza=baza)





@app.route('/admin_logging',methods=['POST','GET'])
def admin_logging():
    if(request.method=='POST'):
        email=request.form.get('email')
        password = request.form.get('password')
        if (email == "") or (password == ""):
            flash("wypelnij wszystkie pola!")
            return render_template(('admin_index.html'))
        x=User.query.filter(email==email).first()
        if(x.class_type!=2):
            flash("nie masz uprawnien administratora!")
            return render_template(('admin_index.html'))
        if x and check_password_hash(x.password,password):
            login_user(x)
            return redirect("admin__chose")
        else:
            flash("nieprawidlowy login lub haslo!")
            return render_template(('admin_index.html'))


@app.route('/admin_verify_accept',methods=['POST','GET'])
@login_required
def admin_verify_accept():
    if (request.method == 'POST'):
        id = request.form.get('id')
        pacjent=User.query.filter(User.id==id).first()
        pacjent.class_type=0
        db.session.commit()
        return redirect("admin__chose")

@app.route('/admin_verify_deny',methods=['POST','GET'])
@login_required
def admin_verify_deny():
    if (request.method == 'POST'):
        id = request.form.get('id')
        pacjent=User.query.filter(User.id==id).first()

        db.session.delete(pacjent)  #nie trzeba usuwac jego wizyt bo jeszcze takowe nie zostaly utworzone
        db.session.commit()
        return redirect("admin__chose")

@app.route('/admin_add_doctor',methods=['POST','GET'])
@login_required
def admin_add_doctor():
    if (request.method == 'POST'):
        x = User.query.filter(User.id==current_user.id).first()
        if (x.class_type != 2):
            flash("nie masz uprawnien administratora!")
            return render_template(('index.html'))
        name = request.form.get('name')
        surname = request.form.get('surname')
        birthdate=request.form.get('birthdate')
        date_time_obj = datetime.strptime(birthdate, '%Y-%m-%d')
        address = request.form.get('address')
        pesel = request.form.get('pesel')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        class_type=1
        jwt_token="default"
        account_confirmed=1
        password_h=generate_password_hash(password)

        Doctor=User(name,surname,date_time_obj,address,pesel,email,phone_number,password_h,class_type,jwt_token,account_confirmed)
        db.session.add(Doctor)
        db.session.commit()

        spec1 = request.form.get('spec1')#on/None
        spec2 = request.form.get('spec2')
        spec3 = request.form.get('spec3')
        spec4 = request.form.get('spec4')
        spec5 = request.form.get('spec5')
        spec6 = request.form.get('spec6')

        id=0
        doctors = User.query.filter(User.class_type==1)
        for i in doctors:
            id=int(i.id)    #id ostaniego lekarza (ostatnio dodanego)

        if (spec1 == "on"):
            spec = Specializations("laryngolog",id)
            db.session.add(spec)
        if (spec2 == "on"):
            spec = Specializations("proktolog",id)
            db.session.add(spec)
        if (spec3 == "on"):
            spec = Specializations("dentysta",id)
            db.session.add(spec)
        if (spec4 == "on"):
            spec = Specializations("okulista",id)
            db.session.add(spec)
        if (spec5 == "on"):
            spec = Specializations("neurolog",id)
            db.session.add(spec)
        if (spec6 == "on"):
            spec = Specializations("gastrolog",id)
            db.session.add(spec)
        db.session.commit()

        return redirect("admin__chose")
#
#
# @app.route('/delete',methods=['POST','GET'])
# @login_required
# def delete():
#     if (request.method == 'POST'):
#         id_lekarza = int(request.form.get('selected'))#nie dodawaj do opcji ale do select'a
#         gr = Specializations.query.filter(Specializations.id_lekarza == id_lekarza)
#         for i in gr:
#             db.session.delete(i)
#         db.session.commit()
#         gr = Lekarze.query.filter(Lekarze.id == id_lekarza).first()#pamietaj o first!
#         db.session.delete(gr)
#         db.session.commit()
#         baza = []
#         lekarze = Lekarze.query.all()
#         for i in lekarze:
#             baza.append(i.id)
#         return render_template(('admin_chose.html'), baza=baza)
#
@app.route('/admin_edit_doctor',methods=['POST','GET'])
@login_required
def admin_edit_doctor():
    if (request.method == 'POST'):
        x = User.query.filter(User.id == current_user.id).first()
        if (x.class_type != 2):
            flash("nie masz uprawnien administratora!")
            return render_template(('admin_index.html'))
        doctor_id = int(request.form.get('selected'))#nie dodawaj do opcji ale do select'a
        gr = User.query.filter(User.id == doctor_id).first()  # pamietaj o first!
        if(gr!=None):

            baza=[]
            baza.append(doctor_id)
            baza.append(gr.name)
            baza.append(gr.surname)
            baza.append(gr.birthdate)
            baza.append(gr.address)
            baza.append(gr.pesel)
            baza.append(gr.email)
            baza.append(gr.phone_number)
            baza.append(gr.password)
            baza.append(gr.class_type)
            baza.append(gr.jwt_token)
            baza.append(int(gr.account_confirmed))
            #sprawdzam jakie checkboxy zaznaczyc
            bylo=False
            gr=Specializations.query.filter(Specializations.doctor_id==doctor_id)
            for i in gr:
                if (i.name == "laryngolog"):  # 8
                    bylo = True
                    break
            if (bylo == True):
                baza.append("checked")
            else:
                baza.append("")
            bylo = False
            for i in gr:
                if (i.name == "proktolog"):  # 9
                    bylo = True
                    break
            if (bylo == True):
                baza.append("checked")
            else:
                baza.append("")
            bylo = False
            for i in gr:
                if (i.name == "dentysta"):  # 10
                    bylo = True
                    break
            if (bylo == True):
                baza.append("checked")
            else:
                baza.append("")
            bylo = False
            for i in gr:
                if (i.name == "okulista"):  # 11
                    bylo = True
                    break
            if (bylo == True):
                baza.append("checked")
            else:
                baza.append("")
            bylo = False
            for i in gr:
                if (i.name == "neurolog"):  # 12
                    bylo = True
                    break
            if (bylo == True):
                baza.append("checked")
            else:
                baza.append("")
            bylo = False
            for i in gr:
                if (i.name == "gastrolog"):  # 13
                    bylo = True
                    break
            if (bylo == True):
                baza.append("checked")
            else:
                baza.append("")
            return render_template(('admin_edit_doctor.html'), baza=baza)

@app.route('/admin_edit_patient',methods=['POST','GET'])
@login_required
def admin_edit_patient():
    if (request.method == 'POST'):
        x = User.query.filter(User.id == current_user.id).first()
        if (x.class_type != 2):
            flash("nie masz uprawnien administratora!")
            return render_template(('admin_index.html'))
        patient_id = int(request.form.get('selected'))#nie dodawaj do opcji ale do select'a
        gr = User.query.filter(User.id == patient_id).first()  # pamietaj o first!
        if(gr!=None):
            baza=[]
            baza.append(patient_id)
            baza.append(gr.name)
            baza.append(gr.surname)
            baza.append(gr.birthdate)
            baza.append(gr.address)
            baza.append(gr.pesel)
            baza.append(gr.email)
            baza.append(gr.phone_number)
            baza.append(gr.password)
            baza.append(gr.class_type)
            baza.append(gr.jwt_token)
            baza.append(int(gr.account_confirmed))
            return render_template(('admin_edit_patient.html'), baza=baza)


@app.route('/admin_doctor_edited',methods=['POST','GET'])
@login_required
def admin_doctor_edited():
    if (request.method == 'POST'):
        id=request.form.get('id')
        name = request.form.get('name')
        surname = request.form.get('surname')
        birthdate = request.form.get('birthdate')
        date_time_obj = datetime.strptime(birthdate,'%Y-%m-%d')
        address = request.form.get('address')
        pesel = request.form.get('pesel')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        class_type = request.form.get('class_type')
        jwt_token = request.form.get('jwt_token')
        account_confirmed = request.form.get('account_confirmed')
        spec1 = request.form.get('spec1')  # on/None
        spec2 = request.form.get('spec2')
        spec3 = request.form.get('spec3')
        spec4 = request.form.get('spec4')
        spec5 = request.form.get('spec5')
        spec6 = request.form.get('spec6')

        gr = Specializations.query.filter(Specializations.doctor_id == id)
        for i in gr:
            db.session.delete(i)
        db.session.commit()

        if (spec1 == "on"):
            spec = Specializations("laryngolog", id)
            db.session.add(spec)
        if (spec2 == "on"):
            spec = Specializations("proktolog", id)
            db.session.add(spec)
        if (spec3 == "on"):
            spec = Specializations("dentysta", id)
            db.session.add(spec)
        if (spec4 == "on"):
            spec = Specializations("okulista", id)
            db.session.add(spec)
        if (spec5 == "on"):
            spec = Specializations("neurolog", id)
            db.session.add(spec)
        if (spec6 == "on"):
            spec = Specializations("gastrolog", id)
            db.session.add(spec)
        db.session.commit()

        gr = User.query.filter(User.id == id).first()
        gr.name=name
        gr.surname=surname
        gr.birthdate=date_time_obj
        gr.address=address
        gr.pesel=pesel
        gr.email=email
        gr.phone_number=phone_number
        gr.password=password
        gr.class_type=class_type
        gr.jwt_token=jwt_token
        gr.account_confirmed=account_confirmed
        db.session.commit()

        return redirect("admin__chose")


@app.route('/admin_patient_edited',methods=['POST','GET'])
@login_required
def admin_patient_edited():
    if (request.method == 'POST'):
        id=request.form.get('id')
        name = request.form.get('name')
        surname = request.form.get('surname')
        birthdate = request.form.get('birthdate')
        date_time_obj = datetime.strptime(birthdate,'%Y-%m-%d')
        address = request.form.get('address')
        pesel = request.form.get('pesel')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        class_type = request.form.get('class_type')
        jwt_token = request.form.get('jwt_token')
        account_confirmed = request.form.get('account_confirmed')


        #edycja pacjenta
        gr = User.query.filter(User.id == id).first()
        gr.name=name
        gr.surname=surname
        gr.birthdate=date_time_obj
        gr.address=address
        gr.pesel=pesel
        gr.email=email
        gr.phone_number=phone_number
        gr.password=password
        gr.class_type=class_type
        gr.jwt_token=jwt_token
        gr.account_confirmed=account_confirmed
        db.session.commit()

        return redirect("admin__chose")


@app.route('/admin_back',methods=['POST','GET'])
@login_required
def admin_back():
    x = User.query.filter(User.id == current_user.id).first()
    if (x.class_type != 2):
        flash("nie masz uprawnien administratora!")
        return render_template(('admin_index.html'))
    return redirect("admin__chose")
#
#

@app.route('/admin_logout',methods=['POST','GET'])
@login_required
def admin_logout():
    x = User.query.filter(User.id == current_user.id).first()
    if (x.class_type != 2):
        flash("nie masz uprawnien administratora!")
        return render_template(('admin_index.html'))
    logout_user()
    return render_template(('admin_index.html'))
#---------------------------------------------------


if __name__=="__main__":
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.sqlite'
    app.config['SECRET_KEY']='XDDDDD'
    db.init_app(app)
    login_manager.login_view='login'
    login_manager.init_app(app)
    db.create_all(app=app)
    app.run(host='0.0.0.0', debug=True)
