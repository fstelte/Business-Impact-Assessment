# views.py
import os
import pandas as pd

from flask import Flask, Blueprint, current_app, g, session, request, url_for, redirect, \
    render_template, flash, abort

from app.services import app_db
from app.model import Context_Scope, Components, Availability_Requirements, References, Consequences,  ConsequenceChoices, SecurityProperties, Summary
from .forms import (
    BIANewForm, BIAEditForm, BIADeleteForm, CompNewForm, CompEditForm, CompDeleteForm,
    ReferenceNewForm, ReferenceEditForm, ReferenceDeleteForm,
    ConsequenceNewForm, ConsequenceEditForm, ConsequenceDeleteForm,
    AvailabilityNewForm, AvailabilityEditForm, AvailabilityDeleteForm,
    SummaryNewForm, SummaryEditForm, SummaryDeleteForm
)
from werkzeug.utils import secure_filename

def choices_maken(klas, tagg, items):
        lijst = []
        tobequeried = app_db.session.query(klas).order_by(klas.id).all()
        if getattr(items,tagg) is not None:
            lijst.append(items.component_name)
        for values in tobequeried:
            if getattr(values,tagg) not in lijst:
                lijst.append(values.component_name)

        return lijst

def get_choices(klas, tagg, items):
        lijst = []
        tobequeried = app_db.session.query(klas).order_by(klas.id).all()
        if getattr(items,tagg) is not None:
            lijst.append(items.security_property)
        for values in tobequeried:
            if getattr(values,tagg) not in lijst:
                lijst.append(values.security_property)

        return lijst


def get_references(klas, tagg, items):
        lijst = []
        tobequeried = app_db.session.query(klas).order_by(klas.id).all()
        if getattr(items,tagg) is not None:
            lijst.append(items.consequence_category)
        for values in tobequeried:
            if getattr(values,tagg) not in lijst:
                lijst.append(values.consequence_category)

        return lijst

def get_consequences_wc(klas, tagg, items):
        lijst = []
        tobequeried = app_db.session.query(klas).order_by(klas.id).all()
        if getattr(items,tagg) is not None:
            lijst.append(items.consequence_worstcase)
        for values in tobequeried:
            if getattr(values,tagg) not in lijst:
                lijst.append(values.consequence_worstcase)

        return lijst

def get_consequences_rc(klas, tagg, items):
        lijst = []
        tobequeried = app_db.session.query(klas).order_by(klas.id).all()
        if getattr(items,tagg) is not None:
            lijst.append(items.consequence_realisticcase)
        for values in tobequeried:
            if getattr(values,tagg) not in lijst:
                lijst.append(values.consequence_realisticcase)

        return lijst

def get_bia(klas, tagg, items):
        lijst = []
        tobequeried = app_db.session.query(klas).order_by(klas.id).all()
        if getattr(items,tagg) is not None:
            lijst.append(items.name)
        for values in tobequeried:
            if getattr(values,tagg) not in lijst:
                lijst.append(values.name)

        return lijst

manage_data_blueprint = Blueprint('manage_data', __name__)
app = Flask(__name__)
#BIA / Context_Scope
@manage_data_blueprint.route('/bia/list', methods=['GET', 'POST'])
def bia_list():
    bias = app_db.session.query(Context_Scope).order_by(Context_Scope.name).all()

    thead_th_items = [
        {
            'col_title': '#',
        },
        {
            'col_title': 'Name',
        },
        {
            'col_title': 'Start date'
        },
        {
            'col_title': 'Responsible'
        },
        {
            'col_title': 'Add component'
        },
        {
            'col_title': 'Export to CSV'
        },
        {
            'col_title' : 'Delete BIA'
        }
    ]

    tbody_tr_items = []
    for bia in bias:
 #       Customers_name = '-'
 #       if friend.Customers:
 #           Customers_name = friend.Customers.name
 #       Months_names = '-'
 #       if friend.hobbies:
 #           Months_names = ', '.join([x.name for x in friend.hobbies])

        tbody_tr_items.append([
            {
                'col_value': bia.id,
            },
            {
                'col_value': bia.name,
                'url': url_for('manage_data.bia_edit', bia_id=bia.id),
            },
            {
                'col_value': bia.start_date,
                
            },
            {
                'col_value': bia.responsible,
            },
            { 
                'col_value': 'Add',
                'url': url_for('manage_data.component_new', bia_id=bia.id),
            },
            {
                'col_value': 'Export',
                'url': url_for('manage_data.bia_export', bia_id=bia.id),
            },
            {
                'col_value': 'Delete',
                'url': url_for('manage_data.bia_delete', bia_id=bia.id),
            }
            ])

    return render_template(
        'items_list.html',
        title='BIAs',
        thead_th_items=thead_th_items,
        tbody_tr_items=tbody_tr_items,
        item_new_url=url_for('manage_data.bia_new'),
        item_new_text='New BIA',
    )

