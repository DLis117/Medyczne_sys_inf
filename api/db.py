from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import app

db = SQLAlchemy(app)

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
    telefon=db.Column(db.String(50))
    username=db.Column(db.String(50))
    password=db.Column(db.String(150))

    def __init__(self, imie,nazwisko,adres,email,telefon,username,password):
        self.imie = imie
        self.nazwisko=nazwisko
        self.adres=adres
        self.email=email
        self.telefon=telefon
        self.username=username
        self.password=password

class Pacjenci(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    imie=db.Column(db.String(25))
    nazwisko=db.Column(db.String(50))
    adres=db.Column(db.String(200))
    pesel=db.Column(db.String(11))
    email=db.Column(db.String(100))
    telefon=db.Column(db.String(50))
    username=db.Column(db.String(50))
    password=db.Column(db.String(150))

    def __init__(self, imie,nazwisko,adres,pesel,email,telefon,username,password):
        self.imie = imie
        self.nazwisko=nazwisko
        self.adres=adres
        self.pesel=pesel
        self.email=email
        self.telefon=telefon
        self.username=username
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
    data=db.Column(db.String(150))
    sala=db.Column(db.Integer)

    def __init__(self, nazwa, id_lekarza,id_pacjenta,godzina,data,sala):
        self.nazwa = nazwa
        self.id_lekarza = id_lekarza
        self.id_pacjenta=id_pacjenta
        self.godzina=godzina
        self.data=data
        self.sala=sala