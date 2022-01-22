from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegistrationForm(FlaskForm):
    name = StringField('Imię',
                       validators=[DataRequired(), Length(max = 25)])
    surname = StringField('Nazwisko',
                       validators=[DataRequired(), Length(max = 50)])
    date_of_birth = StringField('data_urodzenia',
                          validators=[DataRequired(), Length(max=50)])
    adress = StringField('Adres',
                       validators=[DataRequired(), Length(max = 200)])
    pesel = StringField('PESEL',
                       validators=[DataRequired(), Length(max = 11)])
    phone_number = StringField('Numer Telefonu',
                       validators=[DataRequired(), Length(max = 50)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Hasło',
                             validators=[DataRequired()])
    confirm_password = PasswordField('Potwierdź Hasło',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Zarejestruj się')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    remember = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj')

# class VisitForm(FlaskForm):