@manage_data_blueprint.route('/bia/new', methods=['GET', 'POST'])
def bia_new():

    item = Context_Scope()
    form = BIANewForm()

    if form.validate_on_submit():
        form.populate_obj(item)
        app_db.session.add(item)
       # send_csv(item)
        app_db.session.commit()
        flash('BIA added: ' + item.name, 'info')
        return redirect(url_for('manage_data.bia_list'))

    return render_template('item_new_edit.html', title='New BIA', form=form)

@manage_data_blueprint.route('/bia/edit/<int:bia_id>', methods=['GET', 'POST'])
def bia_edit(bia_id):

    item = app_db.session.query(Context_Scope).filter(Context_Scope.id == bia_id).first()
    if item is None:
        abort(403)

    form = BIAEditForm(obj=item)

    if form.validate_on_submit():
        form.populate_obj(item)
        app_db.session.commit()
 #       flash('Hours updated: ' + item.customer_id, 'info')
        return redirect(url_for('manage_data.bia_list'))

    return render_template('item_new_edit.html', title='Edit BIA', form=form)

@manage_data_blueprint.route('/bia/delete/<int:bia_id>', methods=['GET', 'POST'])
def bia_delete(bia_id):

    item = app_db.session.query(Context_Scope).filter(Context_Scope.id == bia_id).first()
    if item is None:
        abort(403)

    form = BIADeleteForm(obj=item)

    item_name = item.name
    if form.validate_on_submit():
        app_db.session.delete(item)
        app_db.session.commit()
 #       flash('Deleted hours: ' + item_name, 'info')
        return redirect(url_for('manage_data.bia_list'))

    return render_template('item_delete.html', title='Delete BIA', item_name=item_name, form=form)


