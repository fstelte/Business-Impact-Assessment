
# app/routes.py
# Behandelt de hoofdroutes van de applicatie (CRUD voor BIA).

from flask import render_template, flash, redirect, url_for, request, Blueprint, jsonify,  current_app, send_file, abort
from flask_login import current_user, login_required, login_user
from .utils import (
    export_to_csv,
    import_from_csv,
    get_impact_level,
    get_impact_color,
    export_to_sql,
    import_sql_file,
)
from . import db
from . import auth
from .models import ContextScope, User, Component, Consequences, AvailabilityRequirements, AIIdentificatie, Summary
from .forms import ContextScopeForm, ConsequenceForm, RegistrationForm, ComponentForm, SummaryForm, ImportCSVForm, ChangePasswordForm,ImportSQLForm
from datetime import date, datetime
from .session_security import require_fresh_login
from werkzeug.utils import secure_filename
import logging
import os
import zipfile
import pandas as pd
import tempfile
import shutil
import io
import csv

main = Blueprint('main', __name__)

def get_impact_color(impact):
    impact_colors = {
        'catastrophic': 'badge bg-danger',
        'major': 'badge bg-warning text-dark',
        'moderate': 'badge bg-info text-dark',
        'minor': 'badge bg-primary',
        'insignificant': 'badge bg-success'
    }
    return impact_colors.get(impact.lower(), 'badge bg-secondary')

def get_cia_impact(consequence, property):
    if consequence.security_property.lower() == property:
        return consequence.consequence_realisticcase
    return 'insignificant'

def get_max_cia_impact(consequences):
    max_impacts = {
        'confidentiality': 'insignificant',
        'integrity': 'insignificant',
        'availability': 'insignificant'
    }
    impact_order = ['insignificant', 'minor', 'moderate', 'major', 'catastrophic']
    
    for consequence in consequences:
        for property in ['confidentiality', 'integrity', 'availability']:
            impact = get_cia_impact(consequence, property)
            if impact_order.index(impact) > impact_order.index(max_impacts[property]):
                max_impacts[property] = impact
    
    return max_impacts

@main.route('/')
@main.route('/index')
@login_required
def index():
    """Hoofdpagina/dashboard die alle BIA items toont."""
    items = ContextScope.query.order_by(ContextScope.last_update.desc()).all()
    return render_template('index.html', title='Dashboard', items=items)

@main.route('/item/new', methods=['GET', 'POST'])
@login_required
def new_item():
    """Route voor het aanmaken van een nieuw BIA item."""
    form = ContextScopeForm()
    component_form = ComponentForm() 
    if form.validate_on_submit():
        item = ContextScope(
            name=form.name.data,
            responsible=form.responsible.data,
            coordinator=form.coordinator.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            service_description=form.service_description.data,
            knowledge=form.knowledge.data,
            interfaces=form.interfaces.data,
            mission_critical=form.mission_critical.data,
            support_contracts=form.support_contracts.data,
            security_supplier=form.security_supplier.data,
            user_amount=form.user_amount.data,
            scope_description=form.scope_description.data,
            risk_assessment_human=form.risk_assessment_human.data,
            risk_assessment_process=form.risk_assessment_process.data,
            risk_assessment_technological=form.risk_assessment_technological.data,
            ai_model=form.ai_model.data,
            project_leader=form.project_leader.data,
            risk_owner=form.risk_owner.data,
            product_owner=form.product_owner.data,
            technical_administrator=form.technical_administrator.data,
            security_manager=form.security_manager.data,
            incident_contact=form.incident_contact.data,
            author=current_user
        )
        db.session.add(item)
        db.session.commit()
        flash('BIA Added successfull!', 'success')
        return redirect(url_for('main.index'))
    return render_template('create_edit_item.html', title='New BIA', form=form, legend='New BIA', component_form=component_form, item=None)

