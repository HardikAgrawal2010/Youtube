from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os, base64
import random
import datetime
app = Flask(__name__)
MAX_SIZE = 50*1e+6
app.config['SQLALCHEMY_DATABASE_URI'] =  'sqlite:///database.db' #os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] =  'secret' #os.environ.get('SECRET')
app.config['MAX_CONTENT_LENGTH'] = MAX_SIZE
ALLOWED_EXTENSIONS =  'mp4,wav' #set(os.environ.get('ALLOWED').split(','))
ALL_CHARS = 'abcdefghijklmnopqrstuvxyz1234567890'
db = SQLAlchemy(app)

class Videos(db.Model):
	__tablename__ = 'videos'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.Text)
	views = db.Column(db.Integer)
	video = db.Column(db.LargeBinary)
	datetime = db.Column(db.String)
	code = db.Column(db.String)
	description = db.Column(db.Text)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
	videosl = Videos.query.order_by(Videos.id.desc()).all()
	return render_template('index.html', videosl = videosl)

@app.route('/upload', methods = ['GET', 'POST'])
def upload_file():
	if request.method=='POST':
		filea = request.files['file']
		desc = request.form.get('desc')
		name = request.form.get('name')
		if filea and allowed_file(filea.filename):
			encoded_string = base64.b64encode(filea.read())
			date_time = datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')
			code = ''.join(random.choice(ALL_CHARS) for i in range(5))
			test = Videos.query.filter_by(code=code).first()
			while test is not None:
				code = ''.join(random.choice(ALL_CHARS) for i in range(5))
				test = Videos.query.filter_by(code=code).first()
			vq = Videos(name=name, views=0, video = encoded_string, datetime=date_time, code = code, description=desc)
			db.session.add(vq)
			db.session.commit()
			flash('Video Uploaded Successfully.', 'success')
			return redirect(f'/video?v={code}')
		else:
			flash('Only Upload Supported Files or Video Files', 'error')
			return redirect('/upload')
	else:
		return render_template('upload.html')

@app.route('/search')
def search():
	q = request.args.get('q').lower()
	if ' ' in q:
		words = q.split(' ')
	else:
		words = [q]
	vd = Videos.query.all()
	vdw = []
	ans = []
	for v1 in vd:
		vdw.append(v1.name.split())
	print(vdw)
	for i in range(len(vd)):
		for word in words:
			ans1 = []
			for vdw1 in vdw[i]:
				if word == vdw1.lower() and vd[vdw.index(vdw[i])] not in ans:
					print(vdw.index(vdw[i]))
					ans.append(vd[vdw.index(vdw[i])])
	return render_template('search.html', videosl=ans)

@app.route('/video')
def video():
	v = request.args.get('v')
	if v:
		vd = Videos.query
		Videos.query.filter_by(code=v).first().views += 1
		db.session.commit()
		return render_template('video.html', code=v, vd=vd)
	else:
		return "404", 404

if __name__ == "__main__":
	app.run(debug=True)