@manage_data_blueprint.route('/bia/export/<int:bia_id>', methods=['GET', 'POST'])
def bia_export(bia_id):
    bias = app_db.session.query(Context_Scope).filter(Context_Scope.id == bia_id).all()
    CSV_Name = bias[0].name
    summary = app_db.session.query(Summary).filter(Summary.name == bias[0].name).all()
    components = app_db.session.query(Components).filter(Components.name == bias[0].name).all()
    consequences = app_db.session.query(Consequences).filter(Consequences.component_name.in_([c.component_name for c in components])).all()
    availability = app_db.session.query(Availability_Requirements).filter(Availability_Requirements.component_name.in_([c.component_name for c in components])).all()
    cons_choices = app_db.session.query(ConsequenceChoices).all()
    references = app_db.session.query(References).all()
    directory_name = secure_filename(CSV_Name)
    
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    bias_dicts = [{
        'BIA Name': b.name, 
        'BIA Responsible': b.responsible, 
        'BIA Coordinator': b.coordinator, 
        'BIA Start Date': b.start_date, 
        'BIA End Date': b.end_date, 
        'BIA Last Update': b.last_update,
        'Service Description': b.service_description,
        'Knowledge': b.knowledge,
        'Interfaces': b.interfaces,
        'mission_critical': b.mission_critical,
        'support_contracts': b.support_contracts,
        'security_supplier': b.security_supplier,
        'user_amount': b.user_amount,
        'scope_description': b.scope_description,
        'risk_assessment_human': b.risk_assessment_human,
        'risk_assessment_process': b.risk_assessment_process,
        'risk_assessment_technological': b.risk_assessment_technological,
        'project_leader': b.project_leader,
        'risk_owner': b.risk_owner,
        'product_owner': b.product_owner,
        'technical_administrator': b.technical_administrator,
        'security_manager': b.security_manager,
        'incident_contact': b.incident_contact
    } for b in bias]

    df_bias = pd.DataFrame(bias_dicts)

    comp_dicts = [{
        'Gerelateerd aan BIA': c.name,
        'Component name': c.component_name,
        'Process Dependencies': c.processes_dependencies,
        'Type of information': c.info_type,
        'Information Owner': c.info_owner,
        'Types of users': c.user_type,
        'Description of the component': c.description,
    } for c in components]
    df_components = pd.DataFrame(comp_dicts)
    
    cons_dicts = [{
        'Gerelateerd aan Component': d.component_name,
        'Category of consequence': d.consequence_category,
        'Property of Security': d.security_property,
        'Worstcase consequence': d.consequence_worstcase,
        'Justification for worst consequence': d.justification_worstcase,
        'Realistic consequence': d.consequence_realisticcase,
        'Justification for realistic consequence': d.justification_realisticcase,
    } for d in consequences]
    df_consequences = pd.DataFrame(cons_dicts)

    avail_dicts = [{
        'Gerelateerd aan Component': e.component_name,
        'Maximum Tolerable Downtime': e.mtd,
        'Recovery Time Objective': e.rto,
        'Recovery Point Objective': e.rpo,
        'Minimum Acceptable Service Level': e.masl,
    } for e in availability]
    df_availability = pd.DataFrame(avail_dicts)

    summary_dicts = [{
        'Gerelateerd aan BIA': f.name,
        'Summary Test': f.summary_text,
    } for f in summary]
    df_summary = pd.DataFrame(summary_dicts)

    cons_choices_dicts = [{
        'Ergste geval consequentie': g.consequence_worstcase,
        'Realistisch geval consequentie': g.consequence_realisticcase,
    } for g in cons_choices]
    df_cons_choices = pd.DataFrame(cons_choices_dicts) 
   
    references_dicts = [{
        'Consequentie categorie': h.consequence_category,
        'Consequentie onbeduidend': h.consequence_insignificant,
        'Consequentie klein': h.consequence_small,
        'Consequentie gemiddeld': h.consequence_medium,
        'Consequentie groot': h.consequence_large,
        'Consequentie enorm': h.consequence_huge,
    } for h in references]
    df_references = pd.DataFrame(references_dicts) 
   
    if not df_bias.empty:
        df_bias.to_csv(os.path.join(directory_name, f'{CSV_Name}_bia.csv'), index=False)
    if not df_components.empty:
        df_components.to_csv(os.path.join(directory_name, f'{CSV_Name}_components.csv'), index=False)
    if not df_consequences.empty:
        df_consequences.to_csv(os.path.join(directory_name, f'{CSV_Name}_consequences.csv'), index=False)
    if not df_availability.empty:
        df_availability.to_csv(os.path.join(directory_name, f'{CSV_Name}_availability.csv'), index=False)
    if not df_summary.empty:
        df_summary.to_csv(os.path.join(directory_name, f'{CSV_Name}_summary.csv'), index=False)
    if not df_cons_choices.empty:
        df_cons_choices.to_csv(os.path.join(directory_name, f'{CSV_Name}_choices.csv'), index=False)
    if not df_references.empty:
        df_references.to_csv(os.path.join(directory_name, f'{CSV_Name}_references.csv'), index=False)

    flash('Export geslaagd!')
    return redirect(url_for('manage_data.bia_list'))
   
