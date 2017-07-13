from flask import Flask, request, flash, url_for, redirect, render_template, abort, session
from model import db, User, Project, Timesheet, Customer, Month, hash_string
from datetime import datetime

VERSION="0.0-proto"

app = Flask(__name__)
app.config.from_pyfile('timesheet.cfg')
db.app = app
db.init_app(app)


@app.route('/')
def home():
	if not session.get('logged_in'):
		return(render_template('login.html'))
	else:
		user = User.query.filter_by(username=session['user']).first()
		action = session.get('action')
		month_id = session.get('month')
		if month_id:
			month = Month.query.filter_by(id = month_id).first()
		else:
			today = datetime.now()
			month = Month.query.filter_by(year = today.year).filter_by(month = today.month).first()
		timesheet_id = session.get('timesheet')
		ts = Timesheet.query.filter_by(id = timesheet_id).first()
		return(render_template('home.html', user=user, version=VERSION, month=month, ts=ts))


@app.route('/admin')
def admin():
	#not implemented
	return(redirect(url_for('home')))


@app.route('/do', methods=['POST'])
def do():
	if session.get('logged_in'):
		action = request.form.get('action')
		if action in ["get_month", "save_timesheet" ,"edit_timesheet"]:
			month_id = request.form.get('month')
			month = Month.query.filter_by(id = month_id).first()
			if month:
				session['month'] = month_id
		if action in ["save_timesheet" ,"edit_timesheet"]:
			timesheet_id = request.form.get('timesheet')
			ts = Timesheet.query.filter_by(id = timesheet_id).first()
		if action in ["edit_timesheet"] and ts:
			session['timesheet'] = ts.id
		if action in ["save_timesheet"]:
			project_id = request.form.get('project')
			days = request.form.get('days')
			user = User.query.filter_by(username=session['user']).first()
			project = Project.query.filter_by(id = project_id).first()
			if ts:
				ts.user = user
				ts.project = project
				ts.days = days
			else:
				ts = Timesheet(user, project, month, days)
			db.session.add(ts)
			print(ts)
			db.session.commit()
			print(ts)
		if action in ["get_month", "save_timesheet"]:
			session['timesheet'] = None
		session['action'] = action
	return(redirect(url_for('home')))


@app.route('/login', methods=['POST'])
def login():
	username = request.form['username']
	password = request.form['password']
	user = User.query.filter_by(username=username).first()
	if user and user.check_password(password):
		session['logged_in'] = True
		session['user'] = user.username
	else:
		flash('wrong password!')
	return(redirect(url_for('home')))


@app.route("/logout")
def logout():
	session['logged_in'] = False
	return(redirect(url_for('home')))


if __name__ == '__main__':
	db.create_all()
	if None == User.query.all():
		user = User('admin', 'admin@timesheet', 'admin', True)
		db.session.add(user)
		db.session.commit()
	app.run()