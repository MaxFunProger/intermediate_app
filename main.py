from flask import Flask
from data import db_session
from data.users import *
from data.news import *
from data.departments import *
from flask import render_template
from data.register import RegisterForm
from data.login import LoginForm
from data.add_job import JobForm
from flask import redirect
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/jobs")


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/addjob', methods=['GET', 'POST'])
@login_required
def add_job():
    db_session.global_init('db/blogs.sqlite')
    form = JobForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        if session.query(Jobs).filter(Jobs.job == form.job.data).first():
            return render_template('add_job.html',
                                   form=form,
                                   message="Такая работа уже есть")
        job = Jobs(
            team_leader=form.team_leader.data,
            job=form.job.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_finished=form.is_finished.data
        )
        session.add(job)
        session.commit()
        return redirect("/jobs")
    return render_template('add_job.html', form=form, current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    db_session.global_init('db/blogs.sqlite')
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/jobs")
        return render_template('login_form.html',
                               message="Wrong login or password",
                               form=form)
    return render_template('login_form.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    db_session.global_init('db/blogs.sqlite')
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register_form.html',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register_form.html',
                                   form=form,
                                   message="Такой колонист уже есть")
        user = User(
            address=form.address.data,
            speciality=form.speciality.data,
            position=form.position.data,
            age=form.age.data,
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/jobs')
    return render_template('register_form.html', form=form)


@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/jobs')
def jobs_list():
    db_session.global_init('db/blogs.sqlite')
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    users = session.query(User).all()
    return render_template('jobs.html', jobs=jobs, users=users)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