# Components
@manage_data_blueprint.route('/component/list', methods=['GET', 'POST'])
def component_list():
    comps = app_db.session.query(Components).order_by(Components.id).all()
    bias = app_db.session.query(Context_Scope).order_by(Context_Scope.id).all()

    thead_th_items = [
        {
            'col_title': '#',
        },
        {
            'col_title': 'Name',
        },
        {
            'col_title': 'Linked to BIA'
        },
        {
            'col_title': 'Description'
        },
        {
            'col_title': 'Information type'
        },
        {
            'col_title': 'Delete'
        }
    ]

    tbody_tr_items = []
    for component in comps:

 #       Customers_name = '-'
 #       if friend.Customers:
 #           Customers_name = friend.Customers.name
 #       Months_names = '-'
 #       if friend.hobbies:
 #           Months_names = ', '.join([x.name for x in friend.hobbies])

        tbody_tr_items.append([
            {
                'col_value': component.id,
            },
            {
                'col_value': component.component_name,
                'url': url_for('manage_data.component_edit', component_id=component.id),
            },
            {
                'col_value': component.name
            },
            {
                'col_value': component.description
                
            },
            {
                'col_value': component.info_type
            },
            {
                'col_value': 'Delete',
                'url': url_for('manage_data.component_delete', component_id=component.id),
            }
            ])

    return render_template(
        'items_list.html',
        title='Components',
        thead_th_items=thead_th_items,
        tbody_tr_items=tbody_tr_items,
        item_new_url=url_for('manage_data.component_new'),
        item_new_text='New Component',
    )

@manage_data_blueprint.route('/component/new', methods=['GET', 'POST'])
def component_new():

    
    form = CompNewForm()
    form.name.query = app_db.session.query(Context_Scope).order_by(Context_Scope.id)

    item = Components()

    lijst = get_bia(Context_Scope, 'name', item)
    form.name.choices = lijst

    if form.validate_on_submit():
        
        form.populate_obj(item)
        item.bia_name = form.name.data
        #bia_name = form.name.data 
        #component_name = form.component_name.data
        #processes_dependencies = form.processes_dependencies.data
        #info_type = form.info_type.data
        #user_type = form.user_type.data
        #description = form.description.data
        #new_data = Components(bia_name=bia_name, component_name=component_name, processes_dependencies=processes_dependencies, info_type=info_type, user_type=user_type, description=description)
        app_db.session.add(item)
        #app_db.session.add(new_data)
        app_db.session.commit()
        flash('Component added: ' + item.component_name, 'info')
        return redirect(url_for('manage_data.component_list'))

    return render_template('item_new_edit.html', title='New Component', form=form)

@manage_data_blueprint.route('/component/edit/<int:component_id>', methods=['GET', 'POST'])
def component_edit(component_id):

   
    item = app_db.session.query(Components).filter(Components.id == component_id).first()
    form = CompEditForm(obj=item)
    form.name.query = app_db.session.query(Context_Scope).order_by(Context_Scope.id)

    lijst = get_bia(Context_Scope, 'name', item)
    form.name.choices = lijst

    if item is None:
        abort(403)

    if form.validate_on_submit():
        form.populate_obj(item)
        app_db.session.commit()
        flash('Component updated: ' + item.component_name, 'info')
        return redirect(url_for('manage_data.component_list'))

    return render_template('item_new_edit.html', title='Edit Component', form=form)

@manage_data_blueprint.route('/component/delete/<int:component_id>', methods=['GET', 'POST'])
def component_delete(component_id):

    item = app_db.session.query(Components).filter(Components.id == component_id).first()
    if item is None:
        abort(403)

    form = CompDeleteForm(obj=item)


    item_name = item.component_name
    if form.validate_on_submit():
        app_db.session.delete(item)
        app_db.session.commit()
        flash('Deleted hours: ' + item_name, 'info')
        return redirect(url_for('manage_data.component_list'))

    return render_template('item_delete.html', title='Delete Component', item_name=item_name, form=form)

