from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from hashlib import sha224

def hash_string(string):
	"Retourne le hash de la chaine passée en paramètre."
	return(sha224(string.encode('utf8')).hexdigest())

def to_json(obj):
	return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


db = SQLAlchemy()


join_project_user = db.Table('joint_project_user', db.Model.metadata,
	db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('project_id', db.Integer, db.ForeignKey('project.id'))
)


class Timesheet(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	days = db.Column(db.Numeric(2,2))
	project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
	project = db.relationship("Project", back_populates="timesheets")
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	user = db.relationship("User", back_populates="timesheets")
	month_id = db.Column(db.Integer, db.ForeignKey('month.id'))
	month = db.relationship("Month", back_populates="timesheets")

	def __init__(self, user, project, month, days=0):
		self.user = user
		self.project = project
		self.month = month
		self.days = days

	def __repr__(self):
		return("<Timesheet[%s] %s day(s)>" % (self.id, self.days))

	def delete(self):
		db.session.query(Timesheet).filter(Timesheet.id == self.id).delete(synchronize_session='evaluate')
		db.session.commit()


class Month(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	year = db.Column(db.Integer)
	month = db.Column(db.Integer)
	days = db.Column(db.Numeric(2,2))
	closed = db.Column(db.Boolean)
	timesheets = db.relationship("Timesheet", back_populates="month")

	def __init__(self, year, month, days=0, closed=False):
		self.year = year
		self.month = month
		self.days = days
		self.closed = closed

	def __repr__(self):
		return("<Month[%s] %s-%s>" % (self.id, self.year, self.month))


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	password = db.Column(db.String(120))
	mail = db.Column(db.String(120), unique=True)
	name = db.Column(db.String(120))
	admin = db.Column(db.Boolean)
	timesheets = db.relationship("Timesheet", back_populates="user")
	projects = db.relationship("Project", secondary=join_project_user)

	def __init__(self, username, name, mail, password='pa$$word', admin=False):
		self.username = username
		self.password = hash_string(password)
		self.name = name
		self.mail = mail
		self.admin = admin

	def __repr__(self):
		return("<User[%s] %s>" % (self.id, self.username))

	def check_password(self, password):
		if self.password == hash_string(password):
			return(True)
		else:
			return(False)

	def get_open_months(self):
		return(Month.query.filter_by(closed = False).all())

	def get_projects(self):
		return(self.projects)

	def get_timesheets_for_month(self, month):
		r = []
		for t in self.timesheets:
			if t.month == month:
				r.append(t)
		return(r)

	def get_all_timesheets_for_month(self, month):
		return(Timesheet.query.filter_by(month = month).all())


class Project(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
	customer = db.relationship("Customer", back_populates="projects")
	timesheets = db.relationship("Timesheet", back_populates="project")
	users = db.relationship("User", secondary=join_project_user)

	def __init__(self, name, customer):
		self.name = name
		self.customer = customer

	def __repr__(self):
		return("<Project[%s] %s>" % (self.id, self.name))


class Customer(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	projects = db.relationship("Project", back_populates="customer")

	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return("<Customer[%s] %s>" % (self.id, self.name))
