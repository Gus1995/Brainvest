from flask import Flask, render_template, url_for, redirect, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from datetime import datetime
import random


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SECRET_KEY'] = 'thisisasecretkey'
    #--------------------------------------------------------------------------------------------
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False                                      #--
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 299  # Recycle connections after a certain period #-- CONFIGIRAÇÃO QUE PERMITE MULTITHREAD NO SQLITE 
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'connect_args': {'check_same_thread': False}}  #--
    #--------------------------------------------------------------------------------------------
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Classse que define o modelo de usuário 
    class User(db.Model, UserMixin):
        __tablename__ = 'User'
        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(20), nullable=False, unique=True)
        email = db.Column(db.String(80), nullable=False)
        senha = db.Column(db.String(80), nullable=False)
        status = db.Column(db.String(80), nullable=False)
        area = db.Column(db.String(80), nullable=False)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    class RegisterForm(FlaskForm):
        
        username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
        password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
        submit = SubmitField('Register')

        def validate_username(self, username):
            existing_user_username = User.query.filter_by(username=username.data).first()
            if existing_user_username:
                raise ValidationError('That username already exists. Please choose a different one.')
            

    class LoginForm(FlaskForm):
        username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
        password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
        submit = SubmitField('Login')

    class Person(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(100), nullable=False)
        senha = db.Column(db.String(100), nullable=False)

        @classmethod
        def retrieve_all(cls):
            return Person.query.all()    
        
        # classe declarada globalmente fora do router
    class Task(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        tarefa = db.Column(db.String(100), nullable=False)
        responsavel = db.Column(db.String(50), nullable=False)
        frequencia = db.Column(db.String(50), nullable=False)
        descricao = db.Column(db.String(50), nullable=True)
        status = db.Column(db.String(50), nullable=True)
        ultima_modificacao = db.Column(db.String(50), nullable=True)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home', username=form.username.data))
        return render_template('login.html', form=form)
    
    

    @app.route('/home')
    @login_required
    def home():
        tasks = Task.query.all()  # Query all tasks
        print (tasks)
        return render_template('home.html', tasks=tasks)
    
    @app.route('/middle')
    def middle():
        return render_template('middle.html')
    
    @app.route('/gerenciar')
    def gerenciar():
        return render_template('gerenciar.html')

    @app.route('/outros')
    def outros():
        return render_template('outros.html')
    
    @app.route('/projetos')
    def projetos():
        return render_template('projetos.html')

    @app.route('/fechamento')
    def fechamento():
        return render_template('fechamento.html')
    
    @app.route('/logout')
    def logout():
        session.clear()
        logout_user()
        return redirect(url_for('login'))
    
    #--- Features

    # Criar e gerenciar tasks




    @app.route('/create-task', methods=['POST'])
    def create_task():
        tarefa = request.form['tarefa']
        responsavel = request.form['responsavel']
        frequencia = request.form['frequencia']
        descricao = request.form['descricao']
        id = random.randint(1000, 9999)
        status = 'pendente'
        ultima_modificacao = None

        new_task = Task(tarefa=tarefa, responsavel=responsavel, frequencia=frequencia, descricao=descricao, id=id, status=status, ultima_modificacao=ultima_modificacao)

        db.session.add(new_task)
        db.session.commit()
        db.session.remove()

        return redirect(url_for('home'))
    
    @app.route('/delete-task/<int:task_id>', methods=['POST'])
    def delete_task(task_id):
        task = Task.query.get(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
        return redirect(url_for('home'))  
    
    @app.route('/check-task/<int:task_id>', methods=['POST'])
    def check_task(task_id):
        task = Task.query.get(task_id)
        timestamp = str(datetime.utcnow())
        timestamp = timestamp[0:16]
        if task:
            task.ultima_modificacao = timestamp
            task.status = 'Concluído'
            db.session.commit()
        return redirect(url_for('home'))  
    
    @app.route('/create-user', methods=['POST'])
    def create_user():
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        area= request.form['area']
        id = 'USER' + str(random.randint(1000, 9999))
        status = 'ativo'

        new_user = User(nome=nome, email=email, senha=senha, id=id, status=status, area=area)

        db.session.add(new_user)
        db.session.commit()
        db.session.remove()

        return redirect(url_for('gerenciar'))
    
    return app
    



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)