#References
@manage_data_blueprint.route('/reference/list', methods=['GET', 'POST'])
def reference_list():
    references = app_db.session.query(References).order_by(References.id).all()

    thead_th_items = [
        {
            'col_title': '#',
        },
        {
            'col_title': 'Category',
        },
        {
            'col_title': 'Insignificant'
        },
        {
            'col_title': 'Low'
        },
        {
            'col_title': 'Medium'
        },
        {
            'col_title': 'Large'
        },
        {
            'col_title': 'Huge'
        },
        {
            'col_title': 'Delete'
        }
    ]

    tbody_tr_items = []
    for reference in references:
 #       Customers_name = '-'
 #       if friend.Customers:
 #           Customers_name = friend.Customers.name
 #       Months_names = '-'
 #       if friend.hobbies:
 #           Months_names = ', '.join([x.name for x in friend.hobbies])

        tbody_tr_items.append([
            {
                'col_value': reference.id,
            },
            {
                'col_value': reference.consequence_category,
                'url': url_for('manage_data.reference_edit', reference_id=reference.id),
            },
            {
                'col_value': reference.consequence_insignificant
                
            },
            {
                'col_value': reference.consequence_small
                
            },
            {
                'col_value': reference.consequence_medium
                
            },

            {
                'col_value': reference.consequence_large
                
            },
            {
                'col_value': reference.consequence_huge
            },
            {
                'col_value': 'Delete',
                'url': url_for('manage_data.reference_delete', reference_id=reference.id),
            }
            ])

    return render_template(
        'items_list.html',
        title='References',
        thead_th_items=thead_th_items,
        tbody_tr_items=tbody_tr_items,
        item_new_url=url_for('manage_data.reference_new'),
        item_new_text='New Reference',
    )

@manage_data_blueprint.route('/reference/new', methods=['GET', 'POST'])
def reference_new():

    item = References()
    form = ReferenceNewForm()

    if form.validate_on_submit():
        form.populate_obj(item)
        app_db.session.add(item)
        app_db.session.commit()
        flash('Reference added: ' + item.consequence_category, 'info')
        return redirect(url_for('manage_data.reference_list'))

    return render_template('item_new_edit.html', title='New Reference', form=form)

@manage_data_blueprint.route('/reference/edit/<int:reference_id>', methods=['GET', 'POST'])
def reference_edit(reference_id):

    item = app_db.session.query(References).filter(References.id == reference_id).first()
    if item is None:
        abort(403)

    form = ReferenceEditForm(obj=item)

    if form.validate_on_submit():
        form.populate_obj(item)
        app_db.session.commit()
        flash('Reference updated: ' + item.consequence_category, 'info')
        return redirect(url_for('manage_data.reference_list'))

    return render_template('item_new_edit.html', title='Edit Reference', form=form)

@manage_data_blueprint.route('/reference/delete/<int:reference_id>', methods=['GET', 'POST'])
def reference_delete(reference_id):

    item = app_db.session.query(References).filter(References.id == reference_id).first()
    if item is None:
        abort(403)

    form = ReferenceDeleteForm(obj=item)

    item_name = item.consequence_category
    if form.validate_on_submit():
        app_db.session.delete(item)
        app_db.session.commit()
        flash('Deleted reference: ' + item_name, 'info')
        return redirect(url_for('manage_data.reference_list'))

    return render_template('item_delete.html', title='Delete Reference', item_name=item_name, form=form)
