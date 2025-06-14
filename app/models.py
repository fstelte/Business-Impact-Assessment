# app/models.py
# Definieert de database modellen met SQLAlchemy.

from . import db, login_manager
from sqlalchemy import Enum
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime
from pyotp import random_base32


@login_manager.user_loader
def load_user(user_id):
    """Callback functie voor Flask-Login om een gebruiker te laden."""
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    """Gebruikersmodel voor authenticatie."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False, default='user')
    # Nieuw veld om accountstatus bij te houden
    active = db.Column(db.Boolean(), nullable=False, default=False)
    mfa_secret = db.Column(db.String(32), nullable=True)
    mfa_enabled = db.Column(db.Boolean, default=False)

    items = db.relationship('ContextScope', backref='author', lazy='dynamic')

    # Override de is_active property van Flask-Login
    # Dit is cruciaal voor de integratie
      # Definieer is_active als een property
    @property
    def is_active(self):
        return self.active

    @is_active.setter
    def is_active(self, value):
        self.active = value

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.mfa_secret:
            self.mfa_secret = random_base32()
    
class ContextScope(db.Model):
    """Model voor de context en scope van de BIA."""
    __tablename__ = 'context_scope'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    responsible = db.Column(db.String(100))
    coordinator = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    last_update = db.Column(db.Date, default=date.today, onupdate=date.today)
    service_description = db.Column(db.Text)
    knowledge = db.Column(db.Text)
    interfaces = db.Column(db.Text)
    mission_critical = db.Column(db.String(255))
    support_contracts = db.Column(db.String(255))
    security_supplier = db.Column(db.String(255))
    user_amount = db.Column(db.Integer)
    scope_description = db.Column(db.Text)
    
    risk_assessment_human = db.Column(db.Boolean, default=False)
    risk_assessment_process = db.Column(db.Boolean, default=False)
    risk_assessment_technological = db.Column(db.Boolean, default=False)
    ai_model = db.Column(db.Boolean, default=False)
    
    project_leader = db.Column(db.String(100))
    risk_owner = db.Column(db.String(100))
    product_owner = db.Column(db.String(100))
    technical_administrator = db.Column(db.String(100))
    security_manager = db.Column(db.String(100))
    incident_contact = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    components = db.relationship('Component', back_populates='context_scope', cascade="all, delete-orphan")
    summary = db.relationship('Summary', uselist=False, back_populates='context_scope', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ContextScope {self.name}>'

class Component(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    info_type = db.Column(db.String(100))
    info_owner = db.Column(db.String(100))
    user_type = db.Column(db.String(100))
    process_dependencies = db.Column(db.String(100))
    description = db.Column(db.Text)
    context_scope_id = db.Column(db.Integer, db.ForeignKey('context_scope.id'), nullable=False)
    context_scope = db.relationship('ContextScope', back_populates='components')
    consequences = db.relationship('Consequences', back_populates='component', cascade="all, delete-orphan")
    availability_requirement = db.relationship('AvailabilityRequirements', back_populates='component', uselist=False, cascade="all, delete-orphan")
    ai_identificaties = db.relationship("AIIdentificatie", back_populates="component", cascade="all, delete-orphan")


    def __repr__(self):
        return f'<Component {self.name}>'

class Consequences(db.Model):
    __tablename__ = 'consequences'
    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey('component.id'), nullable=False)
    consequence_category = db.Column(db.String(255))  # We gebruiken een string om meerdere categorieën op te slaan
    security_property = db.Column(db.String(100))
    consequence_worstcase = db.Column(db.Text)
    justification_worstcase = db.Column(db.Text)
    consequence_realisticcase = db.Column(db.Text)
    justification_realisticcase = db.Column(db.Text)

    component = db.relationship('Component', back_populates='consequences')
    def get_categories(self):
        return self.consequence_category.split(',') if self.consequence_category else []
    
class AvailabilityRequirements(db.Model):
    __tablename__ = 'availability_requirements'
    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey('component.id'), nullable=False)
    mtd = db.Column(db.String(50))
    rto = db.Column(db.String(50))
    rpo = db.Column(db.String(50))
    masl = db.Column(db.String(50))

    component = db.relationship('Component', back_populates='availability_requirement')

    def __repr__(self):
        return f'<AvailabilityRequirements for Component {self.component_id}>'


class AIIdentificatie(db.Model):
    __tablename__ = 'ai_identificatie'
    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey('component.id'), nullable=False)
    category = db.Column(Enum(
        'No AI',
        'Unacceptable risk',
        'High risk',
        'Limited risk',
        'Minimal risk',
        name='ai_category'
    ), default='No AI')
    motivatie = db.Column(db.Text)

    component = db.relationship("Component", back_populates="ai_identificaties")
    
class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    context_scope_id = db.Column(db.Integer, db.ForeignKey('context_scope.id'), unique=True)
    context_scope = db.relationship('ContextScope', back_populates='summary')