from flask import Flask, render_template,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager,login_user, current_user,logout_user,login_required
from werkzeug.security import generate_password_hash, check_password_hash

app=Flask(__name__)
db=SQLAlchemy()
login_manager=LoginManager()

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
    data_ur=db.Column(db.DateTime)
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
    data=db.Column(db.DateTime)
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
def main():
    return render_template("admin_index.html")

@app.route('/logging',methods=['POST','GET'])
def logging():
    if(request.method=='POST'):
        login=request.form.get('login')
        haslo = request.form.get('password')
        if (login == "") or (haslo == ""):
            flash("wypelnij wszystkie pola!")
            return render_template(('admin_index.html'))
        x=User.query.filter_by(name=login).first()
        if x and check_password_hash(x.password,haslo):
            login_user(x)
            baza=[]
            lekarze= Lekarze.query.all()
            for i in lekarze:
                baza.append(i.id)
            return render_template(('admin_chose.html'),baza=baza)
        flash("nieprawidlowy login lub haslo!")
        return render_template(('admin_index.html'))

@app.route('/add',methods=['POST','GET'])
@login_required
def add():
    if (request.method == 'POST'):
        imie = request.form.get('name')
        nazwisko = request.form.get('surname')
        adres = request.form.get('address')
        email = request.form.get('email')
        telefon = request.form.get('phone')
        password = request.form.get('password')

        password_h=generate_password_hash(password)

        Lekarz=Lekarze(imie,nazwisko,adres,email,telefon,password_h)
        db.session.add(Lekarz)
        db.session.commit()

        spec1 = request.form.get('spec1')#on/None
        spec2 = request.form.get('spec2')
        spec3 = request.form.get('spec3')
        spec4 = request.form.get('spec4')
        spec5 = request.form.get('spec5')
        spec6 = request.form.get('spec6')

        id=0
        lekarze = Lekarze.query.all()
        for i in lekarze:
            id=int(i.id)    #id ostaniego lekarza (ostatnio dodanego)

        if (spec1 == "on"):
            spec = Specjalizacje("laryngolog",id)
            db.session.add(spec)
        if (spec2 == "on"):
            spec = Specjalizacje("proktolog",id)
            db.session.add(spec)
        if (spec3 == "on"):
            spec = Specjalizacje("dentysta",id)
            db.session.add(spec)
        if (spec4 == "on"):
            spec = Specjalizacje("okulista",id)
            db.session.add(spec)
        if (spec5 == "on"):
            spec = Specjalizacje("neurolog",id)
            db.session.add(spec)
        if (spec6 == "on"):
            spec = Specjalizacje("gastrolog",id)
            db.session.add(spec)
        db.session.commit()
        baza = []
        lekarze = Lekarze.query.all()
        for i in lekarze:
            baza.append(i.id)
        return render_template(('admin_chose.html'),baza=baza)


@app.route('/delete',methods=['POST','GET'])
@login_required
def delete():
    if (request.method == 'POST'):
        id_lekarza = int(request.form.get('selected'))#nie dodawaj do opcji ale do select'a
        gr = Specjalizacje.query.filter(Specjalizacje.id_lekarza == id_lekarza)
        for i in gr:
            db.session.delete(i)
        db.session.commit()
        gr = Lekarze.query.filter(Lekarze.id == id_lekarza).first()#pamietaj o first!
        db.session.delete(gr)
        db.session.commit()
        baza = []
        lekarze = Lekarze.query.all()
        for i in lekarze:
            baza.append(i.id)
        return render_template(('admin_chose.html'), baza=baza)

