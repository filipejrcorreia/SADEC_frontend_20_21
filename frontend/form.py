from flask import Flask, render_template, session, url_for
from flask_wtf import FlaskForm, RecaptchaField
from werkzeug.utils import redirect
from wtforms import SelectField, IntegerField
from wtforms.fields.html5 import IntegerRangeField
from wtforms.validators import NumberRange
import pandas
import requests 
import json
import unicodedata
backend_URL = "http://localhost:8000"

app = Flask(__name__)

#secret key to prevent csrf
app.config['SECRET_KEY'] = 'notsosecret'

#captcha to prevent bots from spam-filling 
app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lct2BkaAAAAABodhqluqvhUFP_NzJnJ0Ge0Ev1b'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Lct2BkaAAAAAESzee4aTb19KNdxgVo4WCgWcvts'

app.config['TESTING'] = True

#add locations
locations = pandas.read_csv('data_concelhos_new.csv')['concelho']

class Form(FlaskForm):
    age = IntegerField(u'Idade', validators=[NumberRange(min = 0, max = 120)]) # final values?
    location = SelectField(u'Concelho de residência ', choices = [tuple((location,location.title())) for location in locations.drop_duplicates()])
    cough = SelectField(u'Tem tosse? ', choices=[('yes', 'Sim'), ('no', 'Não')], default ='no')
    fever = SelectField(u'Tem febre (temperatura acima dos 37,8º)? ', choices=[('yes', 'Sim'), ('no', 'Não')], default ='no')
    muscle_sore = SelectField(u'Tem tensão e dores musculares ou sente os músculos doridos? ', choices=[('yes', 'Sim'), ('no', 'Não')], default ='no')
    fatigue = SelectField(u'Sente fadiga? ', choices=[('yes', 'Sim'), ('no', 'Não')], default ='no')
    sore_throat = SelectField(u'Tem dor de garganta? ', choices=[('yes', 'Sim'), ('no', 'Não')], default ='no')
    lack_of_air = SelectField(u'Tem falta de ar? ', choices=[('yes', 'Sim'), ('no', 'Não')], default ='no')
    loss_of_smell = SelectField(u'Perdeu o olfato/cheiro ', choices=[('yes', 'Sim'), ('no', 'Não')], default ='no')
    loss_of_taste = SelectField(u'Perdeu o paladar/sabor? ', choices=[('yes', 'Sim'), ('no', 'Não')], default ='no')
    headache = SelectField(u'Tem dor de cabeça? ', choices=[('yes', 'Sim'), ('no', 'Não')], default ='no')
    type_of_headache = SelectField(u'Qual destes tipos de dor de cabeça julga ter? ', choices=[('migraine', 'Enxaqueca'), ('tension', 'Tensão'), ('cluster', 'Cefaleia'), ('other', 'Não tenho a certeza / outra')], 
    default ='migraine')
    intensity = IntegerRangeField(label=u'Intensidade da dor de cabeça')
    contact = SelectField(u'Esteve em contacto com alguém infetado recentemente? ', choices=[('yes', 'Sim'), ('no', 'Não')], default ='no')
    recaptcha = RecaptchaField()

@app.route('/result')
def result():
    userAnswers = session['userAnswers']
    try:
        results = requests.post(backend_URL, json = userAnswers)
        print(unicodedata.normalize("NFKD",results.text))
    except requests.exceptions.RequestException as exception:
        raise SystemExit(exception)
    
    return render_template('result.html',results=results.text)

# take any path
@app.route('/', defaults={'path': ''}, methods = ['GET','POST'])
@app.route('/<path:path>', methods = ['GET','POST'])
def catch_all(path):
    form = Form()

    # validate submission
    if form.validate_on_submit():
        #return 'Submitted!'
        intensity = 0
        type_of_headache = None
        if form.headache.data == 'yes':
            type_of_headache = form.intensity.data
            intensity = form.intensity.data

        userAnswers = {
            "age" : form.age.data,
            "location" : form.location.data,
            "cough" : form.cough.data,
            "fever" : form.fever.data,
            "muscle_sore" : form.muscle_sore.data,
            "fatigue" : form.fatigue.data,
            "sore_throat" : form.sore_throat.data,
            "labored_respiration" : form.lack_of_air.data,
            "loss_of_smell" : form.loss_of_smell.data,
            "loss_of_taste" : form.loss_of_taste.data,
            "headache" : form.headache.data,
            "type_of_headache": type_of_headache,
            "intensity": intensity,
            "high_risk_interactions": form.contact.data
        }
        print(userAnswers)
        session['userAnswers'] = userAnswers

        return redirect(url_for('.result'))

    return render_template('form.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)