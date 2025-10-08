import csv
import io
from datetime import datetime
from .models import db, ContextScope, Component, Consequences, AvailabilityRequirements, AIIdentificatie, Summary
from flask_login import current_user
from flask import session
from datetime import datetime, timedelta


def get_session_info():
    """Get session information for display in templates."""
    if 'last_activity' in session:
        last_activity = datetime.fromisoformat(session['last_activity'])
        expires_at = last_activity + timedelta(hours=12)
        time_remaining = expires_at - datetime.now()
        
        return {
            'expires_at': expires_at,
            'time_remaining': time_remaining,
            'expires_soon': time_remaining < timedelta(minutes=30)
        }
    return None

def get_impact_level(impact):
    """Retourneert een numerieke waarde voor impact vergelijking."""
    if not impact:
        return 0
    
    impact_levels = {
        'very low': 1,
        'low': 2,
        'medium': 3,
        'high': 4,
        'very high': 5,
        'insignificant': 1,
        'minor': 2,
        'moderate': 3,
        'major': 4,
        'catastrophic': 5
    }
    return impact_levels.get(impact.lower(), 0)

def get_impact_color(impact_level):
    """
    Retourneert de juiste CSS klasse voor een impact level.
    Consistent met de legenda kleuren.
    """
    if not impact_level:
        return 'impact-unknown'
    
    impact_lower = str(impact_level).lower().strip()
    
    # Very Low / Insignificant
    if impact_lower in ['very low', 'insignificant', '1']:
        return 'bg-green'
    
    # Low / Minor  
    elif impact_lower in ['low', 'minor', '2']:
        return 'bg-yellow'
    
    # Medium / Moderate
    elif impact_lower in ['medium', 'moderate', '3']:
        return 'bg-orange'
    
    # High / Major
    elif impact_lower in ['high', 'major', '4']:
        return 'bg-red'
    
    # Very High / Catastrophic
    elif impact_lower in ['very high', 'catastrophic', '5']:
        return 'bg-dark-red'
    
    # Default voor onbekende waarden
    else:
        return 'impact-unknown'

def get_max_cia_impact(consequences):
    """Berekent de maximale CIA impact uit een lijst van consequences."""
    max_impacts = {
        'Confidentiality': {'worstcase': 'Very Low', 'realistic': 'Very Low'},
        'Integrity': {'worstcase': 'Very Low', 'realistic': 'Very Low'},
        'Availability': {'worstcase': 'Very Low', 'realistic': 'Very Low'}
    }
    
    for consequence in consequences:
        prop = consequence.security_property
        if prop in max_impacts:
            current_worst = consequence.consequence_worstcase or 'Very Low'
            current_realistic = consequence.consequence_realisticcase or 'Very Low'
            
            if get_impact_level(current_worst) > get_impact_level(max_impacts[prop]['worstcase']):
                max_impacts[prop]['worstcase'] = current_worst
            
            if get_impact_level(current_realistic) > get_impact_level(max_impacts[prop]['realistic']):
                max_impacts[prop]['realistic'] = current_realistic
    
    return max_impacts

def get_cia_impact(consequences, security_property, case_type='worstcase'):
    """Haalt de maximale impact op voor een specifieke security property."""
    max_impact = 'Very Low'
    
    for consequence in consequences:
        if consequence.security_property == security_property:
            if case_type == 'worstcase':
                current_impact = consequence.consequence_worstcase or 'Very Low'
            else:
                current_impact = consequence.consequence_realisticcase or 'Very Low'
            
            if get_impact_level(current_impact) > get_impact_level(max_impact):
                max_impact = current_impact
    
    return max_impact

def translate_consequence(value):
    translation = {
        'Medium': 'moderate',
        'High': 'major',
        'Low': 'minor',
        'Huge': 'catastrophic',
        'Insignificant': 'insignificant'
    }
    return translation.get(value, value)

