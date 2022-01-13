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
    teacher_id = db.Column(db.ForeignKey('teacher.id'))
    key_stage = db.Column(db.ForeignKey('key_stage.key_stage'))

    # one (group) to many (student) relationship
    students = db.relationship('Student', backref='groups')

    def __init__(self, id, name, size, teacher_id, key_stage):
        self.id = id
        self.name = name
        self.size = size
        self.teacher_id = teacher_id
        self.key_stage = key_stage


class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer(), autoincrement=True, nullable=False, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    key_stage = db.Column(db.ForeignKey('key_stage.key_stage'))

    # many (questions) to one (quiz)
    questions = db.relationship('Question', backref='user')

    def __init__(self, name, key_stage):
        self.name = name
        self.key_stage = key_stage


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer(), autoincrement=True, nullable=False, primary_key=True)
    quiz_id = db.Column(db.ForeignKey('quizzes.id'))
    question_text = db.Column(db.String(), nullable=False)
    choices = db.Column(db.String(), nullable=False)
    correct_choice = db.Column(db.Integer(), nullable=False)

    def __init__(self, quiz_id, question_text, choices, correct_choice):
        self.quiz_id = quiz_id
        self.question_text = question_text
        self.choices = choices
        self.correct_choice = correct_choice


class StudentQuizScores(db.Model):
    __tablename__ = 'student_quiz_scores'
    id = db.Column(db.Integer(), autoincrement=True, nullable=False, primary_key=True)
    quiz_id = db.Column(db.ForeignKey('quizzes.id'))
    student_id = db.Column(db.ForeignKey('student.id'))
    score = db.Column(db.Integer())    # percentile score

    # one (quiz) to many (scores)
    quiz = db.relationship('Quiz', foreign_keys='StudentQuizScores.quiz_id')
    # one (student) to many (scores)
    student = db.relationship('Student', foreign_keys='StudentQuizScores.student_id')

    def __init__(self, quiz_id, student_id, score):
        self.quiz_id = quiz_id
        self.student_id = student_id
        self.score = score


# will likely be expanded to contain more data in future development
class KeyStage(db.Model):
    __tablename__ = 'key_stage'
    id = db.Column(db.Integer(), nullable=False, primary_key=True)
    key_stage = db.Column(db.String(), nullable=False)

    def __init__(self, key_stage):
        self.key_stage = key_stage


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

    group = Group(id="453153",
                  name="Class 4",
                  size=30,
                  teacher_id=teacher.id,
                  key_stage=1)


    student = Student(role="student",
                      name="James Newsome",
                      username="JamesNewsome5412",
                      password="TestTestTest5412",
                      last_login=None,
                      registered_on="19/12/2021 00:55:11",
                      group_id=group.id)

    quiz0 = Quiz(name="Test Quiz",
                 key_stage=1)

    question0 = Question(quiz_id=1,
                         question_text="Which of these is blue?",
                         choices="Red|Blue|Green|Yellow",
                         correct_choice=1)

    question1 = Question(quiz_id=1,
                         question_text="Choose the Odd number",
                         choices="8|2|3|4",
                         correct_choice=2)

    question2 = Question(quiz_id=1,
                         question_text="Choose the fish",
                         choices="dog|not fish|not fish|fish",
                         correct_choice=3)

    question3 = Question(quiz_id=1,
                         question_text="Pick Home",
                         choices="House|House|House|Home",
                         correct_choice=3)

    question4 = Question(quiz_id=1,
                         question_text="Black is the correct choice here",
                         choices="Black|Blue|Green|Yellow",
                         correct_choice=0)

    quiz1 = Quiz(name="Other Quiz",
                 key_stage=2)

    question5 = Question(quiz_id=2,
                         question_text="Which of these is blue?",
                         choices="Red|Blue|Green|Yellow",
                         correct_choice=1)

    question6 = Question(quiz_id=2,
                         question_text="Choose the Odd number",
                         choices="8|2|3|4",
                         correct_choice=2)

    question7 = Question(quiz_id=2,
                         question_text="Choose the fish",
                         choices="dog|not fish|not fish|fish",
                         correct_choice=3)

    question8 = Question(quiz_id=2,
                         question_text="Pick Home",
                         choices="House|House|House|Home",
                         correct_choice=3)

    question9 = Question(quiz_id=2,
                         question_text="Black is the correct choice here",
                         choices="Black|Blue|Green|Yellow",
                         correct_choice=0)

    key_stage1 = KeyStage(key_stage=1)
    key_stage2 = KeyStage(key_stage=1)

    db.session.add(teacher)
    db.session.commit()
    db.session.add(group)
    db.session.commit()
    db.session.add(student)
    db.session.add(quiz0)
    db.session.add(quiz1)
    db.session.add(question0)
    db.session.add(question1)
    db.session.add(question2)
    db.session.add(question3)
    db.session.add(question4)
    db.session.add(question5)
    db.session.add(question6)
    db.session.add(question7)
    db.session.add(question8)
    db.session.add(question9)
    db.session.add(key_stage1)
    db.session.add(key_stage2)
    group.teacher_id = teacher.id

    db.session.commit()

