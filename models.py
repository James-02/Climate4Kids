# created 4/12/2021 by Josh Oppenheimer
# model of the database. Has constructors for handling the database information within python
# (Will change as we change that details of variables and table interaction)
from app import db, app
from flask_login import UserMixin
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


#  Decryption of group codes considered, decided it was unnecessary however, implementation in future is still possible.
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
    score = db.Column(db.Integer())  # percentile score

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


def create_models():
    """ Function to define testing instances """
    questions, quizzes = [], []
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
                  teacher_id=None,
                  key_stage=1)

    student = Student(role="student",
                      name="James Newsome",
                      username="JamesNewsome5412",
                      password="TestTestTest5412",
                      last_login=None,
                      registered_on="19/12/2021 00:55:11",
                      group_id=group.id)

    quizzes.append(Quiz(name="Weather and Climate",
                        key_stage=1))

    questions.append(Question(quiz_id=1,
                              question_text="What is Weather?",
                              choices="If it's raining or not"
                                      "|The daily conditions in a small area"
                                      "|The average temperature"
                                      "|The number of clouds in the sky",
                              correct_choice=1))

    questions.append(Question(quiz_id=1,
                              question_text="What is Climate?",
                              choices="The long term weather pattern over a large area"
                                      "|The average temperature of the world"
                                      "|The weather at the end of the year"
                                      "|The weather over a large area",
                              correct_choice=0))

    questions.append(Question(quiz_id=1,
                              question_text="What is the Climate like in the United Kingdom?",
                              choices="Cool summers and warm winters"
                                      "|Very hot and windy all year"
                                      "|Cool winters and warm summers"
                                      "|Very Cold with no rain all year",
                              correct_choice=2))

    questions.append(Question(quiz_id=1,
                              question_text="What is the Climate like in the desert?",
                              choices="Cold with lots of snowfall"
                                      "|Hot and lots of rainfall"
                                      "|Cold and windy"
                                      "|Very hot and dry all year",
                              correct_choice=3))

    questions.append(Question(quiz_id=1,
                              question_text="What is the Climate like in the rainforest",
                              choices="Hot all year and very wet"
                                      "|Hot and dry"
                                      "|Cold and lots of rainfall"
                                      "|Very hot and windy",
                              correct_choice=0))

    quizzes.append(Quiz(name="Climate Change",
                        key_stage=2))

    questions.append(Question(quiz_id=2,
                              question_text="What is Climate Change?",
                              choices="Describes the weather changing each day"
                                      "|Describes the earth moving further away from the sun"
                                      "|When the seasons change, for example: spring to summer"
                                      "|Describes how the planets climates change over a long period of time ",
                              correct_choice=3))

    questions.append(Question(quiz_id=2,
                              question_text="What is Global Warming?",
                              choices="Describes the change in the Earth's average temperature over a long period"
                                      "|Describes the increase in the number of clouds around the world"
                                      "|The cooling of the Earth and increase of rainfall"
                                      "|Describes the increase in human body temperature over time",
                              correct_choice=0))

    questions.append(Question(quiz_id=2,
                              question_text="Which of these is not a greenhouse gas?",
                              choices="Water Vapour"
                                      "|Acid"
                                      "|Carbon Dioxide"
                                      "|Methane",
                              correct_choice=1))

    questions.append(Question(quiz_id=2,
                              question_text="Why is it important that the levels of greenhouse gases in our atmosphere "
                                            "remain roughly the same?",
                              choices="So that we can breath more easily"
                                      "|To maintain a stable climate"
                                      "|To help keep us cool"
                                      "|To keep the sky blue",
                              correct_choice=1))

    questions.append(Question(quiz_id=2,
                              question_text="What is causing the sharp rise in carbon dioxide levels in our "
                                            "atmosphere today?",
                              choices="The Earth's natural cycle"
                                      "|Human actions such as burning fossil fuels, farming and deforestation"
                                      "|Sun spots and volcanic activity"
                                      "|The sun getting hotter",
                              correct_choice=0))

    key_stages = [KeyStage(key_stage=1), KeyStage(key_stage=2)]

    student_quiz_score0 = StudentQuizScores(quiz_id=1,
                                            student_id=2,
                                            score=80)

    student_quiz_score1 = StudentQuizScores(quiz_id=2,
                                            student_id=2,
                                            score=60)

    admin = Teacher(role="teacher",
                    name="admin",
                    username="admin",
                    password="Unguessable12*",
                    last_login=None,
                    registered_on="19/12/2021 00:55:11",
                    email="jamjar6922@gmail.com")

    admin_group = Group(id="-1",
                        name="admin group",
                        size=1,
                        teacher_id=admin.id,
                        key_stage=0)

    db.session.add(teacher)
    db.session.add(admin)
    db.session.commit()

    db.session.add(group)
    db.session.add(admin_group)
    db.session.add(student)

    for key_stage in key_stages:
        db.session.add(key_stage)

    for quiz in quizzes:
        db.session.add(quiz)

    for question in questions:
        db.session.add(question)

    db.session.add(student_quiz_score0)
    db.session.add(student_quiz_score1)

    group.teacher_id = teacher.id
    admin_group.teacher_id = admin.id
    db.session.commit()


def init_db():
    """ Database table creation using models """
    db.init_app(app)
    with app.app_context():
        db.drop_all()
        db.create_all()
        create_models()
        db.session.commit()
        print(f"\n===== Sucessfully created {db} ======")


if __name__ == "__main__":
    init_db()
