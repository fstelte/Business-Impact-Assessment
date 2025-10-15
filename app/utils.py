import csv
import io
import logging
import re
from datetime import datetime
from .models import db, ContextScope, Component, Consequences, AvailabilityRequirements, AIIdentificatie, Summary
from flask_login import current_user
from flask import session
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SubmitField
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


MAX_SQL_FILE_SIZE = 2 * 1024 * 1024

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
    
    consequences_writer.writerow([
        'Gerelateerd aan Component',
        'Category of consequence',
        'Property of Security',
        'Worstcase consequence',
        'Justification for worst consequence',
        'Realistic consequence',
        'Justification for realistic consequence'
    ])

    for component in item.components:
        for consequence in component.consequences:
            consequences_writer.writerow([
                
                component.name,
                consequence.consequence_category,
                consequence.security_property,
                consequence.consequence_worstcase,
                consequence.justification_worstcase,
                consequence.consequence_realisticcase,
                consequence.justification_realisticcase
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
                'Category of consequence': 'consequence_category',
                'Property of Security': 'security_property',
                'Worstcase consequence': 'consequence_worstcase',
                'Justification for worst consequence': 'justification_worstcase',
                'Realistic consequence': 'consequence_realisticcase',
                'Justification for realistic consequence': 'justification_realisticcase',
            }


            mapped_row = {consequences_field_mapping.get(k, k): v for k, v in row.items() if k in consequences_field_mapping}
            component_name = row.get('Gerelateerd aan Component')
            
            # Vertaal de consequence waarden
            mapped_row['consequence_worstcase'] = translate_consequence(mapped_row.get('consequence_worstcase'))
            mapped_row['consequence_realisticcase'] = translate_consequence(mapped_row.get('consequence_realisticcase'))
            
            print(f"Processing consequence for component: {component_name}")
            print(f"Mapped row: {mapped_row}")
            
            if component_name:
                # Zoek de component die bij de huidige context_scope hoort
                component = Component.query.filter_by(name=component_name, context_scope_id=context_scope.id).first()
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
                    print(f"Component not found: {component_name} for context_scope_id: {context_scope.id}")
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

class SQLImportForm(FlaskForm):
    sql_file = FileField(
        'SQL-bestand',
        validators=[
            FileRequired(message='Kies een SQL-bestand.'),
            FileAllowed(['sql'], 'Alleen .sql-bestanden zijn toegestaan.')
        ]
    )
    submit = SubmitField('Importeren')

def escape_sql_string(value):
    """Escapes a string for use in an SQL statement."""
    if value is None:
        return "NULL"
    # Replace single quote with two single quotes for SQL compatibility
    return "'" + str(value).replace("'", "''") + "'"

def export_to_sql(item):
    """Exports a BIA item and its related data to SQL INSERT statements."""
    from .models import Component, Consequences, AvailabilityRequirements, AIIdentificatie, Summary
    sql_statements = []

    # Helper to generate INSERT statement
    def generate_insert(table_name, data):
        # Filter out None values, as they should be represented as NULL in SQL
        filtered_data = {k: v for k, v in data.items() if v is not None}
        columns = ', '.join(filtered_data.keys())
        values = ', '.join(map(str, filtered_data.values()))
        return f"INSERT INTO {table_name} ({columns}) VALUES ({values});"

    # Helper to escape strings and handle None
    def escape_sql_string(value):
        if value is None:
            return "NULL"
        return f"'{str(value).replace("'", "''")}'"
        
    def escape_sql_date(value):
        if value is None:
            return "NULL"
        return f"'{value.strftime('%Y-%m-%d')}'"
    # 1. ContextScope
    bia_data = {
        'id': item.id,
        'name': escape_sql_string(item.name),
        'responsible': escape_sql_string(item.responsible),
        'coordinator': escape_sql_string(item.coordinator),
        'start_date': escape_sql_date(item.start_date),
        'end_date': escape_sql_date(item.end_date),
        'last_update': escape_sql_date(item.last_update),
        'service_description': escape_sql_string(item.service_description),
        'knowledge': escape_sql_string(item.knowledge),
        'interfaces': escape_sql_string(item.interfaces),
        'mission_critical': escape_sql_string(item.mission_critical),
        'support_contracts': escape_sql_string(item.support_contracts),
        'security_supplier': escape_sql_string(item.security_supplier),
        'user_amount': item.user_amount,
        'scope_description': escape_sql_string(item.scope_description),
        'risk_assessment_human': 1 if item.risk_assessment_human else 0,
        'risk_assessment_process': 1 if item.risk_assessment_process else 0,
        'risk_assessment_technological': 1 if item.risk_assessment_technological else 0,
        'ai_model': 1 if item.ai_model else 0,
        'project_leader': escape_sql_string(item.project_leader),
        'risk_owner': escape_sql_string(item.risk_owner),
        'product_owner': escape_sql_string(item.product_owner),
        'technical_administrator': escape_sql_string(item.technical_administrator),
        'security_manager': escape_sql_string(item.security_manager),
        'incident_contact': escape_sql_string(item.incident_contact),
        'user_id': item.user_id
    }
    sql_statements.append(generate_insert('context_scope', bia_data))

    # 2. Components
    for component in item.components:
        comp_data = {
            'id': component.id,
            'name': escape_sql_string(component.name),
            'info_type': escape_sql_string(component.info_type),
            'info_owner': escape_sql_string(component.info_owner),
            'user_type': escape_sql_string(component.user_type),
            'process_dependencies': escape_sql_string(component.process_dependencies),
            'description': escape_sql_string(component.description),
            'context_scope_id': component.context_scope_id
        }
        sql_statements.append(generate_insert('component', comp_data))

        for consequence in component.consequences:
            cons_data = {
                'id': consequence.id,
                'security_property': escape_sql_string(consequence.security_property),
                'consequence_category': escape_sql_string(consequence.consequence_category),
                'consequence_worstcase': escape_sql_string(consequence.consequence_worstcase),
                'justification_worstcase': escape_sql_string(consequence.justification_worstcase),
                'consequence_realisticcase': escape_sql_string(consequence.consequence_realisticcase),
                'justification_realisticcase': escape_sql_string(consequence.justification_realisticcase),
                'component_id': consequence.component_id
            }
            sql_statements.append(generate_insert('consequences', cons_data))

        availability = component.availability_requirement
        if availability:
            ar_data = {
                'id': availability.id,
                'mtd': escape_sql_string(availability.mtd),
                'rto': escape_sql_string(availability.rto),
                'rpo': escape_sql_string(availability.rpo),
                'masl': escape_sql_string(availability.masl),
                'component_id': availability.component_id
            }
            sql_statements.append(generate_insert('availability_requirements', ar_data))

        for ai_identification in component.ai_identificaties:
            ai_data = {
                'id': ai_identification.id,
                'category': escape_sql_string(ai_identification.category),
                'motivatie': escape_sql_string(ai_identification.motivatie),
                'component_id': ai_identification.component_id
            }
            sql_statements.append(generate_insert('ai_identificatie', ai_data))

    # 6. Summary
    summary = item.summary
    if summary:
        summary_data = {
            'id': summary.id,
            'content': escape_sql_string(summary.content),
            'context_scope_id': summary.context_scope_id
        }
        sql_statements.append(generate_insert('summary', summary_data))
    return "\n".join(sql_statements)



def import_from_sql(sql_content):
    if not current_user.is_authenticated:
        raise PermissionError("Authenticatie vereist.")
    if not sql_content or not sql_content.strip():
        raise ValueError("Geen SQL-inhoud ontvangen.")
    allowed_tables = {
        'context_scope',
        'component',
        'consequences',
        'availability_requirements',
        'ai_identificatie',
        'summary'
    }
    expected_columns = {
        'context_scope': {
            'id', 'name', 'responsible', 'coordinator', 'start_date', 'end_date', 'last_update',
            'service_description', 'knowledge', 'interfaces', 'mission_critical', 'support_contracts',
            'security_supplier', 'user_amount', 'scope_description', 'risk_assessment_human',
            'risk_assessment_process', 'risk_assessment_technological', 'ai_model', 'project_leader',
            'risk_owner', 'product_owner', 'technical_administrator', 'security_manager',
            'incident_contact', 'user_id'
        },
        'component': {
            'id', 'name', 'info_type', 'info_owner', 'user_type', 'process_dependencies',
            'description', 'context_scope_id'
        },
        'consequences': {
            'id', 'consequence_category', 'security_property', 'consequence_worstcase',
            'justification_worstcase', 'consequence_realisticcase', 'justification_realisticcase',
            'component_id'
        },
        'availability_requirements': {
            'id', 'mtd', 'rto', 'rpo', 'masl', 'component_id'
        },
        'ai_identificatie': {
            'id', 'category', 'motivatie', 'component_id'
        },
        'summary': {
            'id', 'content', 'context_scope_id'
        }
    }
    insert_regex = re.compile(
        r"^INSERT\s+INTO\s+(?P<table>[a-z_]+)\s*\((?P<columns>[^)]+)\)\s+VALUES\s*\((?P<values>.*)\)\s*;$",
        re.IGNORECASE | re.DOTALL
    )

    def split_statements(sql_text):
        statements, current, in_string, i = [], [], False, 0
        while i < len(sql_text):
            ch = sql_text[i]
            current.append(ch)
            if ch == "'":
                if i + 1 < len(sql_text) and sql_text[i + 1] == "'":
                    current.append("'")
                    i += 1
                else:
                    in_string = not in_string
            elif ch == ';' and not in_string:
                statement = ''.join(current).strip()
                if statement:
                    statements.append(statement)
                current = []
            i += 1
        if ''.join(current).strip():
            raise ValueError("SQL-bestand bevat een onvolledig statement.")
        return statements

    def split_values(values_str):
        values, current, in_string, i = [], [], False, 0
        while i < len(values_str):
            ch = values_str[i]
            if ch == "'" and not in_string:
                in_string = True
                current.append(ch)
            elif ch == "'" and in_string:
                current.append(ch)
                if i + 1 < len(values_str) and values_str[i + 1] == "'":
                    current.append("'")
                    i += 1
                else:
                    in_string = False
            elif ch == ',' and not in_string:
                values.append(''.join(current).strip())
                current = []
            else:
                current.append(ch)
            i += 1
        if current:
            values.append(''.join(current).strip())
        return values

    def convert_value(token):
        cleaned = token.strip()
        if cleaned.upper() == 'NULL':
            return None
        if cleaned.startswith("'") and cleaned.endswith("'"):
            return cleaned[1:-1].replace("''", "'")
        if re.fullmatch(r'-?\d+', cleaned):
            return int(cleaned)
        if re.fullmatch(r'-?\d+\.\d+', cleaned):
            return float(cleaned)
        return cleaned

    def parse_statement(statement):
        match = insert_regex.match(statement)
        if not match:
            raise ValueError("Ongeldig SQL statement gedetecteerd.")
        table = match.group('table').lower()
        if table not in allowed_tables:
            raise ValueError("Niet-toegestane tabel aangetroffen.")
        columns = [col.strip() for col in match.group('columns').split(',')]
        if not all(re.fullmatch(r'[a-z_]+', col) for col in columns):
            raise ValueError("Ongeldige kolomnaam aangetroffen.")
        values = split_values(match.group('values').strip())
        if len(columns) != len(values):
            raise ValueError("Aantal kolommen komt niet overeen met aantal waarden.")
        if not set(columns).issubset(expected_columns[table]):
            raise ValueError("Niet-toegestane kolommen voor tabel aangetroffen.")
        return table, columns, [convert_value(value) for value in values]

    statements = split_statements(sql_content)
    if not statements:
        raise ValueError("Geen SQL-statements gevonden.")

    parsed_data = {table: [] for table in allowed_tables}
    for statement in statements:
        table, columns, values = parse_statement(statement)
        parsed_data[table].append(dict(zip(columns, values)))

    if not parsed_data['context_scope']:
        raise ValueError("Geen context_scope records gevonden in het SQL-bestand.")

    def to_bool(value):
        if isinstance(value, bool):
            return value
        if value in (None, '', 'None'):
            return False
        if isinstance(value, (int, float)):
            return bool(value)
        return str(value).strip().lower() in {'true', '1', 'yes', 'y', 'on'}

    def parse_date_field(value):
        if not value or str(value).strip().lower() == 'none':
            return None
        if isinstance(value, datetime):
            return value.date()
        return datetime.strptime(str(value), '%Y-%m-%d').date()

    def prepare_context(row):
        prepared = {k: v for k, v in row.items() if k not in {'id', 'user_id'}}
        prepared['user_id'] = current_user.id
        for field in ('start_date', 'end_date', 'last_update'):
            prepared[field] = parse_date_field(prepared.get(field))
        for field in ('risk_assessment_human', 'risk_assessment_process', 'risk_assessment_technological', 'ai_model'):
            prepared[field] = to_bool(prepared.get(field))
        numeric = prepared.get('user_amount')
        if numeric in (None, '', 'None'):
            prepared['user_amount'] = None
        else:
            try:
                prepared['user_amount'] = int(numeric)
            except (TypeError, ValueError):
                prepared['user_amount'] = None
        return prepared

    def prepare_component(row, context_map):
        prepared = {k: v for k, v in row.items() if k != 'id'}
        original_id = prepared.get('context_scope_id')
        if isinstance(original_id, str) and original_id.isdigit():
            original_id = int(original_id)
        if original_id not in context_map:
            raise ValueError("Component verwijst naar onbekende context_scope.")
        prepared['context_scope_id'] = context_map[original_id]
        return prepared

    def prepare_child(row, key_map, foreign_key):
        prepared = {k: v for k, v in row.items() if k != 'id'}
        original_fk = prepared.get(foreign_key)
        if isinstance(original_fk, str) and original_fk.isdigit():
            original_fk = int(original_fk)
        if original_fk not in key_map:
            raise ValueError(f"Record verwijst naar onbekende {foreign_key}.")
        prepared[foreign_key] = key_map[original_fk]
        return prepared

    scope_names = {row.get('name') for row in parsed_data['context_scope'] if row.get('name')}
    if not scope_names:
        raise ValueError("Geen geldige BIA-namen gevonden in het SQL-bestand.")

    context_map, component_map = {}, {}
    try:
        with db.session.begin_nested():
            for name in scope_names:
                for scope in ContextScope.query.filter_by(name=name).all():
                    db.session.delete(scope)
            db.session.flush()

            for row in parsed_data['context_scope']:
                original_id = row.get('id')
                context = ContextScope(**prepare_context(row))
                db.session.add(context)
                db.session.flush()
                if original_id is not None:
                    context_map[original_id] = context.id

            for row in parsed_data['component']:
                original_id = row.get('id')
                component = Component(**prepare_component(row, context_map))
                db.session.add(component)
                db.session.flush()
                if original_id is not None:
                    component_map[original_id] = component.id

            for row in parsed_data['consequences']:
                db.session.add(Consequences(**prepare_child(row, component_map, 'component_id')))

            for row in parsed_data['availability_requirements']:
                db.session.add(AvailabilityRequirements(**prepare_child(row, component_map, 'component_id')))

            for row in parsed_data['ai_identificatie']:
                ai_row = prepare_child(row, component_map, 'component_id')
                if not ai_row.get('category'):
                    ai_row['category'] = 'No AI'
                db.session.add(AIIdentificatie(**ai_row))

            for row in parsed_data['summary']:
                db.session.add(Summary(**prepare_child(row, context_map, 'context_scope_id')))
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        logging.exception("SQL import failed")
        cause = exc.__cause__ if exc.__cause__ else exc
        raise ValueError(f"Import van SQL-bestand is mislukt: {cause}") from exc

def import_sql_file(file_storage):
    if not current_user.is_authenticated:
        raise PermissionError("Authenticatie vereist.")
    if not file_storage or not file_storage.filename:
        raise ValueError("Geen bestand opgegeven.")
    filename = secure_filename(file_storage.filename)
    if not filename.lower().endswith('.sql'):
        raise ValueError("Alleen .sql-bestanden zijn toegestaan.")
    stream = file_storage.stream
    stream.seek(0, io.SEEK_END)
    if stream.tell() > MAX_SQL_FILE_SIZE:
        raise ValueError("SQL-bestand overschrijdt de maximale grootte.")
    stream.seek(0)
    content = stream.read()
    if not content:
        raise ValueError("Het SQL-bestand is leeg.")
    try:
        sql_text = content.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise ValueError("SQL-bestand moet UTF-8 gecodeerd zijn.") from exc
    import_from_sql(sql_text)