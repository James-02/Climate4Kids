# created 4/12/2021 by Josh Oppenheimer
# model of the database. Has constructors for handling the database information within python
# (Will change as we change that details of variables and table interaction)
from flask_login import UserMixin

from app import db
from werkzeug.security import generate_password_hash


# parent class of Student and Teacher, role defines which of the two they are.
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), autoincrement=True, nullable=False, primary_key=True)
    role = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, unique=True)
    last_login = db.Column(db.String(50))
    registered_on = db.Column(db.String(50), nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'users', 'polymorphic_on': role}

    # constructor
    def __init__(self, role, name, username, password, last_login, registered_on):
        self.role = role
        self.name = name
        self.username = username
        self.password = generate_password_hash(password)
        self.lastLogin = last_login
        self.registered_on = registered_on


# NOTE: group_id is used by both student and teacher and could be made a user property instead
class Student(User):
    __tablename__ = "student"
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    # foreign keys show one to one relationship
    group_id = db.Column(db.ForeignKey('groups.id'))

    # relationships

    # mapping relationship
    __mapper_args__ = {'polymorphic_identity': 'student'}

    def __init__(self, role, name, username, password, last_login, registered_on, group_id):
        super().__init__(role, name, username, password, last_login, registered_on)
        self.group_id = group_id


#  Decryption of group codes considered, decided it was unneccessary,
#   however implementation in future is still possible.
class Teacher(User):
    __tablename__ = 'teacher'
    # foreign keys show one to one relationship
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    email = db.Column(db.String(60), unique=True)

    # one (teacher) to many (groups) relationship
    group = db.relationship('Group', uselist=True)

    # mapping relationship
    __mapper_args__ = {'polymorphic_identity': 'teacher'}

    def __init__(self, role, name, username, password, last_login, registered_on, email):
        super().__init__(role, name, username, password, last_login, registered_on)
        self.email = email


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.String(6), nullable=False, primary_key=True, unique=True)
    name = db.Column(db.String(100), nullable=False)
    size = db.Column(db.Integer(), default=50, nullable=False)
    key_stage = db.Column(db.Integer(), nullable=True)
    teacher_id = db.Column(db.ForeignKey('teacher.id'))
    # one (group) to many (student) relationship
    students = db.relationship('Student', backref='groups')

    def __init__(self, id, name, size, key_stage, teacher_id):
        self.id = id
        self.name = name
        self.size = size
        self.key_stage = key_stage
        self.teacher_id = teacher_id


class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer(), autoincrement=True, nullable=False, primary_key=True)
    student_id = db.Column(db.ForeignKey('student.id'))
    score = db.Column(db.Integer(), nullable=False)

    # many (quiz) to one (student) relationship
    student = db.relationship('Student')

    def __init__(self, score, student_id):
        self.score = score
        self.student_id = student_id


def init_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

    teacher = Teacher(role="teacher",
                      name="Adam Smith",
                      username="AdamSmith3412",
                      password="Testing123",
                      last_login=None,
                      registered_on="19/12/2021 00:55:11",
                      email="diversitycontracters1@gmail.com")

    teacher2 = Teacher(role="teacher",
                      name="Adam Smith2",
                      username="AdamSmith34122",
                      password="Testing123",
                      last_login=None,
                      registered_on="19/12/2021 00:55:12",
                      email="diversitycontracters12@gmail.com")

    group = Group(id="453153",
                  name="Class 4",
                  size=30,
                  key_stage=1,
                  teacher_id=teacher.id)

    student = Student(role="student",
                      name="James Newsome",
                      username="JamesNewsome5412",
                      password="TestTestTest5412",
                      last_login=None,
                      registered_on="19/12/2021 00:55:11",
                      group_id=group.id)

    db.session.add(teacher)
    db.session.commit()
    db.session.add(group)
    db.session.commit()
    db.session.add(student)
    db.session.commit()
    db.session.add(teacher2)
    db.session.commit()


    group.teacher_id = teacher.id
    db.session.commit()

