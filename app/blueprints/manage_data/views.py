# views.py
import os
import tempfile
import zipfile
import shutil
import pandas as pd
import io


from flask import Flask, Blueprint, current_app, g, session, request, url_for, redirect, \
    render_template, flash, abort, send_file, abort, after_this_request, make_response
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from flask_paginate import Pagination, get_page_parameter
from sqlalchemy.orm import joinedload


from app.services import app_db
from app.model import Context_Scope, Components, Availability_Requirements, References, Consequences,  ConsequenceChoices, SecurityProperties, Summary, AIIdentificatie
from .forms import (
    BIANewForm, BIAEditForm, BIADeleteForm, CompNewForm, CompEditForm, CompDeleteForm,
    ReferenceNewForm, ReferenceEditForm, ReferenceDeleteForm,
    ConsequenceNewForm, ConsequenceEditForm, ConsequenceDeleteForm,
    AvailabilityNewForm, AvailabilityEditForm, AvailabilityDeleteForm,
    SummaryNewForm, SummaryEditForm, SummaryDeleteForm,
    ConsequenceChoicesNewForm, ConsequenceChoicesEditForm, ConsequenceChoicesDeleteForm,
    SecurityPropertyNewForm, SecurityPropertyEditForm, SecurityPropertyDeleteForm,
    RegistrationForm,
    AIIdentificatieNewForm, AIIdentificatieEditForm, AIIdentificatieDeleteForm
)
from werkzeug.utils import secure_filename

def calculate_cia_score(consequence):
    score_map = {'Low': 1, 'Medium': 2, 'High': 3, 'Huge': 4}
    return score_map.get(consequence, 0)
# Functie om datumstrings om te zetten naar Python date objecten
import datetime
def parse_date(date_str):
    if pd.isna(date_str) or date_str == '' or date_str == 'None' or date_str is None:
        return None
    try:
        # Probeer verschillende datumformaten
        formats = ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
        for fmt in formats:
            try:
                return datetime.datetime.strptime(str(date_str), fmt).date()
            except ValueError:
                continue
        # Als geen van de formats werkt, return None
        return None
    except Exception:
        return None

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
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Number of items per page

    query = app_db.session.query(Context_Scope).order_by(Context_Scope.name)
    total = query.count()
    bias = query.offset((page - 1) * per_page).limit(per_page).all()

    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': (total + per_page - 1) // per_page
    }
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
        },
        {
            'col_title': 'Generate Report'
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
            },
            {
                'col_value': 'Generate Report',
                'url': url_for('manage_data.bia_report', bia_id=bia.id),
            }

            ])

    return render_template(
        'items_list.html',
        title='BIAs',
        thead_th_items=thead_th_items,
        tbody_tr_items=tbody_tr_items,
        item_new_url=url_for('manage_data.bia_new'),
        item_new_text='New BIA',
        item_import_url=url_for('manage_data.bia_import'),
        show_import=True,
        item_import_text='Import BIA',
        pagination=pagination
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
        # Verwijder alle gerelateerde gegevens
        components = app_db.session.query(Components).filter(Components.name == item.name).all()
        for component in components:
            # Verwijder consequences
            app_db.session.query(Consequences).filter(Consequences.component_name == component.component_name).delete()
            # Verwijder availability requirements
            app_db.session.query(Availability_Requirements).filter(Availability_Requirements.component_name == component.component_name).delete()
            # Verwijder AI identification
            app_db.session.query(AIIdentificatie).filter(AIIdentificatie.component_name == component.component_name).delete()

        # Verwijder components
        app_db.session.query(Components).filter(Components.name == item.name).delete()
        
        # Verwijder summary
        app_db.session.query(Summary).filter(Summary.name == item.name).delete()

        # Verwijder de BIA zelf
        app_db.session.delete(item)
        
        app_db.session.commit()
        flash('Deleted BIA and all related data: ' + item_name, 'info')
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
    ai_identifications = app_db.session.query(AIIdentificatie).filter(AIIdentificatie.component_name.in_([c.component_name for c in components])).all()
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
   
       # Voeg AI identificatie export toe
    ai_dicts = [{
        'Gerelateerd aan Component': ai.component_name,
        'AI Category': ai.category,
        'AI Justification': ai.motivatie,
    } for ai in ai_identifications]
    df_ai = pd.DataFrame(ai_dicts)

   
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
    if not df_ai.empty:
        df_ai.to_csv(os.path.join(directory_name, f'{CSV_Name}_ai_identification.csv'), index=False)

    flash('Export geslaagd!')
    return redirect(url_for('manage_data.bia_list'))

import logging

@manage_data_blueprint.route('/bia/report/<int:bia_id>', methods=['GET'])
def bia_report(bia_id):
    bia = app_db.session.query(Context_Scope).filter(Context_Scope.id == bia_id).first()
    components = app_db.session.query(Components).filter(Components.name == bia.name).all()
    components = app_db.session.query(Components).filter(Components.name == bia.name).options(joinedload(Components.ai_identificaties)).all()
    
    consequences = app_db.session.query(Consequences).filter(
        Consequences.component_name.in_([c.component_name for c in components])
    ).all()
    
    availability = app_db.session.query(Availability_Requirements).filter(
        Availability_Requirements.component_name.in_([c.component_name for c in components])
    ).all()
    
    summary = app_db.session.query(Summary).filter(Summary.name == bia.name).first()

    consequences_by_component = {}
    cia_scores = {}
    for component in components:
        consequences_by_component[component.component_name] = []
        cia_scores[component.component_name] = {'C': [], 'I': [], 'A': []}
        # Set default AI category to "No AI" if no AI identification exists
        if not component.ai_identificaties:
            component.ai_category = "No AI"
        else:
            component.ai_category = component.ai_identificaties[0].category

    for consequence in consequences:
        consequences_by_component[consequence.component_name].append(consequence)
        cia_map = {'Confidentiality': 'C', 'Integrity': 'I', 'Availability': 'A'}
        cia_key = cia_map.get(consequence.security_property, '')
        if cia_key:
            score = calculate_cia_score(consequence.consequence_realisticcase)
            cia_scores[consequence.component_name][cia_key].append({
                'score': score,
                'consequence': consequence.consequence_realisticcase,
                'category': consequence.consequence_category
            })

    # Debug logging
    print(f"Number of components: {len(components)}")
    print(f"Number of consequences: {len(consequences)}")
    for component_name, cons_list in consequences_by_component.items():
        print(f"Component {component_name} has {len(cons_list)} consequences")
        print(f"CIA scores for {component_name}: {cia_scores[component_name]}")

    # Debug logging
    for component_name, scores in cia_scores.items():
        print(f"CIA scores for {component_name}:")
        for cia, score_list in scores.items():
            for score in score_list:
                print(f"  {cia}: {score['consequence']} -> {score['score']}")

    html_content = render_template('bia_report.html',
                           bia=bia,
                           components=components,
                           consequences=consequences_by_component,
                           availability=availability,
                           summary=summary,
                           cia_scores=cia_scores)

    # Create a BytesIO object
    buffer = io.BytesIO()
    buffer.write(html_content.encode('utf-8'))
    buffer.seek(0)

    # Send the file
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"BIA_Report_{bia.name}.html",
        mimetype='text/html'
    )


