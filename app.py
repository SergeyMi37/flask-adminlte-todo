from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babel import Babel, gettext as _, lazy_gettext as _l
from flask_restx import Api, Resource, fields
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import logging

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///todo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Flask-Babel setup
babel = Babel(app)

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Настройки Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'ru'  # Русский по умолчанию
app.config['BABEL_SUPPORTED_LOCALES'] = ['ru', 'en']  # Поддерживаемые языки

# Инициализация Babel с динамическим выбором локали
def get_locale():
    """Определяет текущий язык пользователя"""
    try:
        from flask import g
        # Сначала проверяем объект g, установленный в load_user_settings
        if hasattr(g, 'babel_locale') and g.babel_locale:
            logger.debug(f"get_locale from g: {g.babel_locale}")
            return g.babel_locale
        # Затем проверяем сессию
        lang = session.get('language')
        logger.debug(f"get_locale from session: {lang}")
        if not lang:
            # Если в сессии нет, загружаем из Options
            lang = get_option('language', category='user_settings')
            logger.debug(f"get_locale from options: {lang}")
        if not lang:
            # Если в Options нет, используем принятые языки браузера
            lang = request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])
            logger.debug(f"get_locale from browser: {lang}")
        logger.debug(f"get_locale returning: {lang}")
        return lang
    except Exception as e:
        logger.error(f"Error in get_locale: {e}")
        return app.config['BABEL_DEFAULT_LOCALE']

babel.init_app(app, locale_selector=get_locale)

@app.before_request
def load_user_settings():
    """Загружаем пользовательские настройки перед каждым запросом"""
    if 'language' not in session:
        session['language'] = get_option('language', category='user_settings')
    if 'theme' not in session:
        session['theme'] = get_option('theme', category='user_settings')
    if 'per_page' not in session:
        session['per_page'] = get_option('per_page', category='user_settings')
    
    # Обновляем локаль для Babel, если язык в сессии изменился
    from flask import g
    g.babel_locale = session.get('language', get_option('language', category='user_settings'))

# Удаляем дублирующиеся определения функций и инициализаций
# Все необходимые функции и инициализации уже определены ранее

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def is_admin():
    """Проверяет, является ли текущий пользователь администратором"""
    return current_user.is_authenticated and current_user.role.name == 'admin'

# Helper functions for Options
def get_option(name, default=None, user_id=None, category=None):
    option = Options.query.filter_by(name=name, user_id=user_id, category=category).first()
    result = option.value if option else default
    logger.debug(f"Getting option: {name} = {result} (category: {category})")
    return result

@app.template_global()
def get_option(name, default=None, user_id=None, category=None):
    option = Options.query.filter_by(name=name, user_id=user_id, category=category).first()
    result = option.value if option else default
    logger.debug(f"Getting option: {name} = {result} (category: {category})")
    return result

@app.template_global()
def get_g_value(attr_name, default=None):
    from flask import g
    return getattr(g, attr_name, default)

def set_option(name, value, description='', user_id=None, category=None):
    logger.debug(f"Setting option: {name} = {value} (category: {category})")
    option = Options.query.filter_by(name=name, user_id=user_id, category=category).first()
    if option:
        logger.debug(f"Updating existing option: {option.value} -> {value}")
        option.value = value
        option.description = description
    else:
        logger.debug(f"Creating new option: {name} = {value}")
        option = Options(name=name, value=value, description=description, user_id=user_id, category=category)
        db.session.add(option)
    db.session.commit()

# Flask-RESTX API setup
api = Api(app, version='1.0', title='Todo API',
          description='A comprehensive Todo API with user management, roles, and CRUD operations',
          doc='/api/docs')

ns = api.namespace('api/todos', description='Todo operations')
ns_options = api.namespace('api/options', description='Options operations')
ns_users = api.namespace('api/users', description='User operations')
ns_roles = api.namespace('api/roles', description='Role operations')

todo_model = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The todo unique identifier'),
    'title': fields.String(required=True, description='The todo title'),
    'description': fields.String(description='The todo description'),
    'completed': fields.Boolean(description='Todo completion status'),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp'),
    'updated_at': fields.DateTime(readonly=True, description='Last update timestamp'),
    'due_date': fields.DateTime(description='Due date for the todo')
})

