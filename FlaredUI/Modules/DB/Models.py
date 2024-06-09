import json

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from FlaredUI.Modules.Auth import login_manager
from FlaredUI.Modules.DB import db
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from cryptography.fernet import Fernet
from FlaredUI.Config import encryption_key


# --- User Model ---
class User(UserMixin, db.Model):
    """Represents a user in the application."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    oauth = db.relationship('OAuth', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name != 'password_hash'}


# --- OAuth Provider Model ---
class OAuth(db.Model):
    """Stores OAuth information for a user."""
    __tablename__ = 'oauth'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('oauth_providers.id'), nullable=False)
    oauth_id = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))


# --- TLD Domain Model ---
class TLD(db.Model):
    """Stores top-level domain (TLD) information."""
    __tablename__ = 'tlds'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)


# Association table for many-to-many relationship between Tunnels and TLDs
tunnel_tlds = db.Table('tunnel_tlds',
                       db.Column('tunnel_id', db.Integer, db.ForeignKey('tunnels.id'), primary_key=True),
                       db.Column('tld_id', db.Integer, db.ForeignKey('tlds.id'), primary_key=True)
                       )


# --- Tunnel Model ---
class Tunnel(db.Model):
    """Stores Tunnel information."""
    __tablename__ = 'tunnels'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    uuid = db.Column(db.String(128), unique=True, nullable=False)
    domain = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), unique=True, nullable=False)
    tlds = db.relationship('TLD', secondary=tunnel_tlds, backref='tunnels')

    def to_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # Include TLDs for tunnels
        result['tlds'] = [tld.name for tld in self.tlds]
        return result


# --- Container Management Model ---
class ContainerManagement(db.Model):
    """Stores container management information."""
    __tablename__ = 'container_management'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    servers = relationship('Server', back_populates='container_manager')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }


# --- VMs Management Model ---
class VMManagement(db.Model):
    """Stores VMs management information."""
    __tablename__ = 'vm_management'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    servers = relationship('Server', back_populates='vm_manager')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }


# --- Server Model ---
class Server(db.Model):
    """Stores Individual Server Information."""
    __tablename__ = 'servers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    hostname = db.Column(db.String(80), nullable=False)
    ip_address = db.Column(db.String(80), nullable=False)
    ssh_port = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    container_manager_id = db.Column(db.Integer, db.ForeignKey('container_management.id'), nullable=False)
    vm_manager_id = db.Column(db.Integer, db.ForeignKey('vm_management.id'), nullable=False)
    namespace = db.Column(db.String(80), nullable=True)
    container_manager = db.relationship('ContainerManagement', back_populates='servers')
    vm_manager = db.relationship('VMManagement', back_populates='servers')
    containers = db.relationship('Container', backref='server', lazy=True, cascade="all, delete-orphan")
    vms = db.relationship('VMs', backref='server', lazy=True, cascade="all, delete-orphan")
    tlds = db.relationship('TLD', secondary=tunnel_tlds, backref='tunnels')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Converts the Server object to a dictionary, excluding the password hash."""
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name != 'password_hash'}

        # Include nested relationships as dictionaries (excluding server reference to avoid circularity)
        result['containers'] = [container.to_dict() for container in self.containers]
        result['vms'] = [vm.to_dict() for vm in self.vms]
        result['applications'] = [app.to_dict() for app in self.applications]

        # Include the container manager and VMs manager names
        if self.container_manager:
            result['container_manager'] = self.container_manager.name
        if self.vm_manager:
            result['vm_manager'] = self.vm_manager.name
        return result


# --- Container Model ---
class Container(db.Model):
    """Stores Individual Container Information."""
    __tablename__ = 'containers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    image = db.Column(db.String(255))
    state = db.Column(db.String(80))
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)
    hostname = db.Column(db.String(255))  # Subdomain for the container
    enabled = db.Column(db.Boolean, nullable=False, default=False)
    server = db.relationship('Server', backref=db.backref('containers', lazy=True))
    applications = db.relationship('Application', backref='container', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # Include applications for the container
        result['applications'] = [app.to_dict() for app in self.applications]
        return result


# --- Application Model ---
class Application(db.Model):
    """Stores information about non-containerized applications."""
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    exposed_ports = db.Column(db.JSON)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)
    container_id = db.Column(db.Integer, db.ForeignKey('containers.id', ondelete="CASCADE"), nullable=True)
    vm_id = db.Column(db.Integer, db.ForeignKey('vms.id', ondelete="SET NULL"), nullable=True)
    hostname = db.Column(db.String(255))  # Subdomain for the application
    enabled = db.Column(db.Boolean, nullable=False, default=False)
    tunnel_id = db.Column(db.Integer,
                          db.ForeignKey('tunnels.id', ondelete="SET NULL"))  # Can be associated with multiple tunnels
    tunnels = db.relationship('Tunnel', secondary='tunnel_applications', backref='applications')

    def to_dict(self):
        """Converts a model object to a dictionary, handling exposed_ports JSON field."""
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if self.exposed_ports:
            result['exposed_ports'] = []
            for protocol, ports in json.loads(self.exposed_ports).items():
                for port in ports:
                    result['exposed_ports'].append({'port': port, 'protocol': protocol})

        # Construct full hostnames
        if self.hostname and self.tunnel:
            result['hostnames'] = [f"{self.hostname}.{tld.name}" for tld in self.tunnel.tlds]
        return result

    # --- TunnelApplication Association Table ---
    tunnel_applications = db.Table('tunnel_applications',
                                   db.Column('tunnel_id', db.Integer, db.ForeignKey('tunnels.id'), primary_key=True),
                                   db.Column('application_id', db.Integer, db.ForeignKey('applications.id'),
                                             primary_key=True)
                                   )