def calculate_cia_score(consequence):
    score_map = {
        'Insignificant': 0,
        'Low': 1,
        'Small': 1,
        'Medium': 2,
        'High': 3,
        'Large': 3,
        'Huge': 4
    }
    return score_map.get(consequence, 0)
# Components
@manage_data_blueprint.route('/component/list', methods=['GET', 'POST'])
def component_list():
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Aantal items per pagina

    query = app_db.session.query(Components).order_by(Components.id)
    total = query.count()
    
    offset = (page - 1) * per_page
    comps = query.offset(offset).limit(per_page).all()
    
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': (total + per_page - 1) // per_page
    }

    thead_th_items = [
        {'col_title': '#'},
        {'col_title': 'Name'},
        {'col_title': 'Linked to BIA'},
        {'col_title': 'Description'},
        {'col_title': 'Information type'},
        {'col_title': 'Delete'}
    ]

    tbody_tr_items = []
    for component in comps:
        tbody_tr_items.append([
            {'col_value': component.id},
            {'col_value': component.component_name, 'url': url_for('manage_data.component_edit', component_id=component.id)},
            {'col_value': component.name},
            {'col_value': component.description},
            {'col_value': component.info_type},
            {'col_value': 'Delete', 'url': url_for('manage_data.component_delete', component_id=component.id)}
        ])

    return render_template(
        'items_list.html',
        title='Components',
        thead_th_items=thead_th_items,
        tbody_tr_items=tbody_tr_items,
        item_new_url=url_for('manage_data.component_new'),
        item_new_text='New Component',
        pagination=pagination
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
        item.name = form.name.data
        app_db.session.add(item)
        app_db.session.commit()
        flash('Component added: ' + item.component_name, 'info')
        
        if form.submit_and_new.data:
            # Als op "Add and New" is geklikt, redirect naar nieuwe component met dezelfde BIA
            return redirect(url_for('manage_data.component_new', bia_name=item.name))
        else:
            return redirect(url_for('manage_data.component_list'))

    # Als er een bia_name in de URL parameters staat, selecteer deze
    if request.args.get('bia_name'):
        form.name.data = request.args.get('bia_name')

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
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Aantal items per pagina

    query = app_db.session.query(Consequences).order_by(Consequences.id)
    total = query.count()
    
    offset = (page - 1) * per_page
    consequences = query.offset(offset).limit(per_page).all()
    
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': (total + per_page - 1) // per_page
    }

    thead_th_items = [
        {'col_title': '#'},
        {'col_title': 'Linked to component'},
        {'col_title': 'Security Property'},
        {'col_title': 'Category'},
        {'col_title': 'Consequence realistic'},
        {'col_title': 'Delete'}
    ]

    tbody_tr_items = []
    for consequence in consequences:
        tbody_tr_items.append([
            {'col_value': consequence.id},
            {'col_value': consequence.component_name, 'url': url_for('manage_data.consequence_edit', consequence_id=consequence.id)},
            {'col_value': consequence.security_property},
            {'col_value': consequence.consequence_category},
            {'col_value': consequence.consequence_realisticcase},
            {'col_value': 'Delete', 'url': url_for('manage_data.consequence_delete', consequence_id=consequence.id)}
        ])

    return render_template(
        'items_list.html',
        title='Consequences',
        thead_th_items=thead_th_items,
        tbody_tr_items=tbody_tr_items,
        item_new_url=url_for('manage_data.consequence_new'),
        item_new_text='New Consequence',
        pagination=pagination
    )

