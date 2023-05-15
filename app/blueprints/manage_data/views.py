# views.py

from flask import Flask, Blueprint, current_app, g, session, request, url_for, redirect, \
    render_template, flash, abort

from app.services import app_db
from app.model import Context_Scope, Components, Availability_Requirements, References
from .forms import (
    BIANewForm, BIAEditForm, BIADeleteForm, CompNewForm, CompEditForm, CompDeleteForm
    
)


manage_data_blueprint = Blueprint('manage_data', __name__)


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
                'col_value': bia.responsible
            },
            {
                'col_value': 'delete',
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