option_model = api.model('Option', {
    'id': fields.Integer(readonly=True, description='The option unique identifier'),
    'name': fields.String(required=True, description='The option name'),
    'description': fields.String(description='The option description'),
    'user_id': fields.Integer(description='User ID (null for global options)'),
    'category': fields.String(description='Option category'),
    'value': fields.String(description='Option value')
})

role_model = api.model('Role', {
    'id': fields.Integer(readonly=True, description='The role unique identifier'),
    'name': fields.String(required=True, description='The role name'),
    'description': fields.String(description='The role description')
})

user_model = api.model('User', {
    'id': fields.Integer(readonly=True, description='The user unique identifier'),
    'username': fields.String(required=True, description='The username'),
    'email': fields.String(required=True, description='The user email'),
    'role_id': fields.Integer(required=True, description='The role ID'),
    'role': fields.Nested(role_model, description='The user role'),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp')
})

# Todo Model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None
        }

# Role Model
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))

    def __repr__(self):
        return f'<Role {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role = db.relationship('Role', backref=db.backref('users', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role_id': self.role_id,
            'role': self.role.to_dict() if self.role else None,
            'created_at': self.created_at.isoformat()
        }

# Options Model
class Options(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, nullable=True)  # None for global options
    category = db.Column(db.String(50))
    value = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'category': self.category,
            'value': self.value
        }

# API Routes
@ns.route('/')
class TodoList(Resource):
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo_model)
    def get(self):
        """List all todos"""
        if not current_user.is_authenticated:
            return {'message': 'Authentication required'}, 401
        return [todo.to_dict() for todo in Todo.query.all()]

    @ns.doc('create_todo')
    @ns.expect(todo_model)
    @ns.marshal_with(todo_model, code=201)
    def post(self):
        """Create a new todo"""
        if not current_user.is_authenticated:
            return {'message': 'Authentication required'}, 401
        data = request.get_json()
        new_todo = Todo(
            title=data['title'],
            description=data.get('description', ''),
            completed=data.get('completed', False),
            due_date=data.get('due_date')
        )
        db.session.add(new_todo)
        db.session.commit()
        return new_todo.to_dict(), 201

