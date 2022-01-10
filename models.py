# created 4/12/2021 by Josh Oppenheimer
# model of the database. Has constructors for handling the database information within python
# (Will change as we change that details of variables and table interaction)

from app import db


# parent class of Student and Teacher, user_type defines which of the two they are.
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), autoincrement=True, nullable=False, primary_key=True)
    user_type = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False, unique=True)
    last_login = db.Column(db.String(50))
    registered_on = db.Column(db.String(50), nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'users', 'polymorphic_on': user_type}

    # constructor
    def __init__(self, user_type, name, username, password, last_login, registered_on):
        self.user_type = user_type
        self.name = name
        self.username = username
        self.password = password
        self.lastLogin = last_login
        self.registered_on = registered_on

    # string representation
    def __repr__(self):
        return '<User %r>' % self.username


# NOTE: group_id is used by both student and teacher and could be made a user property instead
class Student(User):
    __tablename__ = "student"
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    # foreign keys show one to one relationship
    group_id = db.Column(db.ForeignKey('groups.id'))

    # mapping relationship
    __mapper_args__ = {'polymorphic_identity': 'student'}

    def __init__(self, user_type, name, username, password, last_login, registered_on, group_id):
        super().__init__(user_type, name, username, password, last_login, registered_on)
        self.group_id = group_id


class Teacher(User):
    __tablename__ = 'teacher'
    # foreign keys show one to one relationship
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    email = db.Column(db.String(60), unique=True)

    group = db.relationship('Group')

    # mapping relationship
    __mapper_args__ = {'polymorphic_identity': 'teacher'}

    def __init__(self, user_type, name, username, password, last_login, registered_on, email):
        super().__init__(user_type, name, username, password, last_login, registered_on)
        self.email = email


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.String(6), nullable=False, primary_key=True)
    teacher_id = db.Column(db.ForeignKey('teacher.id'))
    key_stage = db.Column(db.String(10), nullable=False)

    # one (group) to many (student) relationship
    students = db.relationship('Student')

    def __init__(self, group_id, teacher_id, key_stage):
        self.id = group_id
        self.teacher_id = teacher_id
        self.key_stage = key_stage


class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer(), autoincrement=True, nullable=False, primary_key=True)
    name = db.Column(db.String(), nullable=False)

    questions = db.relationship('Question', backref='user')

    def __init__(self, name):
        self.name = name


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


def init_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

    teacher = Teacher(user_type="teacher",
                      name="Adam Smith",
                      username="AdamSmith@gmail.com",
                      password="testing123",
                      last_login=None,
                      registered_on="19/12/2021 00:55:11",
                      email="teacher@mail.com")

    group = Group(group_id="453153",
                  teacher_id=teacher.id,
                  key_stage=1)

    student = Student(user_type="student",
                      name="James Newsome",
                      username="JamesNewsome5412",
                      password="TestTestTest5412",
                      last_login=None,
                      registered_on="19/12/2021 00:55:11",
                      group_id=group.id)

    quiz = Quiz(name="Test Quiz")

    question0 = Question(id=1,
                         quiz_id=1,
                         question_text="Which of these is blue?",
                         choices="Red|Blue|Green|Yellow",
                         correct_choice=1)

    question1 = Question(id=2,
                         quiz_id=1,
                         question_text="Choose the Odd number",
                         choices="8|2|3|4",
                         correct_choice=2)

    question2 = Question(id=3,
                         quiz_id=1,
                         question_text="Choose the fish",
                         choices="dog|not fish|not fish|fish",
                         correct_choice=3)

    question3 = Question(id=4,
                         quiz_id=1,
                         question_text="Pick Home",
                         choices="House|House|House|Home",
                         correct_choice=3)

    question4 = Question(id=5,
                         quiz_id=1,
                         question_text="Black is the correct choice here",
                         choices="Black|Blue|Green|Yellow",
                         correct_choice=0)

    db.session.add(teacher)
    db.session.add(group)
    db.session.add(student)
    db.session.add(quiz)
    db.session.add(question0)
    db.session.add(question1)
    db.session.add(question2)
    db.session.add(question3)
    db.session.add(question4)
    db.session.commit()