@main.route('/item/<int:item_id>')
@login_required
def view_item(item_id):
    item = ContextScope.query.get_or_404(item_id)
    
    consequences = []
    for component in item.components:
        consequences.extend(component.consequences)
    
    max_cia_impact = get_max_cia_impact(consequences)
    
    ai_identifications = {}
    for component in item.components:
        ai_identification = AIIdentificatie.query.filter_by(component_id=component.id).first()
        if ai_identification and ai_identification.category != 'No AI':
            ai_identifications[component.id] = ai_identification
    
    return render_template('view_item.html', 
                           title=item.name, 
                           item=item, 
                           consequences=consequences,
                           get_impact_color=get_impact_color, 
                           get_cia_impact=get_cia_impact,
                           max_cia_impact=max_cia_impact,
                           ai_identifications=ai_identifications)


@main.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    """Route voor het bewerken van een bestaand item."""
    
    item = ContextScope.query.get_or_404(item_id)

    if item.author != current_user:
        flash('You do not have permissions to edit this item.', 'danger')
        return redirect(url_for('main.index'))
    
    # Laad het formulier en vul het met de data van het 'item' object.
    # Dit werkt voor zowel GET als POST requests.
    form = ContextScopeForm(obj=item)
    
    # ComponentForm is nog steeds nodig voor de modal, zoals je correct opmerkte.
    component_form = ComponentForm()

    if form.validate_on_submit():
        # Gebruik populate_obj om alle formulierdata in het 'item' object te laden.
        # Dit werkt voor alle velden, inclusief de gecorrigeerde RadioFields.
        form.populate_obj(item)
        
        # Enkel velden die niet in het formulier staan, moet je nog handmatig instellen.
        item.last_update = date.today()

        db.session.commit()
        flash('BIA has been updated!', 'success')
        return redirect(url_for('main.view_item', item_id=item.id))

    # Het 'elif request.method == 'GET':' blok is niet meer nodig.
    # WTForms vult het formulier al via de 'obj=item' parameter.
    
    return render_template('create_edit_item.html', title='Edit BIA', form=form, component_form=component_form, item=item)

@main.route('/item/<int:item_id>/delete', methods=['POST'])
@login_required
@require_fresh_login(max_age_minutes=30)  # Require login within last 30 minutes
def delete_item(item_id):
    """Route voor het verwijderen van een item."""
    item = ContextScope.query.get_or_404(item_id)
    if item.author != current_user:
        flash('You do not have permissions to remove this item.', 'danger')
        return redirect(url_for('main.index'))
    
    db.session.delete(item)
    db.session.commit()
    flash('Successfully removed item.', 'success')
    return redirect(url_for('main.index'))

@main.route('/add_component', methods=['POST'])
@login_required
def add_component():
    form = ComponentForm()
    if form.validate_on_submit():
        bia_id = request.form.get('bia_id')
        bia = ContextScope.query.get(bia_id) if bia_id else None
        component = Component(
            name=form.name.data,
            info_type=form.info_type.data,
            info_owner=form.info_owner.data,
            user_type=form.user_type.data,
            description=form.description.data,
            context_scope=bia
        )
        db.session.add(component)
        db.session.commit()
        return jsonify({'success': True, 'id': component.id, 'name': component.name})
    return jsonify({'success': False, 'errors': form.errors}), 400

@main.route('/delete_component/<int:component_id>', methods=['POST'])
@login_required
def delete_component(component_id):
    component = Component.query.get_or_404(component_id)
    db.session.delete(component)
    db.session.commit()
    return jsonify({'success': True})

@main.route('/update_component/<int:component_id>', methods=['POST'])
@login_required
def update_component(component_id):
    component = Component.query.get_or_404(component_id)
    form = ComponentForm()
    
    if form.validate_on_submit():
        component.name = form.name.data
        component.info_type = form.info_type.data
        component.info_owner = form.info_owner.data
        component.user_type = form.user_type.data
        component.process_dependencies = form.process_dependencies.data
        component.description = form.description.data
        db.session.commit()
        return jsonify({'success': True, 'name': component.name})
    
    return jsonify({'success': False, 'errors': form.errors}), 400


