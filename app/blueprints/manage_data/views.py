# views.py

from flask import Flask, Blueprint, current_app, g, session, request, url_for, redirect, \
    render_template, flash, abort

from app.services import app_db
from app.model import Context_Scope, Components, Availability_Requirements, References, Consequences,  ConsequenceChoices, SecurityProperties
from .forms import (
    BIANewForm, BIAEditForm, BIADeleteForm, CompNewForm, CompEditForm, CompDeleteForm,
    ReferenceNewForm, ReferenceEditForm, ReferenceDeleteForm,
    ConsequenceNewForm, ConsequenceEditForm, ConsequenceDeleteForm,
    AvailabilityNewForm, AvailabilityEditForm, AvailabilityDeleteForm
)


manage_data_blueprint = Blueprint('manage_data', __name__)

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
            'col_title': 'Delete'
        },
        {
            'col_title': 'Add Component'
        },
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
                'col_value': bia.responsible
            },
            {
                'col_value': 'delete',
                'url': url_for('manage_data.bia_delete', bia_id=bia.id),
            },
            { 
                'col_value': 'Add Component',
                'url': url_for('manage_data.component_new', bia_id=bia.id)
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
# Components
@manage_data_blueprint.route('/component/list', methods=['GET', 'POST'])
def component_list():
    components = app_db.session.query(Components).order_by(Components.component_name).all()
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
    for component in components:

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
                'col_value': component.bia_name
            },
            {
                'col_value': component.description
                
            },
            {
                'col_value': component.info_type
            },
            {
                'col_value': 'delete',
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

    if form.validate_on_submit():
        item = Components()
        form.populate_obj(item)
        item.bia_name = form.name.data.name
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

    return render_template('item_new_edit.html', title='New BIA', form=form)

@manage_data_blueprint.route('/component/edit/<int:component_id>', methods=['GET', 'POST'])
def component_edit(component_id):

   
    item = app_db.session.query(Components).filter(Components.id == component_id).first()
    form = CompEditForm(obj=item)
    form.name.query = app_db.session.query(Context_Scope).order_by(Context_Scope.id)
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

    return render_template('item_delete.html', title='Delete BIA', item_name=item_name, form=form)

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
                'col_value': 'delete',
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
            'col_title': 'Category',
        },
       {
            'col_title': 'Security Property',
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
                'col_value': consequence.category,
            },
            {
                'col_value': consequence.security_property,
            },
            {
                'col_value': consequence.consequence_realisticcase,
            },
            {
                'col_value': 'delete',
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
    #name = app_db.session.query(Components).order_by(Components.id).all()
    form = ConsequenceNewForm()

    if form.validate_on_submit():
        #form.populate_obj(item)
        # Map form fields to object attributes
        item.component_name = form.component_name.data.component_name
        item.category = form.category.data.consequence_category
        item.security_property = form.security_property.data.choice
        item.consequence_worstcase = form.consequence_worstcase.data.choice
        item.justification_worstcase = form.justification_worstcase.data
        item.consequence_realisticcase = form.consequence_realisticcase.data.choice
        item.justification_realisticcase = form.justification_realisticcase.data
        #item.component_name = form.name.data.name
        app_db.session.add(item)
        app_db.session.commit()
        flash('Consequence added: ' + item.category, 'info')
        return redirect(url_for('manage_data.consequence_list'))

    return render_template('item_new_edit.html', title='New Consequence', form=form)

@manage_data_blueprint.route('/consequence/edit/<int:consequence_id>', methods=['GET', 'POST'])
def consequence_edit(consequence_id):

    item = app_db.session.query(Consequences).filter(Consequences.id == consequence_id).first()
    if item is None:
        abort(403)

    form = ConsequenceEditForm(obj=item)

    if form.validate_on_submit():
        form.populate_obj(item)
        app_db.session.commit()
        flash('Consequences updated: ' + item.consequence_category, 'info')
        return redirect(url_for('manage_data.consequence_list'))

    return render_template('item_new_edit.html', title='Edit Consequence', form=form)



@manage_data_blueprint.route('/consequence/delete/<int:consequence_id>', methods=['GET', 'POST'])
def consequence_delete(consequence_id):

    item = app_db.session.query(Consequences).filter(Consequences.id == consequence_id).first()
    if item is None:
        abort(403)

    form = ConsequenceDeleteForm(obj=item)

    item_name = item.consequence_category
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
                'col_value': 'delete',
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

    if form.validate_on_submit():
        form.populate_obj(item)
        item.component_name = form.component_name.data.component_name
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

    if form.validate_on_submit():
        form.populate_obj(item)
        app_db.session.commit()
        flash('Availability requirements updated: ' + item.id, 'info')
        return redirect(url_for('manage_data.availability_list'))

    return render_template('item_new_edit.html', title='Edit Availability requirement', form=form)

@manage_data_blueprint.route('/availability/delete/<int:availability_id>', methods=['GET', 'POST'])
def availability_delete(availability_id):

    item = app_db.session.query(Availability_Requirements).filter(Availability_Requirements.id == availability_id).first()
    if item is None:
        abort(403)

    form = AvailabilityDeleteForm(obj=item)

    item_name = item.id
    if form.validate_on_submit():
        app_db.session.delete(item)
        app_db.session.commit()
        flash('Deleted availability requirement: ' + item_name, 'info')
        return redirect(url_for('manage_data.availability_list'))

    return render_template('item_delete.html', title='Delete availability requirement', item_name=item_name, form=form)