@manage_data_blueprint.route('/consequence/new', methods=['GET', 'POST'])
def consequence_new():
    form = ConsequenceNewForm()

    # Haal alle componenten op en maak een lijst van tuples (id, component_name)
    components = app_db.session.query(Components).all()
    form.component_name.choices = [(c.component_name, c.component_name) for c in components]

    # Haal alle security properties op
    security_properties = app_db.session.query(SecurityProperties).all()
    form.security_property.choices = [(sp.security_property, sp.security_property) for sp in security_properties]

    # Haal alle referenties (categorieën) op
    references = app_db.session.query(References).all()
    form.consequence_category.choices = [(r.consequence_category, r.consequence_category) for r in references]

    # Haal alle consequence choices op
    consequence_choices = app_db.session.query(ConsequenceChoices).all()
    form.consequence_worstcase.choices = [(cc.consequence_worstcase, cc.consequence_worstcase) for cc in consequence_choices]
    form.consequence_realisticcase.choices = [(cc.consequence_realisticcase, cc.consequence_realisticcase) for cc in consequence_choices]

    if form.validate_on_submit():
        categories = form.consequence_category.data
        for category in categories:
            new_consequence = Consequences(
                component_name=form.component_name.data,
                security_property=form.security_property.data,
                consequence_category=category,  # Gebruik één categorie per consequence
                consequence_worstcase=form.consequence_worstcase.data,
                justification_worstcase=form.justification_worstcase.data,
                consequence_realisticcase=form.consequence_realisticcase.data,
                justification_realisticcase=form.justification_realisticcase.data
            )
            app_db.session.add(new_consequence)
        
        app_db.session.commit()
        flash(f'{len(categories)} consequence(s) added successfully', 'success')
        
        if form.submit_and_new.data:
            return redirect(url_for('manage_data.consequence_new', component_name=form.component_name.data))
        else:
            return redirect(url_for('manage_data.consequence_list'))
    # Pre-select component_name if provided in URL parameters
    if request.args.get('component_name'):
        form.component_name.data = request.args.get('component_name')

    return render_template('item_new_edit.html', title='New Consequence', form=form)