@main.route('/components')
@login_required
def view_components():
    # Haal alle unieke ContextScope namen op
    context_scopes = ContextScope.query.with_entities(ContextScope.name).distinct().all()
    context_scope_names = [scope[0] for scope in context_scopes]
    
    # Haal de geselecteerde ContextScope op uit de query parameters
    selected_scope = request.args.get('scope', 'all')
    
    # Filter de componenten op basis van de geselecteerde ContextScope
    if selected_scope != 'all':
        # Gebruik een LIKE query om gedeeltelijke overeenkomsten te vinden
        components = Component.query.join(ContextScope).filter(ContextScope.name.like(f"%{selected_scope}%")).all()
        if not components:
            # Als er geen exacte match is, probeer dan een gedeeltelijke match
            partial_match = ContextScope.query.filter(ContextScope.name.like(f"%{selected_scope}%")).first()
            if partial_match:
                components = Component.query.filter_by(context_scope_id=partial_match.id).all()
                if components:
                    flash(f"Showing components for BIA: {partial_match.name}", 'info')
                else:
                    flash(f"No components found for BIA: {partial_match.name}", 'info')
            else:
                flash(f"No BIA found matching: {selected_scope}", 'info')
    else:
        components = Component.query.all()
    
    # Log de gevonden componenten voor debugging
    print(f"Selected scope: {selected_scope}")
    print(f"Number of components found: {len(components)}")
    for component in components:
        print(f"Component: {component.name}, BIA: {component.context_scope.name}")
    
    # Maak een instantie van het ConsequenceForm
    consequence_form = ConsequenceForm()
    
    return render_template('components.html', 
                           components=components, 
                           context_scope_names=context_scope_names,
                           selected_scope=selected_scope,
                           consequence_form=consequence_form)

@main.route('/get_component/<int:component_id>')
def get_component(component_id):
    component = Component.query.get_or_404(component_id)
    return jsonify({
        'id': component.id,
        'name': component.name,
        'info_type': component.info_type,
        'info_owner': component.info_owner,
        'user_type': component.user_type,
        'description': component.description,
        'process_dependencies': component.process_dependencies,
        'bia_name': component.context_scope.name,
        'consequences_count': len(component.consequences)
    })

@main.route('/add_consequence/<int:component_id>', methods=['POST'])
@login_required
def add_consequence(component_id):
    data = request.json
    print("Received data:", data)  # Debug print
    form = ConsequenceForm(data=data)
    if form.validate():
        categories = data.get('consequence_category', [])
        print("Received categories:", categories)  # Debug print
        
        if not isinstance(categories, list):
            categories = [categories]
        
        print("Processed categories:", categories)  # Debug print
        
        for category in categories:
            consequence = Consequences(
                component_id=component_id,
                consequence_category=category,
                security_property=form.security_property.data,
                consequence_worstcase=form.consequence_worstcase.data,
                justification_worstcase=form.justification_worstcase.data,
                consequence_realisticcase=form.consequence_realisticcase.data,
                justification_realisticcase=form.justification_realisticcase.data
            )
            db.session.add(consequence)
        db.session.commit()
        return jsonify({'success': True, 'message': f'{len(categories)} consequences added successfully'})
    return jsonify({'success': False, 'errors': form.errors}), 400

@main.route('/get_consequence/<int:consequence_id>')
def get_consequence(consequence_id):
    consequence = Consequences.query.get_or_404(consequence_id)
    data = {
        'id': consequence.id,
        'consequence_category': consequence.consequence_category,  # Verwijder de list check hier
        'security_property': consequence.security_property,
        'consequence_worstcase': consequence.consequence_worstcase,
        'justification_worstcase': consequence.justification_worstcase,
        'consequence_realisticcase': consequence.consequence_realisticcase,
        'justification_realisticcase': consequence.justification_realisticcase
    }
    print("Sending consequence data:", data)  # Log de verzonden data
    return jsonify(data)