# Consequences
@manage_data_blueprint.route('/consequence/list', methods=['GET', 'POST'])
def consequence_list():
    consequences = app_db.session.query(Consequences).order_by(Consequences.id).all()

    thead_th_items = [
        {
            'col_title': '#',
        },
        {
            'col_title': 'Linked to component',
        },
        {
            'col_title': 'Security Property',
        },
        {
            'col_title': 'Category',
        },
       
       {
            'col_title': 'Consequence realistic',
        },
        {
            'col_title': 'Delete'
        },

    ]

    tbody_tr_items = []
    for consequence in consequences:
 #       Customers_name = '-'
 #       if friend.Customers:
 #           Customers_name = friend.Customers.name
 #       Months_names = '-'
 #       if friend.hobbies:
 #           Months_names = ', '.join([x.name for x in friend.hobbies])

        tbody_tr_items.append([
            {
                'col_value': consequence.id,
            },
            {
                'col_value': consequence.component_name,
                'url': url_for('manage_data.consequence_edit', consequence_id=consequence.id),
            },
            {
                'col_value': consequence.security_property,
            },
            {
                'col_value': consequence.consequence_category,
            },

            {
                'col_value': consequence.consequence_realisticcase,
            },
            {
                'col_value': 'Delete',
                'url': url_for('manage_data.consequence_delete', consequence_id=consequence.id),
            }
            ])

    return render_template(
        'items_list.html',
        title='Consequences',
        thead_th_items=thead_th_items,
        tbody_tr_items=tbody_tr_items,
        item_new_url=url_for('manage_data.consequence_new'),
        item_new_text='New Consequence',
    )

@manage_data_blueprint.route('/consequence/new', methods=['GET', 'POST'])
def consequence_new():

    item = Consequences()
    form = ConsequenceNewForm()

    lijst = choices_maken(Components, 'component_name', item)
    form.component_name.choices = lijst

    sec_prop = get_choices(SecurityProperties, 'security_property', item)
    form.security_property.choices = sec_prop

    con_cat = get_references(References, 'consequence_category', item)
    form.consequence_category.choices = con_cat

    con_wc = get_consequences_wc(ConsequenceChoices, 'consequence_worstcase', item)
    form.consequence_worstcase.choices = con_wc

    con_rc = get_consequences_rc(ConsequenceChoices, 'consequence_realisticcase', item)
    form.consequence_realisticcase.choices = con_rc

    if form.validate_on_submit():
        form.populate_obj(item)
        # Map form fields to object attributes
        item.component_name = form.component_name.data #.component_name
        item.security_property = form.security_property.data
        item.consequence_category = form.consequence_category.data
        item.consequence_worstcase = form.consequence_worstcase.data
        item.justification_worstcase = form.justification_worstcase.data
        item.consequence_realisticcase = form.consequence_realisticcase.data
        item.justification_realisticcase = form.justification_realisticcase.data
        #item.component_name = form.name.data.name
        app_db.session.add(item)
        app_db.session.commit()
        flash('Consequence added: ' + item.consequence_category, 'info')
        return redirect(url_for('manage_data.consequence_list'))

    return render_template('item_new_edit.html', title='New Consequence', form=form)

@manage_data_blueprint.route('/consequence/edit/<int:consequence_id>', methods=['GET', 'POST'])
def consequence_edit(consequence_id):

    item = app_db.session.query(Consequences).filter(Consequences.id == consequence_id).first()
    if item is None:
        abort(403)

    form = ConsequenceEditForm(obj=item)

    lijst = choices_maken(Components, 'component_name', item)
    form.component_name.choices = lijst

    sec_prop = get_choices(SecurityProperties, 'security_property', item)
    form.security_property.choices = sec_prop

    con_cat = get_references(References, 'consequence_category', item)
    form.consequence_category.choices = con_cat

    con_wc = get_consequences_wc(ConsequenceChoices, 'consequence_worstcase', item)
    form.consequence_worstcase.choices = con_wc

    con_rc = get_consequences_rc(ConsequenceChoices, 'consequence_realisticcase', item)
    form.consequence_realisticcase.choices = con_rc

    if form.validate_on_submit():
        form.populate_obj(item)
        item.component_name = form.component_name.data
        item.security_property = form.security_property.data
        item.consequence_category = form.consequence_category.data
        item.consequence_worstcase = form.consequence_worstcase.data
        item.justification_worstcase = form.justification_worstcase.data
        item.consequence_realisticcase = form.consequence_realisticcase.data
        item.justification_realisticcase = form.justification_realisticcase.data
        app_db.session.commit()
        flash('Consequences updated: ' + item.component_name + item.consequence_category, 'info')
        return redirect(url_for('manage_data.consequence_list'))

    return render_template('item_new_edit.html', title='Edit Consequence', form=form)