@manage_data_blueprint.route('/consequence/edit/<int:consequence_id>', methods=['GET', 'POST'])
def consequence_edit(consequence_id):
    consequence = app_db.session.query(Consequences).filter(Consequences.id == consequence_id).first()
    if consequence is None:
        abort(404)

    form = ConsequenceEditForm(obj=consequence)

    # Populate form choices
    form.component_name.choices = choices_maken(Components, 'component_name', consequence)
    form.security_property.choices = get_choices(SecurityProperties, 'security_property', consequence)
    # If it's a GET request, populate the form with existing data
    if request.method == 'GET':
        form.consequence_category.data = consequence.consequence_category
    form.consequence_category.choices = get_references(References, 'consequence_category', consequence)
    form.consequence_worstcase.choices = get_consequences_wc(ConsequenceChoices, 'consequence_worstcase', consequence)
    form.consequence_realisticcase.choices = get_consequences_rc(ConsequenceChoices, 'consequence_realisticcase', consequence)

    if form.validate_on_submit():
        consequence.component_name = form.component_name.data
        consequence.security_property = form.security_property.data
        consequence.consequence_category = form.consequence_category.data
        consequence.consequence_worstcase = form.consequence_worstcase.data
        consequence.justification_worstcase = form.justification_worstcase.data
        consequence.consequence_realisticcase = form.consequence_realisticcase.data
        consequence.justification_realisticcase = form.justification_realisticcase.data

        app_db.session.commit()
        flash('Consequence updated successfully', 'success')
        return redirect(url_for('manage_data.consequence_list'))

    # If it's a GET request, populate the form with existing data
   # if request.method == 'GET':
    #    form.consequence_category.data = consequence.consequence_category

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
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Aantal items per pagina

    query = app_db.session.query(Availability_Requirements).order_by(Availability_Requirements.id)
    total = query.count()
    
    offset = (page - 1) * per_page
    availabilities = query.offset(offset).limit(per_page).all()
    
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': (total + per_page - 1) // per_page
    }

    thead_th_items = [
        {'col_title': '#'},
        {'col_title': 'Linked to component'},
        {'col_title': 'Maximum Tolerable Downtime (MTD)'},
        {'col_title': 'Recovery Time Objective (RTO)'},
        {'col_title': 'Recovery Point Objective (RPO)'},
        {'col_title': 'Minimal Acceptable Service Level (MASL)'},
        {'col_title': 'Delete'}
    ]

    tbody_tr_items = []
    for availability in availabilities:
        tbody_tr_items.append([
            {'col_value': availability.id},
            {'col_value': availability.component_name, 'url': url_for('manage_data.availability_edit', availability_id=availability.id)},
            {'col_value': availability.mtd},
            {'col_value': availability.rto},
            {'col_value': availability.rpo},
            {'col_value': availability.masl},
            {'col_value': 'Delete', 'url': url_for('manage_data.availability_delete', availability_id=availability.id)}
        ])

    return render_template(
        'items_list.html',
        title='Availability Requirements',
        thead_th_items=thead_th_items,
        tbody_tr_items=tbody_tr_items,
        item_new_url=url_for('manage_data.availability_new'),
        item_new_text='New availability requirement',
        pagination=pagination
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
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Aantal items per pagina

    query = app_db.session.query(Summary).order_by(Summary.id)
    total = query.count()
    
    offset = (page - 1) * per_page
    summarys = query.offset(offset).limit(per_page).all()
    
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': (total + per_page - 1) // per_page
    }

    thead_th_items = [
        {'col_title': '#'},
        {'col_title': 'Linked to BIA'},
        {'col_title': 'Summary'},
        {'col_title': 'Delete'}
    ]

    tbody_tr_items = []
    for summary in summarys:
        tbody_tr_items.append([
            {'col_value': summary.id},
            {'col_value': summary.name, 'url': url_for('manage_data.summary_edit', summary_id=summary.id)},
            {'col_value': summary.summary_text},
            {'col_value': 'Delete', 'url': url_for('manage_data.summary_delete', summary_id=summary.id)}
        ])

    return render_template(
        'items_list.html',
        title='Summary',
        thead_th_items=thead_th_items,
        tbody_tr_items=tbody_tr_items,
        item_new_url=url_for('manage_data.summary_new'),
        item_new_text='New Summary',
        pagination=pagination
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

@manage_data_blueprint.route('/bia/import', methods=['GET', 'POST'])
def bia_import():
    if request.method == 'POST':
        # Bepaal welke importmethode gebruikt wordt (ZIP of losse bestanden)
        import_type = request.form.get('import_type', 'files')
        temp_dir = tempfile.mkdtemp()
        csv_files = {}
        
        try:
            # Methode 1: Via ZIP bestand
            if import_type == 'zip':
                if 'zip_file' not in request.files:
                    flash('Geen ZIP bestand geselecteerd')
                    return redirect(request.url)
                
                zip_file = request.files['zip_file']
                if zip_file.filename == '':
                    flash('Geen ZIP bestand geselecteerd')
                    return redirect(request.url)
                
                # Sla het ZIP bestand op en pak het uit
                zip_path = os.path.join(temp_dir, secure_filename(zip_file.filename))
                zip_file.save(zip_path)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Zoek alle CSV bestanden in het uitgepakte ZIP bestand
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith(".csv"):
                            file_path = os.path.join(root, file)
                            if "_bia.csv" in file:
                                csv_files['bia'] = file_path
                            elif "_components.csv" in file:
                                csv_files['components'] = file_path
                            elif "_consequences.csv" in file:
                                csv_files['consequences'] = file_path
                            elif "_availability.csv" in file:
                                csv_files['availability'] = file_path
                            elif "_summary.csv" in file:
                                csv_files['summary'] = file_path
                            elif "_choices.csv" in file:
                                csv_files['choices'] = file_path
                            elif "_references.csv" in file:
                                csv_files['references'] = file_path
            
            # Methode 2: Via losse bestanden
            else:
                # BIA bestand is verplicht
                if 'bia_file' not in request.files:
                    flash('Geen BIA bestand geselecteerd')
                    return redirect(request.url)
                
                bia_file = request.files['bia_file']
                if bia_file.filename == '':
                    flash('Geen BIA bestand geselecteerd')
                    return redirect(request.url)
                
                # Sla BIA bestand op
                bia_path = os.path.join(temp_dir, secure_filename(bia_file.filename))
                bia_file.save(bia_path)
                csv_files['bia'] = bia_path
                
                # Sla Components bestand op
                components_file = request.files.get('components_file')
                if components_file and components_file.filename != '':
                    components_path = os.path.join(temp_dir, secure_filename(components_file.filename))
                    components_file.save(components_path)
                    csv_files['components'] = components_path
                
                # Sla Consequences bestand op
                consequences_file = request.files.get('consequences_file')
                if consequences_file and consequences_file.filename != '':
                    consequences_path = os.path.join(temp_dir, secure_filename(consequences_file.filename))
                    consequences_file.save(consequences_path)
                    csv_files['consequences'] = consequences_path
                
                # Sla Availability bestand op
                availability_file = request.files.get('availability_file')
                if availability_file and availability_file.filename != '':
                    availability_path = os.path.join(temp_dir, secure_filename(availability_file.filename))
                    availability_file.save(availability_path)
                    csv_files['availability'] = availability_path
                
                # Sla Summary bestand op
                summary_file = request.files.get('summary_file')
                if summary_file and summary_file.filename != '':
                    summary_path = os.path.join(temp_dir, secure_filename(summary_file.filename))
                    summary_file.save(summary_path)
                    csv_files['summary'] = summary_path
                
                # Sla Choices bestand op (indien van toepassing)
                choices_file = request.files.get('choices_file')
                if choices_file and choices_file.filename != '':
                    choices_path = os.path.join(temp_dir, secure_filename(choices_file.filename))
                    choices_file.save(choices_path)
                    csv_files['choices'] = choices_path
                
                # Sla References bestand op (indien van toepassing)
                references_file = request.files.get('references_file')
                if references_file and references_file.filename != '':
                    references_path = os.path.join(temp_dir, secure_filename(references_file.filename))
                    references_file.save(references_path)
                    csv_files['references'] = references_path
               # Sla AI Identification bestand op (indien van toepassing)
                ai_identification_file = request.files.get('ai_identification_file')
                if ai_identification_file and ai_identification_file.filename != '':
                    ai_identification_path = os.path.join(temp_dir, secure_filename(ai_identification_file.filename))
                    ai_identification_file.save(ai_identification_path)
                    csv_files['ai_identification'] = ai_identification_path
            
            # Controleer of we alle verplichte bestanden hebben
            required_files = ['bia', 'components']
            missing_files = [f for f in required_files if f not in csv_files]
            if missing_files:
                flash(f'Ontbrekende verplichte bestanden: {", ".join(missing_files)}')
                return redirect(request.url)
            
            # Importeer BIA
            df_bia = pd.read_csv(csv_files['bia'])
            
            # Functie om datumstrings om te zetten naar Python date objecten
            import datetime
            def parse_date(date_str):
                if pd.isna(date_str) or date_str == '' or date_str == 'None' or date_str is None:
                    return None
                try:
                    # Probeer verschillende datumformaten
                    formats = ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
                    for fmt in formats:
                        try:
                            return datetime.datetime.strptime(str(date_str), fmt).date()
                        except ValueError:
                            continue
                    # Als geen van de formats werkt, return None
                    return None
                except Exception:
                    return None
            
            for _, row in df_bia.iterrows():
                # Controleer of BIA al bestaat
                existing_bia = app_db.session.query(Context_Scope).filter(Context_Scope.name == row['BIA Name']).first()
                
                # Converteer datum velden naar Python date objecten
                start_date = parse_date(row.get('BIA Start Date'))
                end_date = parse_date(row.get('BIA End Date'))
                last_update = parse_date(row.get('BIA Last Update'))
                
                if existing_bia:
                    # Update bestaande BIA
                    existing_bia.responsible = row.get('BIA Responsible', '')
                    existing_bia.coordinator = row.get('BIA Coordinator', '')
                    existing_bia.start_date = start_date
                    existing_bia.end_date = end_date
                    existing_bia.last_update = last_update
                    existing_bia.service_description = row.get('Service Description', '')
                    existing_bia.knowledge = row.get('Knowledge', '')
                    existing_bia.interfaces = row.get('Interfaces', '')
                    existing_bia.mission_critical = row.get('mission_critical', '')
                    existing_bia.support_contracts = row.get('support_contracts', '')
                    existing_bia.security_supplier = row.get('security_supplier', '')
                    existing_bia.user_amount = row.get('user_amount', '')
                    existing_bia.scope_description = row.get('scope_description', '')
                    existing_bia.risk_assessment_human = row.get('risk_assessment_human', '')
                    existing_bia.risk_assessment_process = row.get('risk_assessment_process', '')
                    existing_bia.risk_assessment_technological = row.get('risk_assessment_technological', '')
                    existing_bia.project_leader = row.get('project_leader', '')
                    existing_bia.risk_owner = row.get('risk_owner', '')
                    existing_bia.product_owner = row.get('product_owner', '')
                    existing_bia.technical_administrator = row.get('technical_administrator', '')
                    existing_bia.security_manager = row.get('security_manager', '')
                    existing_bia.incident_contact = row.get('incident_contact', '')
                else:
                    # Maak nieuwe BIA
                    new_bia = Context_Scope(
                        name=row['BIA Name'],
                        responsible=row.get('BIA Responsible', ''),
                        coordinator=row.get('BIA Coordinator', ''),
                        start_date=start_date,
                        end_date=end_date,
                        last_update=last_update,
                        service_description=row.get('Service Description', ''),
                        knowledge=row.get('Knowledge', ''),
                        interfaces=row.get('Interfaces', ''),
                        mission_critical=row.get('mission_critical', ''),
                        support_contracts=row.get('support_contracts', ''),
                        security_supplier=row.get('security_supplier', ''),
                        user_amount=row.get('user_amount', ''),
                        scope_description=row.get('scope_description', ''),
                        risk_assessment_human=row.get('risk_assessment_human', ''),
                        risk_assessment_process=row.get('risk_assessment_process', ''),
                        risk_assessment_technological=row.get('risk_assessment_technological', ''),
                        project_leader=row.get('project_leader', ''),
                        risk_owner=row.get('risk_owner', ''),
                        product_owner=row.get('product_owner', ''),
                        technical_administrator=row.get('technical_administrator', ''),
                        security_manager=row.get('security_manager', ''),
                        incident_contact=row.get('incident_contact', '')
                    )
                    app_db.session.add(new_bia)
            
            # Commit BIA changes
            app_db.session.commit()
            
            # Verder gaan met de rest van de import...
            bia_name = df_bia['BIA Name'].iloc[0]
            
            # Importeer Components
            if 'components' in csv_files:
                df_components = pd.read_csv(csv_files['components'])
                # Verwijder bestaande componenten voor deze BIA
                app_db.session.query(Components).filter(Components.name == bia_name).delete()
                
                for _, row in df_components.iterrows():
                    new_component = Components(
                        name=bia_name,
                        component_name=row['Component name'],
                        processes_dependencies=row.get('Process Dependencies', ''),
                        info_type=row.get('Type of information', ''),
                        info_owner=row.get('Information Owner', ''),
                        user_type=row.get('Types of users', ''),
                        description=row.get('Description of the component', '')
                    )
                    app_db.session.add(new_component)
            
            # Importeer Consequences
            if 'consequences' in csv_files:
                df_consequences = pd.read_csv(csv_files['consequences'])
                # Verwijder bestaande consequences voor deze componenten
                component_names = df_components['Component name'].tolist()
                app_db.session.query(Consequences).filter(Consequences.component_name.in_(component_names)).delete()
                
                for _, row in df_consequences.iterrows():
                    new_consequence = Consequences(
                        component_name=row['Gerelateerd aan Component'],
                        consequence_category=row.get('Category of consequence', ''),
                        security_property=row.get('Property of Security', ''),
                        consequence_worstcase=row.get('Worstcase consequence', ''),
                        justification_worstcase=row.get('Justification for worst consequence', ''),
                        consequence_realisticcase=row.get('Realistic consequence', ''),
                        justification_realisticcase=row.get('Justification for realistic consequence', '')
                    )
                    app_db.session.add(new_consequence)
            
            # Importeer Availability Requirements
            if 'availability' in csv_files:
                df_availability = pd.read_csv(csv_files['availability'])
                # Verwijder bestaande availability vereisten voor deze componenten
                component_names = df_components['Component name'].tolist()
                app_db.session.query(Availability_Requirements).filter(Availability_Requirements.component_name.in_(component_names)).delete()
                
                for _, row in df_availability.iterrows():
                    new_availability = Availability_Requirements(
                        component_name=row['Gerelateerd aan Component'],
                        mtd=row.get('Maximum Tolerable Downtime', ''),
                        rto=row.get('Recovery Time Objective', ''),
                        rpo=row.get('Recovery Point Objective', ''),
                        masl=row.get('Minimum Acceptable Service Level', '')
                    )
                    app_db.session.add(new_availability)
            
            # Importeer Summary
            if 'summary' in csv_files:
                df_summary = pd.read_csv(csv_files['summary'])
                # Verwijder bestaande summary voor deze BIA
                app_db.session.query(Summary).filter(Summary.name == bia_name).delete()
                
                for _, row in df_summary.iterrows():
                    new_summary = Summary(
                        name=bia_name,
                        summary_text=row.get('Summary Test', '')
                    )
                    app_db.session.add(new_summary)
            
            # Importeer Consequence Choices als die beschikbaar zijn
            if 'choices' in csv_files:
                df_choices = pd.read_csv(csv_files['choices'])
                # Alleen importeren als de tabel leeg is, anders niet overschrijven
                if app_db.session.query(ConsequenceChoices).count() == 0:
                    for _, row in df_choices.iterrows():
                        new_choice = ConsequenceChoices(
                            consequence_worstcase=row.get('Ergste geval consequentie', ''),
                            consequence_realisticcase=row.get('Realistisch geval consequentie', '')
                        )
                        app_db.session.add(new_choice)
            
            # Importeer References als die beschikbaar zijn
            if 'references' in csv_files:
                df_references = pd.read_csv(csv_files['references'])
                # Alleen importeren als de tabel leeg is, anders niet overschrijven
                if app_db.session.query(References).count() == 0:
                    for _, row in df_references.iterrows():
                        new_reference = References(
                            consequence_category=row.get('Consequentie categorie', ''),
                            consequence_insignificant=row.get('Consequentie onbeduidend', ''),
                            consequence_small=row.get('Consequentie klein', ''),
                            consequence_medium=row.get('Consequentie gemiddeld', ''),
                            consequence_large=row.get('Consequentie groot', ''),
                            consequence_huge=row.get('Consequentie enorm', '')
                        )
                        app_db.session.add(new_reference)
            # Importeer AI Identification
            if 'ai_identification' in csv_files:
                df_ai_identification = pd.read_csv(csv_files['ai_identification'])
                # Verwijder bestaande AI identificaties voor deze componenten
                component_names = df_components['Component name'].tolist()
                app_db.session.query(AIIdentificatie).filter(AIIdentificatie.component_name.in_(component_names)).delete()
    
                for _, row in df_ai_identification.iterrows():
                    new_ai_identification = AIIdentificatie(
                    component_name=row['Gerelateerd aan Component'],
                    category=row.get('AI Category', ''),
                    motivatie=row.get('AI Justification', '')
                )
                app_db.session.add(new_ai_identification)
            
            # Commit alle wijzigingen
            app_db.session.commit()
            
            flash('BIA succesvol geïmporteerd!')
            return redirect(url_for('manage_data.bia_list'))
            
        except Exception as e:
            app_db.session.rollback()
            flash(f'Fout bij importeren: {str(e)}')
            return redirect(request.url)
        finally:
            # Verwijder tijdelijke directory
            shutil.rmtree(temp_dir)
    
    # GET request toont het upload formulier
    return render_template('bia_import.html')
@manage_data_blueprint.route('/consequence_choices/list', methods=['GET', 'POST'])
def consequence_choices_list():
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Aantal items per pagina

    query = app_db.session.query(ConsequenceChoices).order_by(ConsequenceChoices.id)
    total = query.count()
    
    offset = (page - 1) * per_page
    choices = query.offset(offset).limit(per_page).all()
    
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': (total + per_page - 1) // per_page
    }

    thead_th_items = [
        {'col_title': '#'},
        {'col_title': 'Realistic Case'},
        {'col_title': 'Worst Case'},
        {'col_title': 'Delete'}
    ]

    tbody_tr_items = []
    for choice in choices:
        tbody_tr_items.append([
            {'col_value': choice.id},
            {'col_value': choice.consequence_realisticcase},
            {'col_value': choice.consequence_worstcase},
            {'col_value': 'Delete', 'url': url_for('manage_data.consequence_choices_delete', choices_id=choice.id)}
        ])

    return render_template(
        'items_list.html',
        title='Consequence Choices',
        thead_th_items=thead_th_items,
        tbody_tr_items=tbody_tr_items,
        item_new_url=url_for('manage_data.consequence_choices_new'),
        item_new_text='New Consequence Choice',
        pagination=pagination
    )
