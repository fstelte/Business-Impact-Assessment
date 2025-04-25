# forms.py

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, DateField, SelectField, TextAreaField, BooleanField
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import InputRequired, Length

from app.services import app_db
from app.model import Context_Scope, Components, Availability_Requirements, References, Consequences, ConsequenceChoices, SecurityProperties, Summary

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
    risk_assessment_human = SelectField('Would a risk assessment on the human factor be necassery ', choices=[('yes', 'Yes'), ('no', 'No')], validators=[InputRequired()])
    risk_assessment_process = SelectField('Would a risk assessment on the process factor be necassery ',choices=[('yes', 'Yes'), ('no', 'No')],  validators=[InputRequired()])
    risk_assessment_technological = SelectField('Would a risk assessment on the technilogical factor be necassery ',choices=[('yes', 'Yes'), ('no', 'No')],  validators=[InputRequired()])
    ai_model= SelectField('Does the system use AI or an algorithm? ',choices=[('yes', 'Yes'), ('no', 'No')],  validators=[InputRequired()])
    project_leader = StringField('Who is the project leader or Product Owner?', validators=[InputRequired()])
    risk_owner = StringField('Who is the risk owner ', validators=[InputRequired()])
    product_owner = StringField('Who is the product owner ', validators=[InputRequired()])
    technical_administrator = StringField('Who is the technical administrator ', validators=[InputRequired()])
    security_manager = StringField('Who is the security manager (advice around security) ', validators=[InputRequired()])
    incident_contact = StringField('Who is the point of contact for security incidents', validators=[InputRequired()])



class BIANewForm(FlaskForm, BIANewEditFormMixin):

    submit = SubmitField('Add', render_kw={'class': 'mt-2'})

class BIAEditForm(FlaskForm, BIANewEditFormMixin):

    submit = SubmitField('Update', render_kw={'class': 'mt-2'})

class BIADeleteForm(FlaskForm):

    submit = SubmitField('Confirm delete', render_kw={'class': 'mt-2'})

# Components
class CompNewEditFormMixin():
    name = SelectField('Linked to BIA',
        render_kw={'size': 1})
    component_name = StringField('Name for Component ', validators=[InputRequired()])
    processes_dependencies = StringField('What processes are dependent on the component', validators=[InputRequired()])
    info_type = StringField('What type of information does the component hold ', validators=[InputRequired()])
    info_owner = StringField('Who is the owner of the information that the component holds?', validators=[InputRequired()])
    user_type = StringField('What type of users use this component ', validators=[InputRequired()])
    description = StringField('Describe the component', validators=[InputRequired()])

class CompNewForm(FlaskForm, CompNewEditFormMixin):
    submit = SubmitField('Add', render_kw={'class': 'mt-2'})

class CompEditForm(FlaskForm, CompNewEditFormMixin):

    submit = SubmitField('Update', render_kw={'class': 'mt-2'})

class CompDeleteForm(FlaskForm):

    submit = SubmitField('Confirm delete', render_kw={'class': 'mt-2'})


# References
class ReferenceNewEditFormMixin():
    consequence_category = StringField('Category for reference ', validators=[InputRequired()])
    consequence_insignificant = StringField('What does the insignificant consequence entail? ', validators=[InputRequired()])
    consequence_small = StringField('What does the small consequence entail? ', validators=[InputRequired()])
    consequence_medium = StringField('What does the medium consequence entail? ', validators=[InputRequired()])
    consequence_large = StringField('What does the large consequence entail? ', validators=[InputRequired()])
    consequence_huge = StringField('What does the huge consequence entail? ', validators=[InputRequired()])

class ReferenceNewForm(FlaskForm, ReferenceNewEditFormMixin):
    submit = SubmitField('Add', render_kw={'class': 'mt-2'})

class ReferenceEditForm(FlaskForm, ReferenceNewEditFormMixin):

    submit = SubmitField('Update', render_kw={'class': 'mt-2'})

class ReferenceDeleteForm(FlaskForm):

    submit = SubmitField('Confirm delete', render_kw={'class': 'mt-2'})

# Consequences app_db.session.query(Consequences).filter(Consequences.id == consequence_id).first()
class ConsequenceNewEditFormMixin:
    component_name = SelectField('Linked to Component',
                           render_kw={'size': 1})
    security_property = SelectField('Where does the consequence interfere with',
                           render_kw={'size': 1})
    consequence_category = SelectField('Consequence Category',
                           render_kw={'size': 1})
    consequence_worstcase = SelectField('Worstcase consequence',
                           render_kw={'size': 1})
    justification_worstcase = TextAreaField('Justification for worstcase consequence', render_kw={"rows": 6, "cols": 6})

    consequence_realisticcase = SelectField('Realistic consequence',
                           render_kw={'size': 1})
    justification_realisticcase = TextAreaField('Justification for realistic consequence', render_kw={"rows": 6, "cols": 6})

class ConsequenceNewForm(FlaskForm, ConsequenceNewEditFormMixin):
    submit = SubmitField('Add', render_kw={'class': 'mt-2'})

class ConsequenceEditForm(FlaskForm, ConsequenceNewEditFormMixin):
    submit = SubmitField('Update', render_kw={'class': 'mt-2'})


class ConsequenceDeleteForm(FlaskForm):

    submit = SubmitField('Confirm delete')
# Availability
class AvailabilityNewEditFormMixin():
    component_name = SelectField('Linked to Component',
                           render_kw={'size': 1})
    mtd = StringField('What is the MTD? ', validators=[InputRequired()])
    rto = StringField('What is the RTO? ', validators=[InputRequired()])
    rpo = StringField('What is the RPO? ', validators=[InputRequired()])
    masl = StringField('What is the MASL ', validators=[InputRequired()])

class AvailabilityNewForm(FlaskForm, AvailabilityNewEditFormMixin):
    submit = SubmitField('Add', render_kw={'class': 'mt-2'})

class AvailabilityEditForm(FlaskForm, AvailabilityNewEditFormMixin):

    submit = SubmitField('Update', render_kw={'class': 'mt-5'})

class AvailabilityDeleteForm(FlaskForm):

    submit = SubmitField('Confirm delete', render_kw={'class': 'mt-2'})

class SummaryNewEditFormMixin():
        name = SelectField('Linked to BIA',
                           render_kw={'size': 1})
        summary_text = TextAreaField('Type your summary', render_kw={"rows": 30, "cols": 11})
        


class SummaryNewForm(FlaskForm, SummaryNewEditFormMixin):

    submit = SubmitField('Add', render_kw={'class': 'mt-2'})

class SummaryEditForm(FlaskForm, SummaryNewEditFormMixin):

    submit = SubmitField('Update', render_kw={'class': 'mt-2'})

class SummaryDeleteForm(FlaskForm):
    submit = SubmitField('Confirm delete')