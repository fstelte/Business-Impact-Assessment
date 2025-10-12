# app/forms.py
# Definieert de formulieren met Flask-WTF.

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SelectMultipleField,SelectField, StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, DateField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Optional

from .models import User

class LoginForm(FlaskForm):
    """Inlogformulier."""
    email = StringField('Email address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')

class MFAForm(FlaskForm):
    """Formulier voor MFA token verificatie."""
    token = StringField('MFA Token', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verify')

class RegistrationForm(FlaskForm):
    """Registratieformulier."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(
        'Repeat password', validators=[DataRequired(), EqualTo('password', message='Password must match.')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('This username is alread in use.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email address is already in use.')

class ContextScopeForm(FlaskForm):
    """Formulier voor het aanmaken en bewerken van een Context/Scope item."""
    name = StringField('Service / business process / product name', validators=[DataRequired(), Length(max=50)])
    responsible = StringField('End reponsible', validators=[Optional(), Length(max=100)])
    coordinator = StringField('Coördinator', validators=[Optional(), Length(max=100)])
    start_date = DateField('Start date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('End date', format='%Y-%m-%d', validators=[Optional()])
    service_description = TextAreaField('Service description', validators=[Optional()])
    knowledge = TextAreaField('Knowledge within the organisation', validators=[Optional()])
    interfaces = TextAreaField('Interfaces with systems', validators=[Optional()])
    mission_critical = TextAreaField('Interfaces with mission critical systems', validators=[Optional(), Length(max=255)])
    support_contracts = StringField('How is support contracted', validators=[Optional(), Length(max=255)])
    security_supplier = StringField('Who is the security supplier?', validators=[Optional(), Length(max=255)])
    user_amount = IntegerField('Amount of users', validators=[Optional()])
    scope_description = TextAreaField('Scope description', validators=[Optional()])
    
     # --- DEFINITIEVE OPLOSSING ---
    # We standaardiseren op integers (1=Ja, 0=Nee) die overeenkomen met de database.
    risk_assessment_human = RadioField(
        'Does a risk assessment on people aspects need to be conducted?',
        choices=[(1, 'Yes'), (0, 'No')],      # <-- GEWIJZIGD naar integers
        coerce=int,                           # <-- GEWIJZIGD naar int
        validators=[Optional()]
    )
    risk_assessment_process = RadioField(
        'Does a risk assessment on process aspects need to be conducted?',
        choices=[(1, 'Yes'), (0, 'No')],      # <-- GEWIJZIGD naar integers
        coerce=int,                           # <-- GEWIJZIGD naar int
        validators=[Optional()]
    )
    risk_assessment_technological = RadioField(
        'Does a risk assessment on technical aspects need to be conducted?',
        choices=[(1, 'Yes'), (0, 'No')],      # <-- GEWIJZIGD naar integers
        coerce=int,                           # <-- GEWIJZIGD naar int
        validators=[Optional()]
    )
    ai_model = RadioField(
        'Is an AI model used?',
        choices=[(1, 'Yes'), (0, 'No')],      # <-- GEWIJZIGD naar integers
        coerce=int,                           # <-- GEWIJZIGD naar int
        validators=[Optional()]
    )
    
    project_leader = StringField('Project responsible', validators=[Optional(), Length(max=100)])
    risk_owner = StringField('Risk owner', validators=[Optional(), Length(max=100)])
    product_owner = StringField('Product owner', validators=[Optional(), Length(max=100)])
    technical_administrator = StringField('Technical administrator', validators=[Optional(), Length(max=100)])
    security_manager = StringField('Security Manager', validators=[Optional(), Length(max=100)])
    incident_contact = StringField('Incident Contact', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Save')

# De losse __init__ functie kan volledig worden verwijderd.
# NIEUW: Voeg deze class toe voor het componentenformulier
class ComponentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    info_type = StringField('Information Type')
    info_owner = StringField('Information Owner')
    user_type = StringField('User Type')
    process_dependencies = TextAreaField('Process Dependencies')
    description = TextAreaField('Description')
    submit = SubmitField('Save Component')

class EditUserForm(FlaskForm):
    """Formulier om gebruikersgegevens te bewerken (admin only)."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email address', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('user', 'USer'), ('admin', 'Administrator')], validators=[DataRequired()])
    submit = SubmitField('Save')

class ConsequenceForm(FlaskForm):
    consequence_category = SelectMultipleField('Consequence Category', choices=[
        ('financial', 'Financial'),
        ('operational', 'Operational'),
        ('reputation and trust', 'Reputation and Trust'),
        ('regulatory', 'Regulatory'),
        ('human and safety', 'Human and Safety'),
        ('privacy', 'Privacy')
    ], 
    coerce=str,
    validators=[DataRequired()])
    
    security_property = SelectField('Security Property', choices=[
        ('confidentiality', 'Confidentiality'),
        ('integrity', 'Integrity'),
        ('availability', 'Availability')
    ], validators=[DataRequired()])
    
    consequence_worstcase = SelectField('Worst Case Consequence', choices=[
        ('catastrophic', 'Catastrophic'),
        ('major', 'Major'),
        ('moderate', 'Moderate'),
        ('minor', 'Minor'),
        ('insignificant', 'Insignificant')
    ], validators=[DataRequired()])
    
    justification_worstcase = TextAreaField('Worst Case Justification')
    
    consequence_realisticcase = SelectField('Realistic Case Consequence', choices=[
        ('catastrophic', 'Catastrophic'),
        ('major', 'Major'),
        ('moderate', 'Moderate'),
        ('minor', 'Minor'),
        ('insignificant', 'Insignificant')
    ], validators=[DataRequired()])
    
    justification_realisticcase = TextAreaField('Realistic Case Justification')
    
    submit = SubmitField('Add Consequence')


class SummaryForm(FlaskForm):
    content = TextAreaField('Summary', validators=[DataRequired()])
    submit = SubmitField('Save Summary')

class ImportCSVForm(FlaskForm):
    bia = FileField('BIA CSV', validators=[FileAllowed(['csv'])])
    components = FileField('Components CSV', validators=[FileAllowed(['csv'])])
    consequences = FileField('Consequences CSV', validators=[FileAllowed(['csv'])])
    availability_requirements = FileField('Availability Requirements CSV', validators=[FileAllowed(['csv'])])
    ai_identification = FileField('AI Identification CSV', validators=[FileAllowed(['csv'])])
    summary = FileField('Summary CSV', validators=[FileAllowed(['csv'])])
    submit = SubmitField('Import')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')

class ImportSQLForm(FlaskForm):
    """Formulier voor het importeren van een BIA via een SQL-bestand."""
    sql_file = FileField('SQL File', validators=[
        FileRequired(),
        FileAllowed(['sql'], 'SQL files only!')
    ])
    submit = SubmitField('Import from SQL')