@manage_data_blueprint.route('/consequence_choices/new', methods=['GET', 'POST'])
def consequence_choices_new():
    item = ConsequenceChoices()
    form = ConsequenceChoicesNewForm()

    if form.validate_on_submit():
        form.populate_obj(item)
        app_db.session.add(item)
        app_db.session.commit()
        flash('Consequence choice added: ' + item.consequence_realisticcase, 'info')
        return redirect(url_for('manage_data.consequence_choices_list'))

    return render_template('item_new_edit.html', title='New Consequence Choice', form=form)

@manage_data_blueprint.route('/consequence_choices/edit/<int:choices_id>', methods=['GET', 'POST'])
def consequence_choices_edit(choices_id):
    item = app_db.session.query(ConsequenceChoices).filter(ConsequenceChoices.id == choices_id).first()
    if item is None:
        abort(403)

    form = ConsequenceChoicesEditForm(obj=item)

    if form.validate_on_submit():
        form.populate_obj(item)
        app_db.session.commit()
        flash('Consequence choice updated: ' + item.consequence_realisticcase, 'info')
        return redirect(url_for('manage_data.consequence_choices_list'))

    return render_template('item_new_edit.html', title='Edit Consequence Choice', form=form)

@manage_data_blueprint.route('/consequence_choices/delete/<int:choices_id>', methods=['GET', 'POST'])
def consequence_choices_delete(choices_id):
    item = app_db.session.query(ConsequenceChoices).filter(ConsequenceChoices.id == choices_id).first()
    if item is None:
        abort(403)

    form = ConsequenceChoicesDeleteForm(obj=item)

    item_name = f"{item.consequence_realisticcase} - {item.consequence_worstcase}"
    if form.validate_on_submit():
        app_db.session.delete(item)
        app_db.session.commit()
        flash('Deleted consequence choice: ' + item_name, 'info')
        return redirect(url_for('manage_data.consequence_choices_list'))

    return render_template('item_delete.html', title='Delete Consequence Choice', item_name=item_name, form=form)

