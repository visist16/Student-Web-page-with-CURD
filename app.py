from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///week7_database.sqlite3'
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String,  nullable=False)
    last_name = db.Column(db.String)
    courses = db.relationship("Course", secondary="enrollments")


class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_name = db.Column(db.String,  nullable=False)
    course_description = db.Column(db.String)


class Enroll(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey("student.student_id"),
                            nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey("course.course_id"),
                           nullable=False)


@app.route('/')
def index():
    data = Student.query.all()
    return render_template('index.html', s_d=data)


@app.route("/student/create", methods=["GET", "POST"])
def add_student():
    if request.method == "GET":
        return render_template("add.html")
    else:

        roll = request.form["roll"]

        if Student.query.filter(Student.roll_number == roll).first():
            return render_template("exists.html", data="s")

        fn = request.form["f_name"]
        ln = request.form["l_name"]

        s = Student(roll_number=roll, first_name=fn, last_name=ln, courses=[])

        db.session.add(s)
        db.session.commit()

        return redirect('/')


@app.route("/student/<int:sid>")
def student_details(sid):
    sd = Student.query.filter(Student.student_id == sid).one()
    return render_template("student.html", s_d=sd)


@app.route("/student/<int:sid>/withdraw/<int:cid>")
def withdraw_course(sid, cid):
    sub = Enroll.query.filter_by(estudent_id=sid, ecourse_id=cid).first()
    db.session.delete(sub)
    db.session.commit()
    return redirect("/")


@app.route("/student/<int:sid>/delete")
def del_student(sid):
    data = Student.query.filter(Student.student_id == sid).one()
    db.session.delete(data)
    db.session.commit()
    return redirect('/')


@app.route("/student/<int:sid>/update", methods=["GET", "POST"])
def update_student(sid):
    if request.method == "GET":
        data = Student.query.filter(Student.student_id == sid).first()
        cd = Course.query.all()
        return render_template("update_s.html", s_d=data, c_d=cd)

    else:
        sub = request.form.getlist("course")[0]

        new = Student.query.filter_by(student_id=sid).first()

        new.first_name = request.form["f_name"]
        new.last_name = request.form["l_name"]
        [new.courses.append(Course.query.filter_by(course_id=int(
            sub)).first()) for i in sub if i not in new.courses]

        db.session.commit()
        return redirect('/')


@app.route('/courses')
def index_course():
    data = Course.query.all()
    return render_template("index_c.html", cd=data)


@app.route('/course/create', methods=["GET", "POST"])
def add_course():
    if request.method == "GET":
        return render_template("add_c.html")
    else:
        code = request.form["code"]
        if Course.query.filter_by(course_code=code).first():
            return render_template("exists.html", data="c")
        new_c = Course(course_code=request.form["code"], course_name=request.form["c_name"],
                       course_description=request.form["desc"])

        db.session.add(new_c)
        db.session.commit()
        return redirect('/courses')
