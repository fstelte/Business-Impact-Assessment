# app/models.py
# Definieert de database modellen met SQLAlchemy.

from . import db, login_manager
from sqlalchemy import Enum, Text, event
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime
from pyotp import random_base32
from datetime import date


@login_manager.user_loader
def load_user(user_id):
    """Callback functie voor Flask-Login om een gebruiker te laden."""
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    """Gebruikersmodel voor authenticatie."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), index=True, unique=True, nullable=False)  # Behouden voor index/unique
    email = db.Column(db.String(255), index=True, unique=True, nullable=False)     # Behouden voor index/unique
    password_hash = db.Column(db.String(512))  # Behouden voor hash opslag
    role = db.Column(db.String(50), nullable=False, default='user')  # Behouden voor enum-achtige waarden
    active = db.Column(db.Boolean(), nullable=False, default=False)
    mfa_secret = db.Column(db.String(64), nullable=True)  # Behouden voor technische waarden
    mfa_enabled = db.Column(db.Boolean, default=False)

    items = db.relationship('ContextScope', backref='author', lazy='dynamic')

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

    @property
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
    name = db.Column(Text, nullable=False)                    # Gewijzigd naar Text
    responsible = db.Column(Text)                             # Gewijzigd naar Text
    coordinator = db.Column(Text)                             # Gewijzigd naar Text
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    last_update = db.Column(db.Date, default=date.today, onupdate=date.today)
    service_description = db.Column(Text)
    knowledge = db.Column(Text)
    interfaces = db.Column(Text)
    mission_critical = db.Column(Text)                        # Gewijzigd naar Text
    support_contracts = db.Column(Text)                       # Gewijzigd naar Text
    security_supplier = db.Column(Text)                       # Gewijzigd naar Text
    user_amount = db.Column(db.Integer)
    scope_description = db.Column(Text)
    
    risk_assessment_human = db.Column(db.Boolean, default=False)
    risk_assessment_process = db.Column(db.Boolean, default=False)
    risk_assessment_technological = db.Column(db.Boolean, default=False)
    ai_model = db.Column(db.Boolean, default=False)
    
    project_leader = db.Column(Text)                          # Gewijzigd naar Text
    risk_owner = db.Column(Text)                              # Gewijzigd naar Text
    product_owner = db.Column(Text)                           # Gewijzigd naar Text
    technical_administrator = db.Column(Text)                 # Gewijzigd naar Text
    security_manager = db.Column(Text)                        # Gewijzigd naar Text
    incident_contact = db.Column(Text)                        # Gewijzigd naar Text

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    components = db.relationship('Component', back_populates='context_scope', cascade="all, delete-orphan")
    summary = db.relationship('Summary', uselist=False, back_populates='context_scope', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ContextScope {self.name}>'

class Component(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(Text, nullable=False)                    # Gewijzigd naar Text
    info_type = db.Column(Text)                               # Gewijzigd naar Text
    info_owner = db.Column(Text)                              # Gewijzigd naar Text
    user_type = db.Column(Text)                               # Gewijzigd naar Text
    process_dependencies = db.Column(Text)                    # Gewijzigd naar Text
    description = db.Column(Text)
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
    consequence_category = db.Column(Text)                    # Gewijzigd naar Text
    security_property = db.Column(Text)                       # Gewijzigd naar Text
    consequence_worstcase = db.Column(Text)
    justification_worstcase = db.Column(Text)
    consequence_realisticcase = db.Column(Text)
    justification_realisticcase = db.Column(Text)

    component = db.relationship('Component', back_populates='consequences')
    
    def get_categories(self):
        return self.consequence_category.split(',') if self.consequence_category else []
    
class AvailabilityRequirements(db.Model):
    __tablename__ = 'availability_requirements'
    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey('component.id'), nullable=False)
    mtd = db.Column(Text)                                     # Gewijzigd naar Text
    rto = db.Column(Text)                                     # Gewijzigd naar Text
    rpo = db.Column(Text)                                     # Gewijzigd naar Text
    masl = db.Column(Text)                                    # Gewijzigd naar Text

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
    motivatie = db.Column(Text)

    component = db.relationship("Component", back_populates="ai_identificaties")
    
class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(Text)
    context_scope_id = db.Column(db.Integer, db.ForeignKey('context_scope.id'), unique=True)
    context_scope = db.relationship('ContextScope', back_populates='summary')

def update_context_scope_last_update(mapper, connection, target):
    if isinstance(target, ContextScope):
        target.last_update = date.today()
        return

    context_scope = None

    if isinstance(target, Component):
        context_scope = target.context_scope
    elif isinstance(target, Consequences):
        component = getattr(target, "component", None)
        if component is not None:
            context_scope = component.context_scope
    elif isinstance(target, AvailabilityRequirements):
        component = getattr(target, "component", None)
        if component is not None:
            context_scope = component.context_scope
    elif isinstance(target, AIIdentificatie):
        component = getattr(target, "component", None)
        if component is not None:
            context_scope = component.context_scope
    elif isinstance(target, Summary):
        context_scope = target.context_scope

    if context_scope:
        context_scope.last_update = date.today()

# Register the event listeners to automatically update the 'last_update' field.
# This ensures that any change in related models updates the parent BIA.
event.listen(ContextScope, 'before_update', update_context_scope_last_update)

models_to_track = [Component, Consequences, AvailabilityRequirements, AIIdentificatie, Summary]
for model in models_to_track:
    event.listen(model, 'after_insert', update_context_scope_last_update)
    event.listen(model, 'after_update', update_context_scope_last_update)
    event.listen(model, 'after_delete', update_context_scope_last_update)