@manage_data_blueprint.route('/consequence/delete/<int:consequence_id>', methods=['GET', 'POST'])
def consequence_delete(consequence_id):

    item = app_db.session.query(Consequences).filter(Consequences.id == consequence_id).first()
    if item is None:
        abort(403)

    form = ConsequenceDeleteForm(obj=item)

    item_name = item.component_name + " " + item.consequence_category
    if form.validate_on_submit():
        app_db.session.delete(item)
        app_db.session.commit()
        flash('Deleted consequence: ' + item_name, 'info')
        return redirect(url_for('manage_data.consequence_list'))

    return render_template('item_delete.html', title='Delete Consequence', item_name=item_name, form=form)
# Availability
@manage_data_blueprint.route('/availability/list', methods=['GET', 'POST'])
def availability_list():
    availabilities = app_db.session.query(Availability_Requirements).order_by(Availability_Requirements.id).all()

    thead_th_items = [
        {
            'col_title': '#',
        },
                {
            'col_title': 'Linked to component',
        },
        {
            'col_title': 'Maximum Tolerable Downtime (MTD)',
        },
        {
            'col_title': 'Recovery Time Objective (RTO)',
        },
        {
            'col_title': 'Recovery Point Objective (RPO)',
        },
        {
            'col_title': 'Minimal Acceptable Service Level (MASL)',
        },
        {
            'col_title': 'Delete'
        },

    ]
    tbody_tr_items = []
    for availability in availabilities:
 #       Customers_name = '-'
 #       if friend.Customers:
 #           Customers_name = friend.Customers.name
 #       Months_names = '-'
 #       if friend.hobbies:
 #           Months_names = ', '.join([x.name for x in friend.hobbies])

        tbody_tr_items.append([
            {
                'col_value': availability.id,
            },
            {
                'col_value': availability.component_name,
                'url': url_for('manage_data.availability_edit', availability_id=availability.id),
            },
            {
                'col_value': availability.mtd,
            },
            {
                'col_value': availability.rto,
            },
            {
                'col_value': availability.rpo,
            },
            {
                'col_value': availability.masl,
            },
            {
                'col_value': 'Delete',
                'url': url_for('manage_data.availability_delete', availability_id=availability.id),
            }
            ])

    return render_template(
        'items_list.html',
        title='Availability Requirements',
        thead_th_items=thead_th_items,
        tbody_tr_items=tbody_tr_items,
        item_new_url=url_for('manage_data.availability_new'),
        item_new_text='New availability requirement',
    )

@manage_data_blueprint.route('/availability/new', methods=['GET', 'POST'])
def availability_new():

    item = Availability_Requirements()
    form = AvailabilityNewForm()

    lijst = choices_maken(Components, 'component_name', item)
    form.component_name.choices = lijst

    if form.validate_on_submit():
        form.populate_obj(item)
        item.component_name = form.component_name.data #.component_name
        app_db.session.add(item)
        app_db.session.commit()
        flash('Availability requirement added: ' + item.component_name, 'info')
        return redirect(url_for('manage_data.availability_list'))

    return render_template('item_new_edit.html', title='New Consequence', form=form)

@manage_data_blueprint.route('/availability/edit/<int:availability_id>', methods=['GET', 'POST'])
def availability_edit(availability_id):

    item = app_db.session.query(Availability_Requirements).filter(Availability_Requirements.id == availability_id).first()
    if item is None:
        abort(403)

    form = AvailabilityEditForm(obj=item)

    lijst = choices_maken(Components, 'component_name', item)
    form.component_name.choices = lijst

    if form.validate_on_submit():
        form.populate_obj(item)
        app_db.session.commit()
        flash('Availability requirements updated: ' + item.component_name, 'info')
        return redirect(url_for('manage_data.availability_list'))

    return render_template('item_new_edit.html', title='Edit Availability requirement', form=form)