@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The todo identifier')
class TodoItem(Resource):
    @ns.doc('get_todo')
    @ns.marshal_with(todo_model)
    def get(self, id):
        """Fetch a todo given its identifier"""
        if not current_user.is_authenticated:
            return {'message': 'Authentication required'}, 401
        todo = Todo.query.get_or_404(id)
        return todo.to_dict()

    @ns.doc('update_todo')
    @ns.expect(todo_model)
    @ns.marshal_with(todo_model)
    def put(self, id):
        """Update a todo given its identifier"""
        if not current_user.is_authenticated:
            return {'message': 'Authentication required'}, 401
        todo = Todo.query.get_or_404(id)
        data = request.get_json()
        todo.title = data.get('title', todo.title)
        todo.description = data.get('description', todo.description)
        # Команда: добавь возможность чтобы при включения чекбокса выполнения элемента автоматичесики выставлялась текущая дата выполнения, и при выключении, то дата убиралась
        new_completed = data.get('completed', todo.completed)
        new_due_date = data.get('due_date', todo.due_date)

        if new_completed and not todo.completed:  # Переход из незавершенного в завершенное
            if not new_due_date:  # Если дата не была указана вручную
                new_due_date = datetime.utcnow()  # Автоматически устанавливаем текущую дату
        elif not new_completed and todo.completed:  # Переход из завершенного в незавершенное
            new_due_date = None  # Убираем дату выполнения

        todo.completed = new_completed
        todo.due_date = new_due_date
        db.session.commit()
        return todo.to_dict()

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        """Delete a todo given its identifier"""
        if not current_user.is_authenticated:
            return {'message': 'Authentication required'}, 401
        todo = Todo.query.get_or_404(id)
        db.session.delete(todo)
        db.session.commit()
        return '', 204
    
    # Options API Routes
    @ns_options.route('/')
    class OptionsList(Resource):
        @ns_options.doc('list_options')
        @ns_options.marshal_list_with(option_model)
        def get(self):
            """List all options"""
            if not current_user.is_authenticated:
                return {'message': 'Authentication required'}, 401
            return [option.to_dict() for option in Options.query.all()]

        @ns_options.doc('create_option')
        @ns_options.expect(option_model)
        @ns_options.marshal_with(option_model, code=201)
        def post(self):
            """Create a new option"""
            if not current_user.is_authenticated:
                return {'message': 'Authentication required'}, 401
            data = request.get_json()
            new_option = Options(
                name=data['name'],
                description=data.get('description', ''),
                user_id=data.get('user_id'),
                category=data.get('category', ''),
                value=data.get('value', '')
            )
            db.session.add(new_option)
            db.session.commit()
            return new_option.to_dict(), 201

    @ns_options.route('/<int:id>')
    @ns_options.response(404, 'Option not found')
    @ns_options.param('id', 'The option identifier')
    class OptionsItem(Resource):
        @ns_options.doc('get_option')
        @ns_options.marshal_with(option_model)
        def get(self, id):
            """Fetch an option given its identifier"""
            if not current_user.is_authenticated:
                return {'message': 'Authentication required'}, 401
            option = Options.query.get_or_404(id)
            return option.to_dict()

        @ns_options.doc('update_option')
        @ns_options.expect(option_model)
        @ns_options.marshal_with(option_model)
        def put(self, id):
            """Update an option given its identifier"""
            if not current_user.is_authenticated:
                return {'message': 'Authentication required'}, 401
            option = Options.query.get_or_404(id)
            data = request.get_json()
            option.name = data.get('name', option.name)
            option.description = data.get('description', option.description)
            option.user_id = data.get('user_id', option.user_id)
            option.category = data.get('category', option.category)
            option.value = data.get('value', option.value)
            db.session.commit()
            return option.to_dict()

        @ns_options.doc('delete_option')
        @ns_options.response(204, 'Option deleted')
        def delete(self, id):
            """Delete an option given its identifier"""
            if not current_user.is_authenticated:
                return {'message': 'Authentication required'}, 401
            option = Options.query.get_or_404(id)
            db.session.delete(option)
            db.session.commit()
            return '', 204

    # Users API Routes
    @ns_users.route('/')
    class UsersList(Resource):
        @ns_users.doc('list_users')
        @ns_users.marshal_list_with(user_model)
        def get(self):
            """List all users"""
            if not current_user.is_authenticated:
                return {'message': 'Authentication required'}, 401
            return [user.to_dict() for user in User.query.all()]

        @ns_users.doc('create_user')
        @ns_users.expect(user_model)
        @ns_users.marshal_with(user_model, code=201)
        def post(self):
            """Create a new user"""
            if not current_user.is_authenticated:
                return {'message': 'Authentication required'}, 401
            data = request.get_json()
            role = Role.query.get_or_404(data['role_id'])
            new_user = User(
                username=data['username'],
                email=data['email'],
                role=role
            )
            new_user.set_password(data.get('password', 'defaultpassword'))
            db.session.add(new_user)
            db.session.commit()
            return new_user.to_dict(), 201

    @ns_users.route('/<int:id>')
    @ns_users.response(404, 'User not found')
    @ns_users.param('id', 'The user identifier')
    class UserItem(Resource):
        @ns_users.doc('get_user')
        @ns_users.marshal_with(user_model)
        def get(self, id):
            """Fetch a user given its identifier"""
            if not current_user.is_authenticated:
                return {'message': 'Authentication required'}, 401
            user = User.query.get_or_404(id)
            return user.to_dict()

        @ns_users.doc('update_user')
        @ns_users.expect(user_model)
        @ns_users.marshal_with(user_model)
        def put(self, id):
            """Update a user given its identifier"""
            if not current_user.is_authenticated:
                return {'message': 'Authentication required'}, 401
            user = User.query.get_or_404(id)
            data = request.get_json()
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            if 'role_id' in data:
                user.role = Role.query.get_or_404(data['role_id'])
            if 'password' in data:
                user.set_password(data['password'])
            db.session.commit()
            return user.to_dict()

        @ns_users.doc('delete_user')
        @ns_users.response(204, 'User deleted')
        def delete(self, id):
            """Delete a user given its identifier"""
            if not current_user.is_authenticated:
                return {'message': 'Authentication required'}, 401
            user = User.query.get_or_404(id)
            db.session.delete(user)
            db.session.commit()
            return '', 204

    # Roles API Routes
    @ns_roles.route('/')
    class RolesList(Resource):
        @ns_roles.doc('list_roles')
        @ns_roles.marshal_list_with(role_model)
        def get(self):
            """List all roles"""
            if not current_user.is_authenticated:
                return {'message': 'Authentication required'}, 401
            return [role.to_dict() for role in Role.query.all()]

        @ns_roles.doc('create_role')
        @ns_roles.expect(role_model)
        @ns_roles.marshal_with(role_model, code=201)
        def post(self):
            """Create a new role"""
            if not current_user.is_authenticated:
                return {'message': 'Authentication required'}, 401
            data = request.get_json()
            new_role = Role(
                name=data['name'],
                description=data.get('description', '')
            )
            db.session.add(new_role)
            db.session.commit()
            return new_role.to_dict(), 201

    @ns_roles.route('/<int:id>')
    @ns_roles.response(404, 'Role not found')
    @ns_roles.param('id', 'The role identifier')
    class RoleItem(Resource):
        @ns_roles.doc('get_role')
        @ns_roles.marshal_with(role_model)
        def get(self, id):
            """Fetch a role given its identifier"""
            if not current_user.is_authenticated:
                return {'message': 'Authentication required'}, 401
            role = Role.query.get_or_404(id)
            return role.to_dict()

        @ns_roles.doc('update_role')
        @ns_roles.expect(role_model)
        @ns_roles.marshal_with(role_model)
        def put(self, id):
            """Update a role given its identifier"""
            if not current_user.is_authenticated:
                return {'message': 'Authentication required'}, 401
            role = Role.query.get_or_404(id)
            data = request.get_json()
            role.name = data.get('name', role.name)
            role.description = data.get('description', role.description)
            db.session.commit()
            return role.to_dict()

        @ns_roles.doc('delete_role')
        @ns_roles.response(204, 'Role deleted')
        def delete(self, id):
            """Delete a role given its identifier"""
            if not current_user.is_authenticated:
                return {'message': 'Authentication required'}, 401
            role = Role.query.get_or_404(id)
            db.session.delete(role)
            db.session.commit()
            return '', 204
    
    # Language and theme switching