def export_to_csv(item):
    csv_files = {}
    prefix = f"{item.name}_"  # Prefix voor alle CSV-bestandsnamen

    # BIA CSV
    bia_data = io.StringIO()
    bia_writer = csv.writer(bia_data)
    bia_writer.writerow(['BIA Name', 'BIA Responsible', 'BIA Coordinator', 'BIA Start Date', 'BIA End Date', 'BIA Last Update', 'Service Description', 'Knowledge', 'Interfaces', 'mission_critical', 'support_contracts', 'security_supplier', 'user_amount', 'scope_description', 'risk_assessment_human', 'risk_assessment_process', 'risk_assessment_technological', 'ai_model', 'project_leader', 'risk_owner', 'product_owner', 'technical_administrator', 'security_manager', 'incident_contact'])
    bia_writer.writerow([
        item.name, item.responsible, item.coordinator, item.start_date, item.end_date, item.last_update,
        item.service_description, item.knowledge, item.interfaces, item.mission_critical,
        item.support_contracts, item.security_supplier, item.user_amount, item.scope_description,
        item.risk_assessment_human, item.risk_assessment_process, item.risk_assessment_technological,
        item.ai_model, item.project_leader, item.risk_owner, item.product_owner,
        item.technical_administrator, item.security_manager, item.incident_contact
    ])
    csv_files[f'{prefix}bia.csv'] = bia_data.getvalue()

    # Components CSV
    components_data = io.StringIO()
    components_writer = csv.writer(components_data)
    components_writer.writerow(['Component name', 'Type of information', 'Process Dependencies', 'Information Owner', 'Types of users', 'Description of the component', 'Gerelateerd aan BIA'])
    for component in item.components:
        components_writer.writerow([
            component.name, component.info_type, component.process_dependencies, component.info_owner, component.user_type,
            component.description, item.name
        ])
    csv_files[f'{prefix}components.csv'] = components_data.getvalue()

    # Consequences CSV
    consequences_data = io.StringIO()
    consequences_writer = csv.writer(consequences_data)
    consequences_writer.writerow(['Gerelateerd aan Component', 'Category of consequence', 'Property of Security', 'Worstcase consequence', 'Realistic consequence', 'Justification'])
    for component in item.components:
        for consequence in component.consequences:
            consequences_writer.writerow([
                component.name, consequence.consequence_category, consequence.security_property,
                consequence.consequence_worstcase,
                consequence.consequence_realisticcase,
                consequence.justification
            ])
    csv_files[f'{prefix}consequences.csv'] = consequences_data.getvalue()

    # Availability Requirements CSV
    availability_data = io.StringIO()
    availability_writer = csv.writer(availability_data)
    availability_writer.writerow(['Gerelateerd aan Component', 'Maximum Tolerable Downtime', 'Recovery Time Objective', 'Recovery Point Objective', 'Minimum Acceptable Service Level'])
    for component in item.components:
        if component.availability_requirement:
            availability_writer.writerow([
                component.name, component.availability_requirement.mtd,
                component.availability_requirement.rto, component.availability_requirement.rpo,
                component.availability_requirement.masl
            ])
    csv_files[f'{prefix}availability_requirements.csv'] = availability_data.getvalue()

    # AIIdentification CSV
    ai_data = io.StringIO()
    ai_writer = csv.writer(ai_data)
    ai_writer.writerow(['Gerelateerd aan Component', 'AI Category', 'AI Justification'])
    for component in item.components:
        for ai_identification in component.ai_identificaties:
            ai_writer.writerow([
                component.name, ai_identification.category, ai_identification.motivatie
            ])
    csv_files[f'{prefix}ai_identification.csv'] = ai_data.getvalue()

    # Summary CSV
    summary_data = io.StringIO()
    summary_writer = csv.writer(summary_data)
    summary_writer.writerow(['Gerelateerd aan BIA', 'Summary Text'])
    if item.summary:
        summary_writer.writerow([item.name, item.summary.content])
    csv_files[f'{prefix}summary.csv'] = summary_data.getvalue()

    return csv_files

