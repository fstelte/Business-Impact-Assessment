# forms.py

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, DateField
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import InputRequired, Length

from app.services import app_db
from app.model import Context_Scope, Components, Availability_Requirements, References

# BIA
class BIANewEditFormMixin():
    name = StringField('Name for BIA ', validators=[InputRequired()])
    responsible = StringField('Who is repsonsible for the BIA ', validators=[InputRequired()])
    coordinator = StringField('Who is coordinator for the BIA ', validators=[InputRequired()])
    start_date = DateField('What is the start date for the BIA ', validators=[InputRequired()])
    end_date = DateField('What is the end date for the BIA ', validators=[InputRequired()])
    last_update = DateField('When is the BIA last updated ', validators=[InputRequired()])
    service_description = StringField('Describe the service ', validators=[InputRequired()])
    knowledge = StringField('What is the knowledge in the organisation about the service', validators=[InputRequired()])
    interfaces = StringField('What interfaces are there for the service ', validators=[InputRequired()])
    mission_critical = StringField('Are there interfaces with mission critical systems ', validators=[InputRequired()])
    support_contracts = StringField('Are there support contracts for the service', validators=[InputRequired()])
    security_supplier = StringField('Who is the security supplier ', validators=[InputRequired()])
    user_amount = IntegerField('How many users are there ', validators=[InputRequired()])
    scope_description = StringField('Describe the scope of the BIA ', validators=[InputRequired()])
    risk_assessment_human = StringField('Would a risk assessment on the human factor be necassery ', validators=[InputRequired()])
    risk_assessment_process = StringField('Would a risk assessment on the process factor be necassery ', validators=[InputRequired()])
    risk_assessment_technological = StringField('Would a risk assessment on the technilogical factor be necassery ', validators=[InputRequired()])
    project_leader = StringField('Who is the project leader ', validators=[InputRequired()])
    risk_owner = StringField('Who is the risk owner ', validators=[InputRequired()])
    product_owner = StringField('Who is the product owner ', validators=[InputRequired()])
    technical_administrator = StringField('Who is the technical administrator ', validators=[InputRequired()])
    security_manager = StringField('Who is the security manager (advice around security) ', validators=[InputRequired()])
    incident_contact = StringField('Who is the point of contact for security incidents', validators=[InputRequired()])



class BIANewForm(FlaskForm, BIANewEditFormMixin):

    submit = SubmitField('Add')

class BIAEditForm(FlaskForm, BIANewEditFormMixin):

    submit = SubmitField('Update')

class BIADeleteForm(FlaskForm):

    submit = SubmitField('Confirm delete')

# Components
class CompNewEditFormMixin():
    name = QuerySelectField('Linked to BIA',
        get_label='name',
        allow_blank=False,
        blank_text='Select the BIA',
        render_kw={'size': 1})
    component_name = StringField('Name for Component ', validators=[InputRequired()])
    processes_dependencies = StringField('What processes are dependent on the component', validators=[InputRequired()])
    info_type = StringField('What type of information does the component hold ', validators=[InputRequired()])
    user_type = StringField('What type of users use this component ', validators=[InputRequired()])
    description = StringField('Describe the component', validators=[InputRequired()])

class CompNewForm(FlaskForm, CompNewEditFormMixin):
    submit = SubmitField('Add')

class CompEditForm(FlaskForm, CompNewEditFormMixin):

    submit = SubmitField('Update')

class CompDeleteForm(FlaskForm):

    submit = SubmitField('Confirm delete')