@main.route('/edit_consequence/<int:consequence_id>', methods=['POST'])
@login_required
def edit_consequence(consequence_id):
    consequence = Consequences.query.get_or_404(consequence_id)
    data = request.json
    
    # Validate required fields manually since we're not using WTForms validation
    required_fields = ['consequence_category', 'security_property', 'consequence_worstcase', 'consequence_realisticcase']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'errors': {field: ['This field is required.']}}), 400
    
    try:
        # Update the consequence directly without form validation
        consequence.consequence_category = data.get('consequence_category')
        consequence.security_property = data.get('security_property')
        consequence.consequence_worstcase = data.get('consequence_worstcase')
        consequence.justification_worstcase = data.get('justification_worstcase', '')
        consequence.consequence_realisticcase = data.get('consequence_realisticcase')
        consequence.justification_realisticcase = data.get('justification_realisticcase', '')
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Consequence updated successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"Error updating consequence: {str(e)}")  # For debugging
        return jsonify({'success': False, 'errors': {'general': ['An error occurred while updating the consequence.']}}), 500


@main.route('/delete_consequence/<int:consequence_id>', methods=['POST'])
@login_required
def delete_consequence(consequence_id):
    consequence = Consequences.query.get_or_404(consequence_id)
    db.session.delete(consequence)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Consequence deleted successfully.'})

@main.route('/consequences/<int:component_id>')
@login_required
def view_consequences(component_id):
    component = Component.query.get_or_404(component_id)
    consequences = Consequences.query.filter_by(component_id=component_id).all()
    
    if not consequences:
        flash('No consequences found for this component.', 'info')
    
    consequence_form = ConsequenceForm()  # Voeg deze regel toe
    
    return render_template('view_consequences.html', 
                           component=component, 
                           consequences=consequences,
                           consequence_form=consequence_form)  # Voeg consequence_form toe aan de context

@main.route('/get_availability/<int:component_id>')
@login_required
def get_availability(component_id):
    availability = AvailabilityRequirements.query.filter_by(component_id=component_id).first()
    if availability:
        return jsonify({
            'mtd': availability.mtd,
            'rto': availability.rto,
            'rpo': availability.rpo,
            'masl': availability.masl
        })
    return jsonify({})

@main.route('/update_availability/<int:component_id>', methods=['POST'])
@login_required
def update_availability(component_id):
    availability = AvailabilityRequirements.query.filter_by(component_id=component_id).first()
    if not availability:
        availability = AvailabilityRequirements(component_id=component_id)
        db.session.add(availability)
    
    availability.mtd = request.form.get('mtd')
    availability.rto = request.form.get('rto')
    availability.rpo = request.form.get('rpo')
    availability.masl = request.form.get('masl')
    
    db.session.commit()
    return jsonify({'success': True})

@main.route('/add_ai_identification/<int:component_id>', methods=['POST'])
@login_required
def add_ai_identification(component_id):
    # Controleer eerst of er al een AI-identificatie bestaat voor deze component
    existing_ai_identification = AIIdentificatie.query.filter_by(component_id=component_id).first()
    
    if existing_ai_identification:
        # Als er al een bestaat, update deze
        existing_ai_identification.category = request.form.get('category')
        existing_ai_identification.motivatie = request.form.get('motivatie')
    else:
        # Als er nog geen bestaat, maak een nieuwe aan
        new_ai_identification = AIIdentificatie(
            component_id=component_id,
            category=request.form.get('category'),
            motivatie=request.form.get('motivatie')
        )
        db.session.add(new_ai_identification)
    
    db.session.commit()
    return jsonify({'success': True})

# Update de bestaande update_ai_identification functie
@main.route('/update_ai_identification/<int:component_id>', methods=['POST'])
@login_required
def update_ai_identification(component_id):
    ai_identification = AIIdentificatie.query.filter_by(component_id=component_id).first()
    
    if not ai_identification:
        # Als er geen AI-identificatie bestaat, maak een nieuwe aan
        ai_identification = AIIdentificatie(component_id=component_id)
        db.session.add(ai_identification)
    
    ai_identification.category = request.form.get('category')
    ai_identification.motivatie = request.form.get('motivatie')
    
    db.session.commit()
    return jsonify({'success': True})