@app.route('/language/<lang>')
def set_language(lang):
    if lang in app.config['BABEL_SUPPORTED_LOCALES']:
        session['language'] = lang
        set_option('language', lang, _('Selected interface language'), category='user_settings')
    else:
        logger.warning(f"Invalid language requested: {lang}")
    
    # Очистка кэша локали для обеспечения обновления
    from flask import g
    if hasattr(g, 'babel_locale'):
        delattr(g, 'babel_locale')
    
    # Принудительно обновляем контекст перевода
    from flask_babel import refresh
    refresh()
    
    # Возвращаем JSON ответ для AJAX запроса
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {'status': 'success', 'language': lang}
    
    return redirect(request.referrer or url_for('index'))

@app.route('/theme/<theme>')
def set_theme(theme):
    if theme in ['light', 'dark']:
        session['theme'] = theme
        set_option('theme', theme, 'Выбранная тема интерфейса', category='user_settings')
    return redirect(request.referrer or url_for('index'))

@app.route('/pagination/<int:per_page>')
def set_pagination(per_page):
    if per_page in [5, 10, 25, 50, 100]:
        session['per_page'] = per_page
        set_option('per_page', str(per_page), 'Количество элементов на странице', category='user_settings')
    return redirect(request.referrer or url_for('index'))

@app.route('/options')
@login_required
def view_options():
    if not is_admin():
        flash(_('Access denied. Administrator rights required.'))
        return redirect(url_for('index'))
    # Получаем все опции пользователя
    user_options = Options.query.filter_by(user_id=None, category='user_settings').all()
    return render_template('options.html', options=user_options)

