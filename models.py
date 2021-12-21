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

    # relationships

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

    def __init__(self, user_type, name, username, password, last_login, registered_on,
                 group_id):
        super().__init__(user_type, name, username, password, last_login, registered_on)
        self.group_id = group_id


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.String(6), nullable=False, primary_key=True, unique=True)
    name = db.Column(db.String(100), nullable=False)
    size = db.Column(db.Integer(), default=50, nullable=False)
    key_stage = db.Column(db.Integer(), nullable=True)
    teacher_id = db.Column(db.ForeignKey('teacher.id'))
    # one (group) to many (student) relationship
    students = db.relationship('Student')

    def __init__(self, id, name, size, key_stage):
        self.id = id
        self.name = name
        self.size = size
        self.key_stage = key_stage


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

    group = Group(432521, "class 4", 30, 1)
    teacher = Teacher("teacher", "Adam Smith", "AdamSmith@gmail.com", "testing123", None, "19/12/2021 00:55:11", group_id=group.id)
    student = Student("student", "James Newsome", "JamesNewsome5412", "TestTestTest5412", None, "19/12/2021 00:55:11", group_id=group.id)

    db.session.add(student)
    db.session.add(group)
    db.session.add(teacher)
    db.session.commit()
