from flask import Flask, render_template,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager,login_user, current_user,logout_user,login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
app=Flask(__name__)
db=SQLAlchemy()
login_manager=LoginManager()

class User(UserMixin,db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(25))
    surname=db.Column(db.String(50))
    birthdate=db.Column(db.DateTime)
    address=db.Column(db.String(100))
    pesel=db.Column(db.Integer)
    email=db.Column(db.String(100))
    phone_number=db.Column(db.String(25))
    password=db.Column(db.String(150))
    class_type=db.Column(db.Integer)                #domyslnie 3 a potem admin zmienia : 0-pacjent 1-lekarz 2-admin
    jwt_token=db.Column(db.String(200))
    account_confirmed=db.Column(db.Boolean)

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

class Specializations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(150))
    doctor_id=db.Column(db.Integer, db.ForeignKey(User.id))#        zrob dodatkowe sprawdzenie czy lekarz!

    def __init__(self, name, doctor_id):
        self.name=name
        self.doctor_id=doctor_id


class Visits(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey(User.id))#        zrob dodatkowe sprawdzenie czy lekarz!
    patient_id = db.Column(db.Integer, db.ForeignKey(User.id))#        zrob dodatkowe sprawdzenie czy pacjent!
    date_and_time=db.Column(db.String(150))
    room=db.Column(db.Integer)
    note = db.Column(db.String(150))

    def __init__(self, doctor_id, patient_id,date_and_time,room,note):
        self.doctor_id=doctor_id
        self.patient_id=patient_id
        self.date_and_time=date_and_time
        self.room=room
        self.note=note

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def main():
    return render_template("admin_index.html")

@app.route('/admin_logging',methods=['POST','GET'])
def admin_logging():
    if(request.method=='POST'):
        email=request.form.get('email')
        password = request.form.get('password')
        if (email == "") or (password == ""):
            flash("wypelnij wszystkie pola!")
            return render_template(('admin_index.html'))
        x=User.query.filter_by(email=email).first()
        if x and check_password_hash(x.password,password):
            login_user(x)
            baza=[]
            unverified=[]
            patients = []
            doctors = []
            Unverified=User.query.filter(User.class_type == 3)  # bierzemy tylko niezweryfikowanych PACJENTOW!!!
            for i in Unverified:
                unverified.append(i)

            Patients = User.query.filter(User.class_type == 0)  # bierzemy tylko lekarzy
            for i in Patients:
                patients.append(i.id)

            Doctors= User.query.filter(User.class_type==1)# bierzemy tylko lekarzy
            for i in Doctors:
                doctors.append(i.id)

            baza.append(unverified)
            baza.append(patients)
            baza.append(doctors)
            return render_template(('admin_chose.html'),baza=baza)
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

@app.route('/admin_verify_deny',methods=['POST','GET'])
@login_required
def admin_verify_deny():
    if (request.method == 'POST'):
        id = request.form.get('id')
        pacjent=User.query.filter(User.id==id).first()

        db.session.delete(pacjent)  #nie trzeba usuwac jego wizyt bo jeszcze takowe nie zostaly utworzone
        db.session.commit()

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

@app.route('/admin_add_doctor',methods=['POST','GET'])
@login_required
def admin_add_doctor():
    if (request.method == 'POST'):
        name = request.form.get('name')
        surname = request.form.get('surname')
        birthdate=request.form.get('birthdate')
        birthdate=birthdate.replace("T"," ")
        birthdate=birthdate+":00"
        date_time_obj = datetime.strptime(birthdate, '%Y-%m-%d %H:%M:%S')
        address = request.form.get('address')
        pesel = request.form.get('pesel')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        class_type=1
        jwt_token="default"
        account_confirmed=True
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
            baza.append(gr.account_confirmed)

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
            baza.append(gr.account_confirmed)
            return render_template(('admin_edit_patient.html'), baza=baza)


@app.route('/admin_doctor_edited',methods=['POST','GET'])
@login_required
def admin_doctor_edited():
    if (request.method == 'POST'):
        id=request.form.get('id')
        name = request.form.get('name')
        surname = request.form.get('surname')
        birthdate = request.form.get('birthdate')
        birthdate = birthdate.replace("T", " ")
        birthdate = birthdate + ":00"
        date_time_obj = datetime.strptime(birthdate, '%Y-%m-%d %H:%M:%S')
        address = request.form.get('address')
        pesel = request.form.get('pesel')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        class_type = request.form.get('class_type')
        jwt_token = request.form.get('jwt_token')
        account_confirmed = bool(request.form.get('account_confirmed'))

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


@app.route('/admin_patient_edited',methods=['POST','GET'])
@login_required
def admin_patient_edited():
    if (request.method == 'POST'):
        id=request.form.get('id')
        name = request.form.get('name')
        surname = request.form.get('surname')
        birthdate = request.form.get('birthdate')
        birthdate = birthdate.replace("T", " ")
        birthdate = birthdate + ":00"
        date_time_obj = datetime.strptime(birthdate, '%Y-%m-%d %H:%M:%S')
        address = request.form.get('address')
        pesel = request.form.get('pesel')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        class_type = request.form.get('class_type')
        jwt_token = request.form.get('jwt_token')
        account_confirmed = bool(request.form.get('account_confirmed'))


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


@app.route('/admin_back',methods=['POST','GET'])
@login_required
def admin_back():
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
#
#

@app.route('/admin_logout',methods=['POST','GET'])
@login_required
def admin_logout():
    logout_user()
    return render_template(('admin_index.html'))


if __name__=="__main__":
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.sqlite'
    app.config['SECRET_KEY']='XDDDDD'
    db.init_app(app)
    login_manager.login_view='login'
    login_manager.init_app(app)
    db.create_all(app=app)
    app.run()