@app.route('/admin/users')
@login_required
def manage_users():
    if not is_admin():
        flash(_('Access denied. Administrator rights required.'))
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@app.route('/admin/users/new', methods=['GET', 'POST'])
@login_required
def new_user():
    if not is_admin():
        flash(_('Access denied. Administrator rights required.'))
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role_id = request.form.get('role_id')

        if User.query.filter_by(username=username).first():
            flash(_('User with this username already exists'))
            return redirect(url_for('new_user'))
        if User.query.filter_by(email=email).first():
            flash(_('User with this email already exists'))
            return redirect(url_for('new_user'))

        role = Role.query.get_or_404(role_id)
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash(_('User created successfully!'))
        return redirect(url_for('manage_users'))
    roles = Role.query.all()
    return render_template('user_form.html', roles=roles)

@app.route('/admin/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if not is_admin():
        flash(_('Access denied. Administrator rights required.'))
        return redirect(url_for('index'))
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        role_id = request.form.get('role_id')
        password = request.form.get('password')

        if User.query.filter_by(username=user.username).first() and User.query.filter_by(username=user.username).first().id != id:
            flash(_('User with this username already exists'))
            return redirect(url_for('edit_user', id=id))
        if User.query.filter_by(email=user.email).first() and User.query.filter_by(email=user.email).first().id != id:
            flash(_('User with this email already exists'))
            return redirect(url_for('edit_user', id=id))

        user.role = Role.query.get_or_404(role_id)
        if password:
            user.set_password(password)
        db.session.commit()
        flash(_('User updated successfully!'))
        return redirect(url_for('manage_users'))
    roles = Role.query.all()
    return render_template('user_form.html', user=user, roles=roles)

@app.route('/admin/users/<int:id>/delete')
@login_required
def delete_user(id):
    if not is_admin():
        flash(_('Access denied. Administrator rights required.'))
        return redirect(url_for('index'))
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash(_("Can't delete yourself!"))
        return redirect(url_for('manage_users'))
    db.session.delete(user)
    db.session.commit()
    flash(_('User deleted successfully!'))
    return redirect(url_for('manage_users'))

@app.route('/admin/roles')
@login_required
def manage_roles():
    if not is_admin():
        flash(_('Access denied. Administrator rights required.'))
        return redirect(url_for('index'))
    roles = Role.query.all()
    return render_template('manage_roles.html', roles=roles)

@app.route('/admin/roles/new', methods=['GET', 'POST'])
@login_required
def new_role():
    if not is_admin():
        flash(_('Access denied. Administrator rights required.'))
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if Role.query.filter_by(name=name).first():
            flash(_('Role with this name already exists'))
            return redirect(url_for('new_role'))

        role = Role(name=name, description=description)
        db.session.add(role)
        db.session.commit()
        flash(_('Role created successfully!'))
        return redirect(url_for('manage_roles'))
    return render_template('role_form.html')

@app.route('/admin/roles/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_role(id):
    if not is_admin():
        flash(_('Access denied. Administrator rights required.'))
        return redirect(url_for('index'))
    role = Role.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if Role.query.filter_by(name=name).first() and Role.query.filter_by(name=name).first().id != id:
            flash(_('Role with this name already exists'))
            return redirect(url_for('edit_role', id=id))

        role.name = name
        role.description = description
        db.session.commit()
        flash(_('Role updated successfully!'))
        return redirect(url_for('manage_roles'))
    return render_template('role_form.html', role=role)

@app.route('/admin/roles/<int:id>/delete')
@login_required
def delete_role(id):
    if not is_admin():
        flash(_('Access denied. Administrator rights required.'))
        return redirect(url_for('index'))
    role = Role.query.get_or_404(id)
    if role.name == 'admin':
        flash(_("Can't delete admin role!"))
        return redirect(url_for('manage_roles'))
    if User.query.filter_by(role_id=id).first():
        flash(_("Can't delete role that is assigned to users!"))
        return redirect(url_for('manage_roles'))
    db.session.delete(role)
    db.session.commit()
    flash(_('Role deleted successfully!'))
    return redirect(url_for('manage_roles'))

# Web Routes
@app.route('/')
def api_docs():
    # Перенаправление на Swagger UI
    return redirect('/swaggerui')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        flash(_('Invalid username or password'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role_name = request.form.get('role', 'user')  # По умолчанию 'user'

        # Проверяем, существует ли пользователь
        if User.query.filter_by(username=username).first():
            flash(_('User with this username already exists'))
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash(_('User with this email already exists'))
            return redirect(url_for('register'))

        # Получаем роль
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            # Создаем роль, если не существует
            role = Role(name=role_name, description=_('Role {role_name}').format(role_name=role_name))
            db.session.add(role)
            db.session.commit()

        # Создаем пользователя
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash(_('Registration successful! You can now log in.'))
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def index():
    # Параметры пагинации
    page = request.args.get('page', 1, type=int)
    # Загружаем per_page из Options или сессии, по умолчанию 10
    per_page_value = get_option('per_page', session.get('per_page', 10), category='user_settings')
    if per_page_value is not None:
        per_page = int(per_page_value)
    else:
        per_page = 10

    # Если per_page из query string, используем его (но не сохраняем)
    query_per_page = request.args.get('per_page', type=int)
    if query_per_page and query_per_page in [5, 10, 25, 50, 100]:
        per_page = query_per_page

    # Валидация per_page
    if per_page not in [5, 10, 25, 50, 100]:
        per_page = 10

    # Получение данных с пагинацией
    pagination = Todo.query.paginate(page=page, per_page=per_page, error_out=False)
    todos = pagination.items

    return render_template('index.html', todos=todos, pagination=pagination, per_page=per_page)

@app.route('/todo/new', methods=['GET', 'POST'])
@login_required
def new_todo():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        due_date_str = request.form.get('due_date', '')
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None
        # Команда: добавь возможность чтобы при включения чекбокса выполнения элемента автоматичесики выставлялась текущая дата выполнения, и при выключении, то дата убиралась
        completed = 'completed' in request.form  # Получаем статус из чекбокса
        if completed and not due_date:
            due_date = datetime.utcnow()  # Автоматически устанавливаем текущую дату при завершении
        new_todo = Todo(title=title, description=description, due_date=due_date, completed=completed)
        db.session.add(new_todo)
        db.session.commit()
        flash(_('Todo created successfully!'))
        return redirect(url_for('index'))
    return render_template('todo_form.html')

@app.route('/todo/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_todo(id):
    todo = Todo.query.get_or_404(id)
    if request.method == 'POST':
        todo.title = request.form['title']
        todo.description = request.form.get('description', '')
        # Команда: добавь возможность чтобы при включения чекбокса выполнения элемента автоматичесики выставлялась текущая дата выполнения, и при выключении, то дата убиралась
        new_completed = 'completed' in request.form
        due_date_str = request.form.get('due_date', '')
        new_due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None

        if new_completed and not todo.completed:  # Переход из незавершенного в завершенное
            if not new_due_date:  # Если дата не была указана вручную
                new_due_date = datetime.utcnow()  # Автоматически устанавливаем текущую дату
        elif not new_completed and todo.completed:  # Переход из завершенного в незавершенное
            new_due_date = None  # Убираем дату выполнения

        todo.completed = new_completed
        todo.due_date = new_due_date
        db.session.commit()
        flash(_('Todo updated successfully!'))
        return redirect(url_for('index'))
    return render_template('todo_form.html', todo=todo)

@app.route('/todo/<int:id>/delete')
@login_required
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    flash(_('Todo deleted successfully!'))
    return redirect(url_for('index'))

@app.route('/todo/<int:id>/toggle')
@login_required
def toggle_todo(id):
    todo = Todo.query.get_or_404(id)
    # Команда: добавь возможность чтобы при включения чекбокса выполнения элемента автоматичесики выставлялась текущая дата выполнения, и при выключении, то дата убиралась
    was_completed = todo.completed
    todo.completed = not was_completed
    if todo.completed and not was_completed:  # Стало завершенным
        if not todo.due_date:  # Если дата не была установлена
            todo.due_date = datetime.utcnow()  # Автоматически устанавливаем текущую дату
    elif not todo.completed and was_completed:  # Стало незавершенным
        todo.due_date = None  # Убираем дату выполнения
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