@main.route('/get_ai_identification/<int:component_id>')
@login_required
def get_ai_identification(component_id):
    ai_identification = AIIdentificatie.query.filter_by(component_id=component_id).first()
    if ai_identification:
        return jsonify({
            'exists': True,
            'category': ai_identification.category,
            'motivatie': ai_identification.motivatie
        })
    else:
        return jsonify({
            'exists': False,
            'category': 'No AI',
            'motivatie': ''
        }), 404  # We gebruiken nog steeds 404 voor consistentie, maar geven wel data terug
    
@main.route('/item/<int:item_id>/summary', methods=['GET', 'POST'])
@login_required
def manage_summary(item_id):
    item = ContextScope.query.get_or_404(item_id)
    if item.author != current_user:
        abort(403)
    
    form = SummaryForm()
    
    if form.validate_on_submit():
        if item.summary:
            item.summary.content = form.content.data
        else:
            new_summary = Summary(content=form.content.data, context_scope=item)
            db.session.add(new_summary)
        db.session.commit()
        flash('Summary updated successfully.', 'success')
        return redirect(url_for('main.view_item', item_id=item.id))
    
    if item.summary:
        form.content.data = item.summary.content
    
    return render_template('manage_summary.html', form=form, item=item)

@main.route('/item/<int:item_id>/summary/delete', methods=['POST'])
@login_required
def delete_summary(item_id):
    item = ContextScope.query.get_or_404(item_id)
    if item.author != current_user:
        abort(403)
    
    if item.summary:
        db.session.delete(item.summary)
        db.session.commit()
        flash('Summary deleted successfully.', 'success')
    
    return redirect(url_for('main.view_item', item_id=item.id))