@manage_data_blueprint.route('/security_property/list', methods=['GET', 'POST'])
def security_property_list():
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Aantal items per pagina

    query = app_db.session.query(SecurityProperties).order_by(SecurityProperties.id)
    total = query.count()
    
    offset = (page - 1) * per_page
    properties = query.offset(offset).limit(per_page).all()
    
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': (total + per_page - 1) // per_page
    }

    thead_th_items = [
        {'col_title': '#'},
        {'col_title': 'Security Property'},
        {'col_title': 'Delete'}
    ]

    tbody_tr_items = []
    for prop in properties:
        tbody_tr_items.append([
            {'col_value': prop.id},
            {'col_value': prop.security_property, 'url': url_for('manage_data.security_property_edit', property_id=prop.id)},
            {'col_value': 'Delete', 'url': url_for('manage_data.security_property_delete', property_id=prop.id)}
        ])

    return render_template(
        'items_list.html',
        title='Security Properties',
        thead_th_items=thead_th_items,
        tbody_tr_items=tbody_tr_items,
        item_new_url=url_for('manage_data.security_property_new'),
        item_new_text='New Security Property',
        pagination=pagination
    )

@manage_data_blueprint.route('/security_property/new', methods=['GET', 'POST'])
def security_property_new():
    item = SecurityProperties()
    form = SecurityPropertyNewForm()

    if form.validate_on_submit():
        form.populate_obj(item)
        app_db.session.add(item)
        app_db.session.commit()
        flash('Security property added: ' + item.security_property, 'info')
        return redirect(url_for('manage_data.security_property_list'))

    return render_template('item_new_edit.html', title='New Security Property', form=form)

