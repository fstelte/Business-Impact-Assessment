# forms.py

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, DateField
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import InputRequired, Length

from app.services import app_db
from app.model import Context_Scope, Components, Availability_Requirements, References, Consequences, ConsequenceChoices, SecurityProperties

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
    info_owner = StringField('Who is the owner of the information that the component holds?', validators=[InputRequired()])
    user_type = StringField('What type of users use this component ', validators=[InputRequired()])
    description = StringField('Describe the component', validators=[InputRequired()])

class CompNewForm(FlaskForm, CompNewEditFormMixin):
    submit = SubmitField('Add')

class CompEditForm(FlaskForm, CompNewEditFormMixin):

    submit = SubmitField('Update')

class CompDeleteForm(FlaskForm):

    submit = SubmitField('Confirm delete')


# References
class ReferenceNewEditFormMixin():
    consequence_category = StringField('Category for reference ', validators=[InputRequired()])
    consequence_small = StringField('What does the small consequence entail? ', validators=[InputRequired()])
    consequence_medium = StringField('What does the medium consequence entail? ', validators=[InputRequired()])
    consequence_large = StringField('What does the large consequence entail? ', validators=[InputRequired()])
    consequence_huge = StringField('What does the huge consequence entail? ', validators=[InputRequired()])

class ReferenceNewForm(FlaskForm, ReferenceNewEditFormMixin):
    submit = SubmitField('Add')

class ReferenceEditForm(FlaskForm, ReferenceNewEditFormMixin):

    submit = SubmitField('Update')

class ReferenceDeleteForm(FlaskForm):

    submit = SubmitField('Confirm delete')

# Consequences
class ConsequenceNewEditFormMixin():
    component_name = QuerySelectField('Linked to Component',
                           get_label='component_name',
                           query_factory=lambda: app_db.session.query(Components).order_by(Components.id).all(),
                           allow_blank=False,
                           blank_text='Select the Component',
                           render_kw={'size': 1})
    category = QuerySelectField('Consequence Category',
                           get_label='consequence_category',
                           query_factory=lambda: app_db.session.query(References).order_by(References.consequence_category).all(),
                           allow_blank=False,
                           blank_text='Select the category',
                           render_kw={'size': 1})
    security_property = QuerySelectField('Where does the consequence interfere with',
                           get_label='choice',
                           query_factory=lambda: app_db.session.query(SecurityProperties).order_by(SecurityProperties.id).all(),
                           allow_blank=False,
                           blank_text='Select the property',
                           render_kw={'size': 1})
    consequence_worstcase = QuerySelectField('Worstcase consequence',
                           get_label='choice',
                           query_factory=lambda: app_db.session.query(ConsequenceChoices).order_by(ConsequenceChoices.id).all(),
                           allow_blank=False,
                           blank_text='Select the Consequence',
                           render_kw={'size': 1})
    justification_worstcase = StringField('Justification for worstcase consequence')

    consequence_realisticcase = QuerySelectField('Realistic consequence',
                           get_label='choice',
                           query_factory=lambda: app_db.session.query(ConsequenceChoices).order_by(ConsequenceChoices.id).all(),
                           allow_blank=False,
                           blank_text='Select the Consequence',
                           render_kw={'size': 1})
    justification_realisticcase = StringField('Justification for realistic consequence')

class ConsequenceNewForm(FlaskForm, ConsequenceNewEditFormMixin):
    submit = SubmitField('Add')

class ConsequenceEditForm(FlaskForm, ConsequenceNewEditFormMixin):
    submit = SubmitField('Update')


class ConsequenceDeleteForm(FlaskForm):

    submit = SubmitField('Confirm delete')
# Availability
class AvailabilityNewEditFormMixin():
    component_name = QuerySelectField('Linked to Component',
                           get_label='component_name',
                           query_factory=lambda: app_db.session.query(Components).order_by(Components.id).all(),
                           allow_blank=False,
                           blank_text='Select the Component',
                           render_kw={'size': 1})
    mtd = StringField('What is the MTD? ', validators=[InputRequired()])
    rto = StringField('What is the RTO? ', validators=[InputRequired()])
    rpo = StringField('What is the RPO? ', validators=[InputRequired()])
    masl = StringField('What is the MASL ', validators=[InputRequired()])

class AvailabilityNewForm(FlaskForm, AvailabilityNewEditFormMixin):
    submit = SubmitField('Add')

class AvailabilityEditForm(FlaskForm, AvailabilityNewEditFormMixin):

    submit = SubmitField('Update')

class AvailabilityDeleteForm(FlaskForm):

    submit = SubmitField('Confirm delete')