# --- VMs Model ---
class VM(db.Model):
    """Stores Individual VMs Information."""
    __tablename__ = 'vms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    os_type = db.Column(db.String(80), nullable=False)
    os_name = db.Column(db.String(80), nullable=False)
    os_version = db.Column(db.String(80), nullable=False)
    cpu_cores = db.Column(db.Integer)
    memory = db.Column(db.Integer)
    storage = db.Column(db.Integer)
    state = db.Column(db.String(80))
    guest_os_id = db.Column(db.String(80))
    creation_time = db.Column(db.DateTime)
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'), nullable=False)
    server = db.relationship('Server', backref='vms')
    enabled = db.Column(db.Boolean, nullable=False, default=False)
    tunnel_id = db.Column(db.Integer, db.ForeignKey('tunnels.id', ondelete="SET NULL"))
    applications = db.relationship('Application', backref='vm', passive_deletes=True)

    def to_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # Include applications for the vm
        result['applications'] = [app.to_dict() for app in self.applications]
        return result


# --- ApiKeys Model ---
class ApiKeys(db.Model):
    """Stores Api Keys and establishes them as a user."""
    __tablename__ = 'api_keys'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255))
    value = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='api_keys')

    def to_dict(self):
        # Exclude 'value' for security reasons
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name != 'value'}


# --- AppSettings Model ---
class AppSettings(db.Model):
    """Stores App Settings."""
    __tablename__ = 'app_settings'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    value = db.Column(db.String(255))
    last_modified = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    modified_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='appsettings')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# --- PluginRepository Model ---
class PluginRepository(db.Model):
    """Represents a repository for plugins."""
    __tablename__ = 'plugin_repos'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    plugins = db.relationship('Plugin', backref='repository', lazy=True)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# --- Plugin Model ---
class Plugin(db.Model):
    """Represents a plugin."""
    __tablename__ = 'plugins'
    __table_args__ = (
        db.UniqueConstraint('name', 'repository_id', name='uq_plugin_name_repo'),  # Unique constraint
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'theme', 'backend', 'frontend'
    repository_id = db.Column(db.Integer, db.ForeignKey('plugin_repository.id'), nullable=False)
    version = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    entry_point = db.Column(db.String(255), nullable=True)
    requires = db.Column(db.JSON, nullable=True)  # Array of dependent plugin names
    installed = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=False)
    installed_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(timezone.utc))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- Custom Login Function (User.Name or User.Email) ---
@login_manager.request_loader
def load_user_from_request(request):
    """Allows login with either username or email."""
    username_or_email = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username_or_email).first()
    if not user:
        # If not found, try by email
        user = User.query.filter_by(email=username_or_email).first()
    if user and user.check_password(password):
        return user
    return None


# --- OAuth Provider Model ---
class OAuthProvider(db.Model):
    """Represents an OAuth provider."""
    __tablename__ = 'oauth_providers'

    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(80), nullable=False)
    client_id = db.Column(db.String(255), nullable=False)
    client_secret = db.Column(db.String(255), nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=False)
    provider_data = db.Column(db.JSON, nullable=True)

    def set_client_secret(self, secret):
        """Encrypts and sets the client secret."""
        f = Fernet(encryption_key)  # Create Fernet object
        self.client_secret = f.encrypt(secret.encode())  # Encrypt and store

    def get_client_secret(self):
        """Decrypts and returns the client secret."""
        f = Fernet(encryption_key)  # Create Fernet object
        return f.decrypt(self.client_secret).decode()  # Decrypt and return

    def to_dict(self):
        """Converts the OAuthProvider object to a dictionary, excluding the client secret."""
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name != 'client_secret'}
        return result