@manage_data_blueprint.route('/security_property/edit/<int:property_id>', methods=['GET', 'POST'])
def security_property_edit(property_id):
    item = app_db.session.query(SecurityProperties).filter(SecurityProperties.id == property_id).first()
    if item is None:
        abort(403)

    form = SecurityPropertyEditForm(obj=item)

    if form.validate_on_submit():
        form.populate_obj(item)
        app_db.session.commit()
        flash('Security property updated: ' + item.security_property, 'info')
        return redirect(url_for('manage_data.security_property_list'))

    return render_template('item_new_edit.html', title='Edit Security Property', form=form)

@manage_data_blueprint.route('/security_property/delete/<int:property_id>', methods=['GET', 'POST'])
def security_property_delete(property_id):
    item = app_db.session.query(SecurityProperties).filter(SecurityProperties.id == property_id).first()
    if item is None:
        abort(403)

    form = SecurityPropertyDeleteForm(obj=item)

    item_name = item.security_property
    if form.validate_on_submit():
        app_db.session.delete(item)
        app_db.session.commit()
        flash('Deleted security property: ' + item_name, 'info')
        return redirect(url_for('manage_data.security_property_list'))

    return render_template('item_delete.html', title='Delete Security Property', item_name=item_name, form=form)

@manage_data_blueprint.route('/ai_identificatie/list', methods=['GET', 'POST'])
def ai_identificatie_list():
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Number of items per page

    query = app_db.session.query(AIIdentificatie).order_by(AIIdentificatie.component_name)
    total = query.count()
    ai_identificaties = query.offset((page - 1) * per_page).limit(per_page).all()

    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': (total + per_page - 1) // per_page
    }

    thead_th_items = [
        {'col_title': '#'},
        {'col_title': 'Component'},
        {'col_title': 'AI Category'},
        {'col_title': 'Motivation'},
        {'col_title': 'Delete'}
    ]

    tbody_tr_items = []
    for ai in ai_identificaties:
        tbody_tr_items.append([
            {'col_value': ai.id},
            {'col_value': ai.component_name, 'url': url_for('manage_data.ai_identificatie_edit', ai_id=ai.id)},
            {'col_value': ai.category},
            {'col_value': ai.motivatie[:50] + '...' if len(ai.motivatie) > 50 else ai.motivatie},
            {'col_value': 'Delete', 'url': url_for('manage_data.ai_identificatie_delete', ai_id=ai.id)}
        ])

    return render_template(
        'items_list.html',
        title='AI Identifications',
        thead_th_items=thead_th_items,
        tbody_tr_items=tbody_tr_items,
        item_new_url=url_for('manage_data.ai_identificatie_new'),
        item_new_text='New AI Identification',
        pagination=pagination
    )
