import time
from datetime import datetime
import os
from flask import Flask, make_response, request
from config import Config
from flask import render_template,flash,redirect,url_for
import requests
import json
from flask import jsonify

app = Flask(__name__,template_folder='templates',static_folder='static',static_url_path='')
app.config.from_object(Config)
from flask_bootstrap import Bootstrap

from donor import Donor
from certificate import Certificate

bootstrap = Bootstrap(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['IMG_FOLDER'] = 'certificates'

from sqlite_helper import db_session

@app.route('/')
def welcome():
    return render_template('search.html')

@app.route('/donation/index')
def index():
    return render_template('search.html')

@app.route('/donation/certificate', methods=['GET'])
def certificate():
    id = request.args.get('id')
    donor=Donor.query.filter(Donor.id==id).first()
    file_dir = os.path.join(basedir, app.config['IMG_FOLDER'])
    if donor:
        no="WH2020012310{0:04d}".format(donor.id)
        certi_file="%s.png"%os.path.join(file_dir,no)
        if not os.path.exists(certi_file):
            amount="%.2f"%donor.amount
            cert=Certificate(donor.name,amount,no)
            cert.grant() 
        image_data = open(certi_file,"rb").read()
        response = make_response(image_data)
        response.headers['Content-Type'] = 'image/png'
        return response
        
	
def donor2dict(donor):
    dc=donor.__dict__
    if '_sa_instance_state' in dc:
        del dc['_sa_instance_state']
    return dc

@app.route('/donation/search',methods=['GET','POST'])
def search():
    key = request.args.get('key')
    print('Search '+key)
    donors=Donor.query.filter(Donor.name.like("%" + key + "%") if key is not None else "").all()

    dcs=[donor2dict(donor) for donor in donors]
    #donors=(json.dumps(dcs))
    print(dcs)
    #return jsonify(result=dcs)
    return make_response({'items':dcs})

@app.route('/donation/suggest',methods=['GET','POST'])
def suggest():
    key = request.args.get('key')
    print('Suggest for '+key)
    donors=Donor.query.filter(Donor.name.like("%" + key + "%") if key is not None else "").all()
    names=[donor.name for donor in donors]
    return make_response({'suggestions':names})

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.run(host='0.0.0.0',port=8080)