@main.route('/item/<int:item_id>/export', methods=['GET'])
@login_required
def export_item(item_id):
    """Exporteert de details van een BIA item als HTML-rapport."""
    item = ContextScope.query.get_or_404(item_id)
    
    # Verzamel alle gevolgen van alle componenten
    consequences = []
    for component in item.components:
        consequences.extend(component.consequences)
    
    # Bereken de maximale CIA impact
    max_cia_impact = get_max_cia_impact(consequences)
    
    # Haal de AI identificatie op voor het eerste component (als er een is)
    ai_identifications = {}
    for component in item.components:
        ai_identification = AIIdentificatie.query.filter_by(component_id=component.id).first()
        if ai_identification and ai_identification.category != 'No AI':
            ai_identifications[component.id] = ai_identification
    ai_risk_category = ai_identification.category if ai_identification else 'No AI'
    
    # Render de template naar een string
    html_content = render_template('export_item.html', 
                                   title=item.name, 
                                   item=item, 
                                   consequences=consequences,
                                   get_impact_color=get_impact_color, 
                                   get_cia_impact=get_cia_impact,
                                   max_cia_impact=max_cia_impact,
                                   ai_risk_category=ai_risk_category,
                                   ai_identifications=ai_identifications)
    
    # Maak een veilige bestandsnaam
    safe_filename = "".join([c for c in item.name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    filename = f"BIA_{safe_filename}.html"
    
    # Bepaal het pad waar het bestand moet worden opgeslagen
    export_path = os.path.join(current_app.root_path, 'exports')
    if not os.path.exists(export_path):
        os.makedirs(export_path)
    
    file_path = os.path.join(export_path, filename)
    
    # Schrijf de HTML-inhoud naar het bestand
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Stuur het bestand naar de gebruiker
    return send_file(file_path, as_attachment=True)


@main.route('/export_csv/<int:item_id>', methods=['GET'])
@login_required
def export_csv(item_id):
    item = ContextScope.query.get_or_404(item_id)
    if item.author != current_user:
        abort(403)

    # Maak een veilige mapnaam
    safe_folder_name = "".join([c for c in item.name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    export_folder = os.path.join(current_app.root_path, 'exports', safe_folder_name)

    # Maak de map aan als deze nog niet bestaat
    if not os.path.exists(export_folder):
        os.makedirs(export_folder)

    # Exporteer de CSV-bestanden
    csv_files = export_to_csv(item)

    # Schrijf elk CSV-bestand naar de map en verzamel bestandsinfo
    exported_files = []
    for filename, content in csv_files.items():
        file_path = os.path.join(export_folder, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Voeg bestandsinfo toe voor de template
        exported_files.append({
            'filename': filename,
            'path': safe_folder_name,
            'size': len(content.encode('utf-8'))  # Bestandsgrootte in bytes
        })

    flash(f'CSV-bestanden zijn succesvol geëxporteerd!', 'success')
    
    # Redirect naar de download overzichtspagina
    return render_template('csv_export_overview.html', 
                         item=item, 
                         exported_files=exported_files,
                         export_folder=safe_folder_name)

@main.route('/download_csv/<path:folder_name>/<filename>')
@login_required
def download_csv_file(folder_name, filename):
    """Route voor het downloaden van individuele CSV-bestanden."""
    file_path = os.path.join(current_app.root_path, 'exports', folder_name, filename)
    
    # Controleer of het bestand bestaat
    if not os.path.exists(file_path):
        flash('Bestand niet gevonden.', 'error')
        return redirect(url_for('main.index'))
    
    return send_file(file_path, as_attachment=True, download_name=filename)

@main.route('/import_csv', methods=['GET', 'POST'])
@login_required
def import_csv():
    form = ImportCSVForm()
    if request.method == 'POST':
        csv_files = {}
        
        try:
            print("Received files:", request.files)
            
            if not request.files:
                flash('Geen bestanden ontvangen in het verzoek', 'error')
                return redirect(request.url)
            
            file_mapping = {
                'bia': 'bia',
                'components': 'components',
                'consequences': 'consequences',
                'availability_requirements': 'availability_requirements',
                'ai_identification': 'ai_identification',
                'summary': 'summary'
            }
            
            for file_type, form_name in file_mapping.items():
                file = request.files.get(form_name)
                if file and file.filename != '':
                    # Verwijder alles voor de underscore in de bestandsnaam
                    original_filename = secure_filename(file.filename)
                    new_filename = original_filename.split('_', 1)[-1] if '_' in original_filename else original_filename
                    
                    # Lees de inhoud van het bestand direct
                    file_content = file.read().decode('utf-8')
                    
                    # Vervang lege velden (,, of , \n) door ,0, of ,0\n
                    # Dit zorgt ervoor dat lege numerieke velden als 0 worden geïnterpreteerd
                    processed_content = file_content.replace(',,', ',0,').replace(',\n', ',0\n')
                    # Herhaal om opeenvolgende lege velden te vangen
                    while ',,' in processed_content:
                        processed_content = processed_content.replace(',,', ',0,')

                    csv_files[file_type] = processed_content
                    print(f"{file_type} file content loaded: {new_filename}")
                else:
                    print(f"No file received for {file_type}")
            
            if 'bia' not in csv_files:
                flash('BIA bestand is verplicht', 'error')
                return redirect(request.url)
            
            print("CSV files to import:", csv_files.keys())
            
            import_from_csv(csv_files)
            
            flash('CSV-bestanden zijn succesvol geïmporteerd!', 'success')
            return redirect(url_for('main.index'))

        except Exception as e:
            flash(f'Er is een fout opgetreden tijdens het importeren: {str(e)}', 'error')
            logging.error(f"Import error: {str(e)}")
            print(f"Exception during import: {str(e)}")

    return render_template('import_csv.html', form=form)

@main.route('/change_password', methods=['GET', 'POST'])
@login_required
@require_fresh_login(max_age_minutes=15)  # Require very fresh login for password changes
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid current password.', 'danger')
    return render_template('change_password.html', form=form)

@main.route('/export_data_inventory')
@login_required
def export_data_inventory():
    """Exporteert een inventory van alle componenten met hun BIA informatie als CSV."""
    
    # Haal alle componenten op met hun gerelateerde ContextScope
    components = Component.query.join(ContextScope).all()
    
    # Maak CSV data
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    
    # Schrijf header
    csv_writer.writerow(['BIA', 'Systeem', 'Informatie', 'Eigenaar', 'Beheer'])
    
    # Schrijf data voor elke component
    for component in components:
        csv_writer.writerow([
            component.context_scope.name,  # BIA
            component.name,  # Systeem
            component.info_type or 'N/A',  # Informatie
            component.info_owner or 'N/A',  # Eigenaar
            component.context_scope.technical_administrator or 'N/A'  # Beheer
        ])
    
    # Maak een veilige bestandsnaam
    filename = f"Data_Inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Bepaal het pad waar het bestand moet worden opgeslagen
    export_path = os.path.join(current_app.root_path, 'exports')
    if not os.path.exists(export_path):
        os.makedirs(export_path)
    
    file_path = os.path.join(export_path, filename)
    
    # Schrijf de CSV-inhoud naar het bestand
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        f.write(csv_data.getvalue())
    
    # Stuur het bestand naar de gebruiker
    return send_file(file_path, as_attachment=True, download_name=filename)

@login_required
def export_all_consequences():
    """Exporteert alle CIA consequences van alle BIA's als HTML-rapport."""
    
    # Haal het type export op uit de query parameters (default: detailed)
    export_type = request.args.get('type', 'detailed')
    
    # Haal alle BIA's op met hun componenten en consequences
    bias = ContextScope.query.all()
    
    if export_type == 'summary':
        # Samenvattende versie: cumulatieve consequences per BIA
        bia_summaries = []
        
        # Debug: print alle BIA's
        print(f"Total BIAs found: {len(bias)}")
        
        for bia in bias:
            print(f"\nProcessing BIA: {bia.name}")
            print(f"  Components count: {len(bia.components)}")
            
            # Verzamel alle consequences voor deze BIA
            all_consequences_for_bia = []
            for component in bia.components:
                print(f"    Component: {component.name}, Consequences: {len(component.consequences)}")
                for consequence in component.consequences:
                    print(f"      - {consequence.security_property}: W={consequence.consequence_worstcase}, R={consequence.consequence_realisticcase}")
                all_consequences_for_bia.extend(component.consequences)
            
            print(f"  Total consequences for BIA: {len(all_consequences_for_bia)}")
            
            # Alleen BIA's met componenten EN consequences toevoegen
            if len(bia.components) > 0 and len(all_consequences_for_bia) > 0:
                # Initialiseer max_impacts met alle drie de security properties
                max_impacts = {
                    'Confidentiality': {'worstcase': None, 'realistic': None},
                    'Integrity': {'worstcase': None, 'realistic': None},
                    'Availability': {'worstcase': None, 'realistic': None}
                }
                
                # Bereken de maximale impact per security property
                for consequence in all_consequences_for_bia:
                    prop = consequence.security_property
                    
                    # Zorg ervoor dat de property key correct is (met hoofdletter)
                    if prop.lower() == 'confidentiality':
                        prop = 'Confidentiality'
                    elif prop.lower() == 'integrity':
                        prop = 'Integrity'
                    elif prop.lower() == 'availability':
                        prop = 'Availability'
                    
                    if prop in max_impacts:
                        current_worst = consequence.consequence_worstcase
                        current_realistic = consequence.consequence_realisticcase
                        
                        # Update worstcase als het de eerste is of hoger is
                        if (max_impacts[prop]['worstcase'] is None or 
                            get_impact_level(current_worst) > get_impact_level(max_impacts[prop]['worstcase'])):
                            max_impacts[prop]['worstcase'] = current_worst
                        
                        # Update realistic als het de eerste is of hoger is
                        if (max_impacts[prop]['realistic'] is None or 
                            get_impact_level(current_realistic) > get_impact_level(max_impacts[prop]['realistic'])):
                            max_impacts[prop]['realistic'] = current_realistic
                
                bia_summaries.append({
                    'bia_name': bia.name,
                    'component_count': len(bia.components),
                    'consequence_count': len(all_consequences_for_bia),
                    'max_impacts': max_impacts
                })
                
                print(f"  Added to summary with max_impacts: {max_impacts}")
        
        print(f"\nTotal BIA summaries created: {len(bia_summaries)}")
        
        # Genereer huidige datum/tijd
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Render de samenvattende template
        html_content = render_template('export_consequences_summary.html', 
                                       title='CIA Consequences Summary by BIA',
                                       bia_summaries=bia_summaries,
                                       current_datetime=current_datetime)
        
        filename = f"CIA_Consequences_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
    else:
        # Uitgebreide versie: alle consequences individueel
        all_consequences = []
        for bia in bias:
            for component in bia.components:
                for consequence in component.consequences:
                    all_consequences.append({
                        'bia_name': bia.name,
                        'component_name': component.name,
                        'consequence': consequence,
                        'justification': consequence.justification
                    })
        
        # Genereer huidige datum/tijd
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M%S')
        
        # Render de uitgebreide template
        html_content = render_template('export_all_consequences.html', 
                                       title='All CIA Consequences Overview',
                                       all_consequences=all_consequences,
                                       current_datetime=current_datetime)
        
        filename = f"All_CIA_Consequences_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    # Bepaal het pad waar het bestand moet worden opgeslagen
    export_path = os.path.join(current_app.root_path, 'exports')
    if not os.path.exists(export_path):
        os.makedirs(export_path)
    
    file_path = os.path.join(export_path, filename)
    
    # Schrijf de HTML-inhoud naar het bestand
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Stuur het bestand naar de gebruiker
    return send_file(file_path, as_attachment=True, download_name=filename)

main.add_url_rule('/export-all-consequences', 'export_all_consequences', export_all_consequences, methods=['GET'])

@main.route('/debug/consequences')
@login_required
def debug_consequences():
    """Debug route om consequences data te controleren"""
    bias = ContextScope.query.all()
    debug_info = []
    
    for bia in bias:
        bia_info = {
            'bia_name': bia.name,
            'bia_id': bia.id,
            'components': []
        }
        
        for component in bia.components:
            component_info = {
                'component_name': component.name,
                'component_id': component.id,
                'consequences': []
            }
            
            for consequence in component.consequences:
                consequence_info = {
                    'security_property': consequence.security_property,
                    'worstcase': consequence.consequence_worstcase,
                    'realistic': consequence.consequence_realisticcase,
                    'category': consequence.consequence_category
                }
                component_info['consequences'].append(consequence_info)
            
            bia_info['components'].append(component_info)
        
        debug_info.append(bia_info)
    
    return jsonify(debug_info)


@main.route('/bia/<int:item_id>/export/sql')
@login_required
def export_bia_sql(item_id):
    """Exporteert een specifieke BIA naar een SQL-bestand."""
    item = ContextScope.query.get_or_404(item_id)
    
    try:
        sql_data = export_to_sql(item)
        
        # Maak een veilige bestandsnaam
        safe_name = "".join(c for c in item.name if c.isalnum() or c in (' ', '_')).rstrip()
        filename = f"BIA_Export_{safe_name}_{datetime.now().strftime('%Y%m%d')}.sql"
        
        # Bepaal het pad waar het bestand moet worden opgeslagen
        export_path = os.path.join(current_app.root_path, 'exports')
        if not os.path.exists(export_path):
            os.makedirs(export_path)
        
        file_path = os.path.join(export_path, filename)
        
        # Schrijf de SQL-data naar het bestand
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(sql_data)
            
        # Stuur het bestand naar de gebruiker
        return send_file(file_path, as_attachment=True, download_name=filename)

    except Exception as e:
        flash(f'Error exporting BIA to SQL: {e}', 'danger')
        return redirect(url_for('main.bia_detail', item_id=item_id))

@main.route("/import-sql", methods=["GET", "POST"])
@login_required
def import_sql_form():
    form = ImportSQLForm()
    if form.validate_on_submit():
        try:
            import_sql_file(form.sql_file.data)
            flash("SQL-bestand succesvol geïmporteerd.", "success")
            return redirect(url_for("main.index"))
        except (ValueError, PermissionError) as exc:
            flash(str(exc), "danger")
        except Exception:
            flash("Onbekende fout bij het importeren van het SQL-bestand.", "danger")
    return render_template("import_sql_form.html", form=form)