@manage_data_blueprint.route('/ai_identificatie/new', methods=['GET', 'POST'])
def ai_identificatie_new():
    form = AIIdentificatieNewForm()
    form.component_name.choices = [(c.component_name, c.component_name) for c in app_db.session.query(Components).all()]

    if form.validate_on_submit():
        ai_identificatie = AIIdentificatie(
            component_name=form.component_name.data,
            category=form.category.data,
            motivatie=form.motivatie.data
        )
        app_db.session.add(ai_identificatie)
        app_db.session.commit()
        flash('AI Identificatie toegevoegd', 'success')
        return redirect(url_for('manage_data.ai_identificatie_list'))

    return render_template('item_new_edit.html', title='Nieuwe AI Identificatie', form=form)

@manage_data_blueprint.route('/ai_identificatie/edit/<int:ai_id>', methods=['GET', 'POST'])
def ai_identificatie_edit(ai_id):
    ai_identificatie = app_db.session.query(AIIdentificatie).filter_by(id=ai_id).first()
    if ai_identificatie is None:
        abort(404)
    
    form = AIIdentificatieEditForm(obj=ai_identificatie)
    form.component_name.choices = [(c.component_name, c.component_name) for c in app_db.session.query(Components).all()]

    if form.validate_on_submit():
        form.populate_obj(ai_identificatie)
        app_db.session.commit()
        flash('AI Identificatie bijgewerkt', 'success')
        return redirect(url_for('manage_data.ai_identificatie_list'))

    return render_template('item_new_edit.html', title='AI Identificatie Bewerken', form=form)

@manage_data_blueprint.route('/ai_identificatie/delete/<int:ai_id>', methods=['GET', 'POST'])
def ai_identificatie_delete(ai_id):
    ai_identificatie = app_db.session.query(AIIdentificatie).filter_by(id=ai_id).first()
    if ai_identificatie is None:
        abort(404)
    
    form = AIIdentificatieDeleteForm()

    if form.validate_on_submit():
        app_db.session.delete(ai_identificatie)
        app_db.session.commit()
        flash('AI Identificatie verwijderd', 'success')
        return redirect(url_for('manage_data.ai_identificatie_list'))

    return render_template('item_delete.html', title='AI Identificatie Verwijderen', 
                           item_name=f"AI Identificatie voor {ai_identificatie.component_name}", 
                           form=form)
@manage_data_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        app_db.session.add(user)
        app_db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('manage_data.login'))  # Assuming you have a login route
    return render_template('register.html', title='Register', form=form)