def import_from_csv(csv_files):
    
    # Controleer of het BIA bestand aanwezig is
    if 'bia' not in csv_files or not csv_files['bia']:
        raise ValueError("ContextScope CSV file (BIA) is required.")

    # Maak een mapping van CSV kolomnamen naar model veldnamen
    field_mapping = {
        'BIA Name': 'name',
        'BIA Responsible': 'responsible',
        'BIA Coordinator': 'coordinator',
        'BIA Start Date': 'start_date',
        'BIA End Date': 'end_date',
        'BIA Last Update': 'last_update',
        'Service Description': 'service_description',
        'Knowledge': 'knowledge',
        'Interfaces': 'interfaces',
        'mission_critical': 'mission_critical',
        'support_contracts': 'support_contracts',
        'security_supplier': 'security_supplier',
        'user_amount': 'user_amount',
        'scope_description': 'scope_description',
        'risk_assessment_human': 'risk_assessment_human',
        'risk_assessment_process': 'risk_assessment_process',
        'risk_assessment_technological': 'risk_assessment_technological',
        'project_leader': 'project_leader',
        'risk_owner': 'risk_owner',
        'product_owner': 'product_owner',
        'technical_administrator': 'technical_administrator',
        'security_manager': 'security_manager',
        'incident_contact': 'incident_contact'
    }

    def parse_date(date_string):
        if date_string:
            try:
                return datetime.strptime(date_string, '%Y-%m-%d').date()
            except ValueError:
                return None
        return None

    # Import ContextScope
    context_scope_data = csv.DictReader(io.StringIO(csv_files['bia']))
    for row in context_scope_data:
        # Verwijder de 'id' uit de row data als deze aanwezig is
        row.pop('id', None)
        
        # Maak een nieuwe dictionary met de juiste veldnamen
        mapped_row = {field_mapping.get(k, k): v for k, v in row.items() if k in field_mapping}
        
        # Converteer datumvelden
        mapped_row['start_date'] = parse_date(mapped_row.get('start_date'))
        mapped_row['end_date'] = parse_date(mapped_row.get('end_date'))
        mapped_row['last_update'] = parse_date(mapped_row.get('last_update'))

        # Converteer boolean velden
        for bool_field in ['risk_assessment_human', 'risk_assessment_process', 'risk_assessment_technological', 'ai_model']:
            if bool_field in mapped_row:
                mapped_row[bool_field] = mapped_row[bool_field].lower() in ['true', 'yes', '1']

        # Converteer numerieke velden
        if 'user_amount' in mapped_row and mapped_row['user_amount']:
            try:
                mapped_row['user_amount'] = int(mapped_row['user_amount'])
            except ValueError:
                mapped_row['user_amount'] = None

        # Voeg het gebruikers-ID toe aan de mapped_row
        mapped_row['user_id'] = current_user.id

        context_scope = ContextScope(**mapped_row)
        db.session.add(context_scope)
    
    db.session.flush()
    # Maak een mapping van CSV kolomnamen naar model veldnamen voor Component
    component_field_mapping = {
                'Component name': 'name',
                'Type of information': 'info_type',
                'Information Owner': 'info_owner',
                'Types of users': 'user_type',
                'Description of the component': 'description',
                'Gerelateerd aan BIA': 'context_scope_id',
                'Process Dependencies': 'process_dependencies'  # Voeg deze toe als het een veld is in je Component model
            }

    # Import Components (als aanwezig)
    if 'components' in csv_files and csv_files['components']:
        components_data = csv.DictReader(io.StringIO(csv_files['components']))
        
        components_data = csv.DictReader(io.StringIO(csv_files['components']))
        
        for row in components_data:
            print(f"Processing row: {row}")
            row.pop('id', None)
            
            # Maak een nieuwe dictionary met de juiste veldnamen
            mapped_row = {component_field_mapping.get(k, k): v.strip() if v else None for k, v in row.items() if k in component_field_mapping}
            
            # Haal de BIA naam op en verwijder het uit mapped_row
            bia_name = mapped_row.pop('context_scope_id', None)
            
            print(f"Mapped row: {mapped_row}")
            print(f"BIA name: {bia_name}")
            
            # Controleer of de verplichte velden aanwezig zijn
            if not mapped_row.get('name'):
                print(f"Skipping component without name: {mapped_row}")
                continue
            
            try:
                # Zoek de juiste context_scope op basis van de BIA naam
                related_context_scope = ContextScope.query.filter_by(name=bia_name).first()
                if not related_context_scope:
                    print(f"ContextScope not found for BIA name: {bia_name}")
                    continue

                component = Component(**mapped_row)
                component.context_scope = related_context_scope
                db.session.add(component)
                print(f"Added component to session: {component.name}, linked to BIA: {related_context_scope.name}")
                
                # Probeer de component direct op te halen om te controleren of deze is toegevoegd
                db.session.flush()
                added_component = Component.query.filter_by(name=component.name, context_scope=related_context_scope).first()
                if added_component:
                    print(f"Component successfully added and retrieved: {added_component.name}, linked to BIA: {added_component.context_scope.name}")
                else:
                    print(f"Failed to retrieve added component: {component.name}")
            except Exception as e:
                print(f"Error adding component: {str(e)}")
                db.session.rollback()

        try:
            db.session.commit()
            print("Session committed successfully")
        except Exception as e:
            print(f"Error committing session: {str(e)}")
            db.session.rollback()

        print(f"Total components in database: {Component.query.count()}")

    # Import Consequences (als aanwezig en components geïmporteerd zijn)
    if 'consequences' in csv_files and csv_files['consequences'] and 'components' in csv_files:
        consequences_data = csv.DictReader(io.StringIO(csv_files['consequences']))
        for row in consequences_data:
            if not any(row.values()):  # Skip empty rows
                continue
            
            consequences_field_mapping = {
                'Gerelateerd aan Component': 'component_name',
                'Category of consequence': 'consequence_category',
                'Property of Security': 'security_property',
                'Worstcase consequence': 'consequence_worstcase',
                'Worstcase Justification': 'justification_worstcase',
                'Realistic consequence': 'consequence_realisticcase',
                'Realistic Justification': 'justification_realisticcase'
            }

            mapped_row = {consequences_field_mapping.get(k, k): v for k, v in row.items() if k in consequences_field_mapping}
            component_name = mapped_row.pop('component_name', None)
            
            # Vertaal de consequence waarden
            mapped_row['consequence_worstcase'] = translate_consequence(mapped_row.get('consequence_worstcase'))
            mapped_row['consequence_realisticcase'] = translate_consequence(mapped_row.get('consequence_realisticcase'))
            
            print(f"Processing consequence for component: {component_name}")
            print(f"Mapped row: {mapped_row}")
            
            if component_name:
                component = Component.query.filter_by(name=component_name, context_scope=context_scope).first()
                if component:
                    try:
                        consequence = Consequences(**mapped_row)
                        consequence.component = component
                        db.session.add(consequence)
                        db.session.flush()
                    except Exception as e:
                        print(f"Error adding consequence for component {component_name}: {str(e)}")
                        db.session.rollback()
                else:
                    print(f"Component not found: {component_name}")
            else:
                print("Skipping consequence without component name")

        db.session.commit()
    # Import Availability Requirements
    if 'availability_requirements' in csv_files and csv_files['availability_requirements'] and 'components' in csv_files:
        availability_data = csv.DictReader(io.StringIO(csv_files['availability_requirements']))
        for row in availability_data:
            availability_field_mapping = {
                'Gerelateerd aan Component': 'component_name',
                'Maximum Tolerable Downtime': 'mtd',
                'Recovery Time Objective': 'rto',
                'Recovery Point Objective': 'rpo',
                'Minimum Acceptable Service Level': 'masl'
            }

            mapped_row = {availability_field_mapping.get(k, k): v.strip() if v else None for k, v in row.items() if k in availability_field_mapping}
            component_name = mapped_row.pop('component_name', None)
            
            if component_name:
                component = Component.query.filter_by(name=component_name).first()
                if component:
                    # Verwijder bestaande availability requirement als die er is
                    if component.availability_requirement:
                        db.session.delete(component.availability_requirement)
                    
                    # Maak een nieuwe availability requirement
                    availability = AvailabilityRequirements(**mapped_row)
                    availability.component = component
                    db.session.add(availability)
                    print(f"Added availability requirement for component: {component_name}")
                else:
                    print(f"Component not found: {component_name}")
            else:
                print("Skipping availability requirement without component name")

        try:
            db.session.commit()
            print("Availability requirements committed successfully")
        except Exception as e:
            print(f"Error committing availability requirements: {str(e)}")
            db.session.rollback()

    # Import AIIdentification (als aanwezig en components geïmporteerd zijn)
    if 'ai_identification' in csv_files and csv_files['ai_identification'] and 'components' in csv_files:
        ai_data = csv.DictReader(io.StringIO(csv_files['ai_identification']))
        for row in ai_data:
            ai_field_mapping = {
                'Gerelateerd aan Component': 'component_name',
                'AI Category': 'category',
                'AI Justification': 'motivatie'
            }

            mapped_row = {ai_field_mapping.get(k, k): v for k, v in row.items() if k in ai_field_mapping}
            component_name = mapped_row.pop('component_name', None)
            
            if component_name:
                component = Component.query.filter_by(name=component_name).first()
                if component:
                    # Verwijder bestaande AI-identificatie als die er is
                    existing_ai = AIIdentificatie.query.filter_by(component_id=component.id).first()
                    if existing_ai:
                        db.session.delete(existing_ai)
                    
                    # Maak een nieuwe AI-identificatie
                    ai_identification = AIIdentificatie(**mapped_row)
                    ai_identification.component = component
                    db.session.add(ai_identification)
                    print(f"Added AI identification for component: {component_name}")
                else:
                    print(f"Component not found: {component_name}")
            else:
                print("Skipping AI identification without component name")

        try:
            db.session.commit()
            print("AI identifications committed successfully")
        except Exception as e:
            print(f"Error committing AI identifications: {str(e)}")
            db.session.rollback()
    # Import Summary (als aanwezig)
    if 'summary' in csv_files and csv_files['summary']:
        summary_data = csv.DictReader(io.StringIO(csv_files['summary']))
        
        summary_field_mapping = {
            'Gerelateerd aan BIA': 'bia_name',
            'Summary Text': 'content'
        }
        
        for row in summary_data:
            if not any(row.values()):  # Skip empty rows
                continue
            
            # Map the row data
            mapped_row = {summary_field_mapping.get(k, k): v.strip() if v else None for k, v in row.items() if k in summary_field_mapping}
            
            # Get the BIA name and remove it from mapped_row
            bia_name = mapped_row.pop('bia_name', None)
            
            print(f"Processing summary for BIA: {bia_name}")
            print(f"Summary content: {mapped_row.get('content', '')[:100]}...")  # Show first 100 chars
            
            if bia_name and mapped_row.get('content'):
                # Find the related context_scope based on BIA name
                related_context_scope = ContextScope.query.filter_by(name=bia_name).first()
                if related_context_scope:
                    try:
                        # Check if summary already exists for this BIA
                        existing_summary = Summary.query.filter_by(context_scope_id=related_context_scope.id).first()
                        if existing_summary:
                            # Update existing summary
                            existing_summary.content = mapped_row['content']
                            print(f"Updated existing summary for BIA: {bia_name}")
                        else:
                            # Create new summary
                            summary = Summary(
                                content=mapped_row['content'],
                                context_scope_id=related_context_scope.id
                            )
                            db.session.add(summary)
                            print(f"Added new summary for BIA: {bia_name}")
                        
                        db.session.flush()
                    except Exception as e:
                        print(f"Error adding/updating summary for BIA {bia_name}: {str(e)}")
                        db.session.rollback()
                else:
                    print(f"ContextScope not found for BIA name: {bia_name}")
            else:
                print(f"Skipping summary - missing BIA name or content")

    try:
        db.session.commit()
        print("All data committed successfully")
    except Exception as e:
        print(f"Error committing session: {str(e)}")
        db.session.rollback()
        raise