@manage_data_blueprint.route('/availability/delete/<int:availability_id>', methods=['GET', 'POST'])
def availability_delete(availability_id):

    item = app_db.session.query(Availability_Requirements).filter(Availability_Requirements.id == availability_id).first()
    if item is None:
        abort(403)

    form = AvailabilityDeleteForm(obj=item)

    item_name = item.component_name
    if form.validate_on_submit():
        app_db.session.delete(item)
        app_db.session.commit()
        flash('Deleted availability requirement: ' + item_name, 'info')
        return redirect(url_for('manage_data.availability_list'))

    return render_template('item_delete.html', title='Delete availability requirement', item_name=item_name, form=form)

@manage_data_blueprint.route('/summary/list', methods=['GET', 'POST'])
def summary_list():
    summarys = app_db.session.query(Summary).order_by(Summary.id).all()
    bias = app_db.session.query(Context_Scope).order_by(Context_Scope.id).all()

    thead_th_items = [
        {
            'col_title': '#',
        },
        {
            'col_title': 'Linked to BIA'
        },
        {
            'col_title': 'Summary'
        },
        {
            'col_title': 'Delete'
        }
    ]

    tbody_tr_items = []
    for summary in summarys:

 #       Customers_name = '-'
 #       if friend.Customers:
 #           Customers_name = friend.Customers.name
 #       Months_names = '-'
 #       if friend.hobbies:
 #           Months_names = ', '.join([x.name for x in friend.hobbies])

        tbody_tr_items.append([
            {
                'col_value': summary.id,
            },
            {
                'col_value': summary.name,
                'url': url_for('manage_data.summary_edit', summary_id=summary.id),
            },
            {
                'col_value': summary.summary_text
            },
            {
                'col_value': 'Delete',
                'url': url_for('manage_data.summary_delete', summary_id=summary.id),
            }
            ])

    return render_template(
        'items_list.html',
        title='Summary',
        thead_th_items=thead_th_items,
        tbody_tr_items=tbody_tr_items,
        item_new_url=url_for('manage_data.summary_new'),
        item_new_text='New Summary',
    )

@manage_data_blueprint.route('/summary/new', methods=['GET', 'POST'])
def summary_new():

    
    form = SummaryNewForm()
    form.name.query = app_db.session.query(Context_Scope).order_by(Context_Scope.id)

    item = Summary()

    lijst = get_bia(Context_Scope, 'name', item)
    form.name.choices = lijst

    if form.validate_on_submit():
        
        form.populate_obj(item)
        item.name = form.name.data
        app_db.session.add(item)
        #app_db.session.add(new_data)
        app_db.session.commit()
        flash('Summary added: ' + item.name, 'info')
        return redirect(url_for('manage_data.summary_list'))

    return render_template('item_new_edit.html', title='New summary', form=form)

@manage_data_blueprint.route('/summary/edit/<int:summary_id>', methods=['GET', 'POST'])
def summary_edit(summary_id):

   
    item = app_db.session.query(Summary).filter(Summary.id == summary_id).first()
    form = SummaryEditForm(obj=item)
    form.name.query = app_db.session.query(Context_Scope).order_by(Context_Scope.id)

    lijst = get_bia(Context_Scope, 'name', item)
    form.name.choices = lijst

    if item is None:
        abort(403)

    if form.validate_on_submit():
        form.populate_obj(item)
        app_db.session.commit()
        flash('Component updated: ' + item.name, 'info')
        return redirect(url_for('manage_data.summary_list'))

    return render_template('item_new_edit.html', title='Edit Summary', form=form)

@manage_data_blueprint.route('/summary/delete/<int:summary_id>', methods=['GET', 'POST'])
def summary_delete(summary_id):

    item = app_db.session.query(Summary).filter(Summary.id == summary_id).first()
    if item is None:
        abort(403)

    form = SummaryDeleteForm(obj=item)


    item_name = item.name
    if form.validate_on_submit():
        app_db.session.delete(item)
        app_db.session.commit()
        flash('Deleted summary for BIA: ' + item_name, 'info')
        return redirect(url_for('manage_data.summary_list'))

    return render_template('item_delete.html', title='Delete Summary', item_name=item_name, form=form)