@app.route('/edit',methods=['POST','GET'])
@login_required
def edit():
    if (request.method == 'POST'):
        id_lekarza = int(request.form.get('selected'))#nie dodawaj do opcji ale do select'a
        gr = Lekarze.query.filter(Lekarze.id == id_lekarza).first()  # pamietaj o first!
        baza=[]
        baza.append(id_lekarza)
        baza.append(gr.imie)
        baza.append(gr.nazwisko)
        baza.append(gr.adres)
        baza.append(gr.email)
        baza.append(gr.telefon)
        baza.append(gr.password)


        #sprawdzam jakie checkboxy zaznaczyc
        bylo=False
        gr=Specjalizacje.query.filter(Specjalizacje.id_lekarza==id_lekarza)
        for i in gr:
            if (i.nazwa == "laryngolog"):  # 8
                bylo = True
                break
        if (bylo == True):
            baza.append("checked")
        else:
            baza.append("")
        bylo = False
        for i in gr:
            if (i.nazwa == "proktolog"):  # 9
                bylo = True
                break
        if (bylo == True):
            baza.append("checked")
        else:
            baza.append("")
        bylo = False
        for i in gr:
            if (i.nazwa == "dentysta"):  # 10
                bylo = True
                break
        if (bylo == True):
            baza.append("checked")
        else:
            baza.append("")
        bylo = False
        for i in gr:
            if (i.nazwa == "okulista"):  # 11
                bylo = True
                break
        if (bylo == True):
            baza.append("checked")
        else:
            baza.append("")
        bylo = False
        for i in gr:
            if (i.nazwa == "neurolog"):  # 12
                bylo = True
                break
        if (bylo == True):
            baza.append("checked")
        else:
            baza.append("")
        bylo = False
        for i in gr:
            if (i.nazwa == "gastrolog"):  # 13
                bylo = True
                break
        if (bylo == True):
            baza.append("checked")
        else:
            baza.append("")
        print(baza)
        return render_template(('admin_edit.html'), baza=baza)

@app.route('/cofnij',methods=['POST','GET'])
@login_required
def goback():
        lekarze = Lekarze.query.all()
        baza=[]
        for i in lekarze:
            baza.append(i.id)
        return render_template(('admin_chose.html'), baza=baza)

@app.route('/edited',methods=['POST','GET'])
@login_required
def edited():
    if (request.method == 'POST'):
        id_lekarza=request.form.get('id')
        imie = request.form.get('name')
        nazwisko = request.form.get('surname')
        adres = request.form.get('address')
        email = request.form.get('email')
        telefon = request.form.get('phone')
        password = request.form.get('password')

        spec1 = request.form.get('spec1')  # on/None
        spec2 = request.form.get('spec2')
        spec3 = request.form.get('spec3')
        spec4 = request.form.get('spec4')
        spec5 = request.form.get('spec5')
        spec6 = request.form.get('spec6')

        gr = Specjalizacje.query.filter(Specjalizacje.id_lekarza == id_lekarza)
        for i in gr:
            db.session.delete(i)
        db.session.commit()

        if (spec1 == "on"):
            spec = Specjalizacje("laryngolog", id_lekarza)
            db.session.add(spec)
        if (spec2 == "on"):
            spec = Specjalizacje("proktolog", id_lekarza)
            db.session.add(spec)
        if (spec3 == "on"):
            spec = Specjalizacje("dentysta", id_lekarza)
            db.session.add(spec)
        if (spec4 == "on"):
            spec = Specjalizacje("okulista", id_lekarza)
            db.session.add(spec)
        if (spec5 == "on"):
            spec = Specjalizacje("neurolog", id_lekarza)
            db.session.add(spec)
        if (spec6 == "on"):
            spec = Specjalizacje("gastrolog", id_lekarza)
            db.session.add(spec)
        db.session.commit()

        gr = Lekarze.query.filter(Lekarze.id == id_lekarza).first()
        gr.imie=imie
        gr.nazwisko=nazwisko
        gr.adres=adres
        gr.telefon=telefon
        gr.password=password
        gr.email=email
        db.session.commit()

        baza = []
        lekarze = Lekarze.query.all()
        for i in lekarze:
            baza.append(i.id)
        return render_template(('admin_chose.html'), baza=baza)

@app.route('/logout',methods=['POST','GET'])
@login_required
def logout():
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