from unittest import result
from odoo import http, _, fields
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
import json
from werkzeug.exceptions import NotFound
from odoo.tools.translate import _
from collections import OrderedDict
from datetime import date, datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from odoo.exceptions import ValidationError


STATES_DICT = {
    'draft': 'Draft',
    'planning': 'Planning',
    'performance_period': 'Performance Period',
    'assessment': 'Assessment',
    'final_comments': 'Final Comments',
    'done': 'Done',
    'cancel': 'Cancel'
}
CETERIA_DICT = {
    'met': 'Met',
    'not_met': 'Not Met',
    'partially_met': 'Partially Met'
}
STATES = [
    'draft',
    'planning',
    'performance_period',
    'assessment',
    'final_comments',
    'done',
    'cancel'
]

APPRAISAL_TYPES = {
    'probation_appraisal': 'Probation Appraisal',
    'general_appraisal': 'Performance Appraisal'
}
def _get_date_as_utc(date):
    date = date.strftime("%Y-%m-%d %H:%M:%S")
    mytz = pytz.timezone(request._context.get('tz') or request.env.user.tz)
    display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(
        str(date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(mytz), "%Y-%m-%d %H:%M:%S")
    return datetime.strptime(display_date_result, "%Y-%m-%d %H:%M:%S")

class WebsiteAppraisalPIP(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(WebsiteAppraisalPIP, self)._prepare_portal_layout_values()
        show_subordinates_appraisals_pip = False
        subordinates_appraisals_pip_count = 0
        show_my_appraisals_pip = False
        my_appraisals_pip_count = 0
        if request.env.user.employee_id:
            request._cr.execute("""
                SELECT 
                    count(pip.id)
                FROM
                    appraisal_pip as pip
                    INNER JOIN hr_employee AS employee ON employee.id = pip.employee_id
                    INNER JOIN hr_employee AS manager ON  manager.id = employee.parent_id
                WHERE
                    pip.active = 't'
                AND
                    employee.active = 't'
                AND
                   manager.active = 't'
                AND
                    pip.state NOT IN ('draft', 'cancel')
                AND
                    (manager.id = %s)
            """, (request.env.user.employee_id.id,))
            pip_appraisals = request._cr.dictfetchone()
            if pip_appraisals.get('count', 0) > 0:
                show_subordinates_appraisals_pip = True
                subordinates_appraisals_pip_count = pip_appraisals.get('count', 0)
            # My pip appraisals
            request._cr.execute("""
                SELECT 
                    count(pip.id)
                FROM
                    appraisal_pip as pip
                    INNER JOIN hr_employee AS employee ON employee.id = pip.employee_id
                WHERE
                    pip.active = 't'
                AND
                    employee.active = 't'
                AND
                    pip.state NOT IN ('draft', 'cancel')
                AND
                    (employee.id = %s)
            """, (request.env.user.employee_id.id,))
            pip_appraisals = request._cr.dictfetchone()
            if pip_appraisals.get('count', 0) > 0:
                show_my_appraisals_pip = True
                my_appraisals_pip_count = pip_appraisals.get('count', 0)
        
        values.update({
            'show_subordinates_appraisals_pip': show_subordinates_appraisals_pip,
            'subordinates_appraisals_pip_count': subordinates_appraisals_pip_count,
            'show_my_appraisals_pip': show_my_appraisals_pip,
            'my_appraisals_pip_count': my_appraisals_pip_count
            })
        return values

class AppraisalControllerPIP(http.Controller):
    """ This Class handles CRUD operations of appraisal by manger for employee for pip. """
    _items_per_page = 20

    def query_appraisals_data(self, limit='', offset='', order='', domain='', view_type='list_view', **kw):
        data = {}
        fields = ""
        joins = ""
        group_by = ""
        limit_and_offset_order = ""
        if request.env.user.employee_id:
            employee = request.env.user.employee_id
            by_managers = True if kw.get('query_type', 'by_manager') == 'by_manager' else False
            if by_managers:
                joins += """ INNER JOIN hr_employee AS manager ON  manager.id = employee.parent_id """
                domain += """ AND (manager.id = %s)"""% (employee.id)
            else:
                joins += """ LEFT JOIN hr_employee AS manager ON  manager.id = employee.parent_id """
                domain += """ AND pip.employee_id = %s """% (employee.id,)
                
            if view_type == "list_view":
                limit_and_offset_order = """
                    ORDER BY %s
                    LIMIT %s
                    OFFSET %s
                """% (order, limit, offset)
            else:
                appraisal_pip_id = kw.get('appraisal_pip_id', False)
                if appraisal_pip_id: 
                    domain += """ AND pip.id = %s """% (appraisal_pip_id)
                joins += """ 
                    LEFT JOIN appraisal_pip_hr_employee_rel AS other_attendees ON other_attendees.appraisal_pip_id = pip.id
                    LEFT JOIN hr_employee AS other_employee ON other_employee.id = other_attendees.hr_employee_id """
                fields += """, ARRAY_AGG (other_employee.name) other_attendees_names  """
                group_by = """
                    GROUP BY 
                        pip.id,
                        employee.id,
                        job.name,
                        unit.name,
                        office.name,
                        department.name,
                        manager.name,
                        second_manager_name,
                        m_job.name"""
            
            request._cr.execute("""
                SELECT 
                    pip.id,
                    pip.state,
                    pip.initial_meeting_date,
                    pip.appraisal_type,
                    employee.id as emp_id,
                    employee.name as employee_name,
                    employee.idc_no as employee_idc_no,
                    job.name as position,
                    unit.name as unit_name,
                    office.name as office,
                    department.name as department_name,
                    manager.name as manager_name, 
                    second_manager.name as second_manager_name,
                    m_job.name as manager_job,
                    pip.manager_sign_date,
                    pip.employee_sign_date
                    %s

                FROM
                    appraisal_pip as pip
                    INNER JOIN hr_employee AS employee ON employee.id = pip.employee_id
                    LEFT JOIN office AS office ON employee.office_id = office.id
                    LEFT JOIN hr_job AS job ON employee.job_id = job.id
                    LEFT JOIN hr_unit as unit ON employee.unit_id = unit.id
                    LEFT JOIN hr_department as department ON employee.department_id = department.id
                    %s
                    LEFT JOIN hr_job AS m_job ON manager.job_id = m_job.id
                    LEFT JOIN hr_employee AS second_manager ON  second_manager.id = employee.second_manager_id
                WHERE
                    pip.active = 't'
                AND
                    employee.active = 't'
                AND
                    manager.active = 't'
                AND
                    pip.state NOT IN ('draft', 'cancel')
                %s
                %s
                %s
            """% (fields, joins, domain, group_by, limit_and_offset_order))
            if view_type == 'list_view':
                pip_appraisals = request._cr.dictfetchall()
                data = pip_appraisals if pip_appraisals else False
            else:
                pip_appraisal = request._cr.dictfetchone()
                if pip_appraisal:
                    state = pip_appraisal.get('state', '')
                    meta_info =  {
                        'byManager': by_managers,
                        'hasCurrentComponentAccess': True,
                        'hasCurrentComponentAccessMessage': '',
                        'setSubmitAccess': True,
                        'setting_pip_objective_state': False,
                        'setting_pip_review_state': False,
                        'setting_pip_review_assessment_state': False,
                        'next_stage': STATES[STATES.index(state)+1] if STATES.index(state) and STATES.index(state)+1  < len(STATES) else '',
                        }
                    
              
                    if by_managers:
                        if state not in  ['planning', 'assessment']:
                            meta_info['hasCurrentComponentAccess'] = False
                            meta_info['setSubmitAccess'] = False
                            meta_info['hasCurrentComponentAccessMessage'] = "Not editable at this stage"
                    else:
                        if state not in  ['final_comments']:
                            meta_info['hasCurrentComponentAccess'] = False
                            meta_info['setSubmitAccess'] = False
                            meta_info['hasCurrentComponentAccessMessage'] = "Not editable at this stage"

                    if state == 'done':
                        meta_info['hasCurrentComponentAccess'] = False
                        meta_info['setSubmitAccess'] = False
                        meta_info['hasCurrentComponentAccessMessage'] = "The record is finalized and is readonly."

                    
                    pip_appraisal.update({'metaInfo': meta_info})

                    # Objective ids
                    request._cr.execute("""
                        SELECT 
                            id,
                            name,
                            performance_concern,
                            agreed_improvement_action,
                            support
                        FROM
                            appraisal_pip_target
                        WHERE
                            appraisal_pip_id = %s
                        ORDER BY
                            id asc
                    """, (appraisal_pip_id,))
                    objectives = request._cr.dictfetchall()
                    pip_appraisal.update({'objectives': objectives})
                    meta_info.update({"setting_pip_objective_state": objectives and True or False})
                    # Reviews ids
                    request._cr.execute("""
                        SELECT 
                            id,
                            review_date,
                            notes,
                            result,
                            finalized
                        FROM
                            appraisal_pip_review
                        WHERE
                            appraisal_pip_id = %s
                        ORDER BY
                            id asc
                    """, (appraisal_pip_id,))
                    reviews = request._cr.dictfetchall()
                    for review in reviews:
                        if review.get('review_date') and review.get('notes') and review.get('result'):
                            review.update({'finalized': True})
                        else:
                            review.update({'finalized': False})
                    missing_reviews_data = list(filter( lambda x: (not x.get('notes') or not x.get('result')), reviews))
                    pip_appraisal.update({'reviews': reviews})
                    meta_info.update({"setting_pip_review_state": reviews and True or False})
                    meta_info.update({"setting_pip_review_assessment_state": len(missing_reviews_data) == 0 and True or False})
                    data = pip_appraisal
                    data.update({"creteria_dict": CETERIA_DICT})

        return data

    def get_appraisals_count(self, domain='', **kw):
        count = 0
        if request.env.user.employee_id:
            employee = request.env.user.employee_id
            by_managers = True if kw.get('query_type', 'by_manager') == 'by_manager' else False
            by_employees = not by_managers
            joins = ""
            if by_managers:
                joins += """ INNER JOIN hr_employee AS manager ON  manager.id = employee.parent_id  """
                domain += """ AND manager.active = 't' AND manager.id = %s """% (employee.id, )
            else:
                domain += """  AND employee.id = %s """% (employee.id)

            request._cr.execute("""
                SELECT 
                    count(pip.id)
                FROM
                    appraisal_pip as pip
                    INNER JOIN hr_employee AS employee ON employee.id = pip.employee_id
                WHERE
                    pip.active = 't'
                AND
                    employee.active = 't'
                AND
                    pip.state != 'draftsssss'
                %s
            """, (domain, ))
            appraisals = request._cr.dictfetchone()
            count = appraisals.get('count', 0)
        return count

    #  Subordinates PIP 
    @http.route(['/supervisor/employee-pip-appraisals', '/supervisor/employee-pip-appraisals/<int:id>' ,'/supervisor/employee-pip-appraisals/page/<int:page>'], type='http', auth='user', website=True)
    def index(self, page=1, filterby=None, search_in='all', sortby=None, **kw):

        if kw.get('id'):
            appraisal_pip = request.env['appraisal.pip'].sudo().search([('id', '=', kw.get('id'))], limit=1)
            return http.request.render('nl_appraisal.pip_single_appraisal', {"id": kw.get('id'), 'appraisal_pip': appraisal_pip})
        
        if not request.env.user.employee_id:
            raise NotFound()

        searchbar_sortings = {
            'date_from_desc': {'label': _('Latest'), 'order': 'pip.create_date desc'},
            'date_from_asc': {'label': _('Oldest'), 'order': 'pip.create_date asc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': ''},
            'general_appraisal': {'label': _('Performance Appraisals'), 'domain': f" AND (pip.appraisal_type = 'general_appraisal') "},
            'probation_appraisal': {'label': _('Probation Appraisals'), 'domain': f" AND (pip.appraisal_type = 'probation_appraisal') "},
        }
        if not sortby:
            sortby = 'date_from_desc'
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']
        order = searchbar_sortings[sortby]['order']

        appraisal_count = self.get_appraisals_count(domain=domain, query_type="by_manager")

        pager = request.website.pager(
            url="/supervisor/employee-pip-appraisals",
            url_args={'sortby': sortby, 'filterby': filterby},
            total=appraisal_count,
            page=page,
            step=self._items_per_page
        )

        data = self.query_appraisals_data(order=order, domain=domain, limit=self._items_per_page, offset=pager['offset'], query_type="by_manager")
        values = {}
        values.update({
            'appraisals': data,
            'all_states': STATES_DICT,
            'all_appraisal_types': APPRAISAL_TYPES,
            'searchbar_sortings': searchbar_sortings,
            'default_url': '/supervisor/employee-pip-appraisals',
            'sortby': sortby,
            'search_in': search_in,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'page_name': 'Subordinate Performance Plans',
            'pager': pager,
        })

        return http.request.render('nl_appraisal.all_pip_appraisals', values)

    @http.route('/supervisor/get-pip-employee-appraisals', type='json', method=['POST'], auth='user')
    def get_sup_pip_single_appraisal(self, **kw):
        data = request.jsonrequest
        record = self.query_appraisals_data(view_type="form_view", appraisal_pip_id = data.get('appraisal_pip_id'), query_type="by_manager")
        return json.dumps(record, indent=4, sort_keys=True, default=str)

    @http.route('/supervisor/update-pip-employee-appraisals', type='json', method=['POST'], auth='user')
    def update_sup_single_pip_appraisal(self, **kw):
        """ Update Field Staff Appraisal Record for an employee by manager."""
        has_error = False
        errors = ''

        data = request.jsonrequest
        appraisal_pip_id = data.get('appraisal_pip_id')
        record = request.env['appraisal.pip'].browse(appraisal_pip_id).sudo()
        objective_obj = request.env['appraisal.pip.target'].sudo()
        review_obj = request.env['appraisal.pip.review'].sudo()

        # For setting reviews
        if data.get('setting_reviews', False) and 'set_reviews' in data:
            for review in data.get('set_reviews', {}).values():
                review_date = review.get('review_date')
                review_notes = review.get('notes')
                review_result = review.get('result')
                if review.get('id', False):
                    review_rec = review_obj.browse(review.get('id')).sudo()
                    old_date = review_rec.review_date
                    if record.state == 'planning':
                        if not review_date:
                            review_rec.unlink()
                        elif old_date != review_date:
                            review_rec = review_rec.write({'review_date': review_date})
                        record.validate_reviews_date()
                    elif record.state == 'assessment':
                        if (review_rec.notes != review_notes or review_rec.result != review_result):
                            review_rec = review_rec.write({
                                'notes': review_notes,
                                'result': review_result,
                                })
                            record.validate_reviews()
                else:
                    # Creating new reviews always called from planning state
                    if review_date:
                        review_rec = review_obj.create({
                            'review_date': review_date, 
                            'appraisal_pip_id': appraisal_pip_id
                            })
                    record.validate_reviews_date()

        # For setting pip objectives
        if data.get('setting_objectives', False) and not has_error and 'set_objectives' in data:
            for objective in data.get('set_objectives', {}).values():
                objective_name = objective.get('name')
                performance_concern = objective.get('performance_concern')
                agreed_improvement_action = objective.get('agreed_improvement_action')
                support = objective.get('support')
                if objective.get('id', False):
                    objective_rec = objective_obj.browse(objective.get('id')).sudo()
                    
                    if not objective_name and not performance_concern and not agreed_improvement_action and not support:
                        objective_rec.unlink()
                    elif (objective_rec.name != objective_name) or (objective_rec.performance_concern != performance_concern) \
                        or (objective_rec.agreed_improvement_action != agreed_improvement_action) or (objective_rec.support != support) :
                        objective_rec.write({
                            'name': objective_name, 
                            'performance_concern': performance_concern,
                            'agreed_improvement_action': agreed_improvement_action,
                            'support': support,
                            })
                    record.validate_targets()
                else:
                    if objective_name or performance_concern or agreed_improvement_action or support:
                        objective_rec = objective_obj.create({
                            'name': objective_name, 
                            'performance_concern': performance_concern,
                            'agreed_improvement_action': agreed_improvement_action,
                            'support': support,
                            'appraisal_pip_id': appraisal_pip_id
                            })
                    record.validate_targets()

        # If changing state
        if data.get('setting_state', False):
            target_state = data.get('target_state', '')
            if record.state == 'planning' and target_state == 'performance_period':
                record.move_to_performance_period()
            elif record.state == 'assessment' and target_state == 'planning':
                record.move_to_planning()
            elif record.state == 'assessment' and target_state == 'final_comments':
                record.move_to_final_comments()

        
        if data.get('state_returning', False):
            if not data.get('sup_state_comment', False):
                raise ValidationError('Please fill in the required input.')
            if record.state == 'final_comments':
                record.write({'state': 'assessment'})
            
            record.message_post(body=data.get('sup_state_comment'), message_type="comment", subtype_xmlid= "mail.mt_comment")

        response = {'update_status': 'success'} 
        if  has_error: 
           response = {'update_status': 'fail', 'errors': errors}
        return json.dumps(response)

    # My PIP
    @http.route(['/employee/my-pip-appraisals', '/employee/my-pip-appraisals/<int:id>', '/employee/my-pip-appraisals/page/<int:page>'], type='http', auth='user', website=True)
    def index_my_appraisals(self, page=1, filterby=None, search_in='all', sortby=None, **kw):
        """ Return my appraisals portal view for an employee. """

        if kw.get('id'):
            appraisal_pip = request.env['appraisal.pip'].sudo().search([('id', '=', kw.get('id'))], limit=1)
            return http.request.render('nl_appraisal.pip_my_appraisal', {"id": kw.get('id'), 'appraisal_pip': appraisal_pip})

        if not request.env.user.employee_id:
            raise NotFound()

        searchbar_sortings = {
            'date_from_desc': {'label': _('Latest'), 'order': 'pip.create_date desc'},
            'date_from_asc': {'label': _('Oldest'), 'order': 'pip.create_date asc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': ''},
            'general_appraisal': {'label': _('Performance Appraisals'), 'domain': f" AND (pip.appraisal_type = 'general_appraisal') "},
            'probation_appraisal': {'label': _('Probation Appraisals'), 'domain': f" AND (pip.appraisal_type = 'probation_appraisal') "},
        }
        if not sortby:
            sortby = 'date_from_desc'
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']
        order = searchbar_sortings[sortby]['order']

        appraisal_count = self.get_appraisals_count(domain=domain, query_type="by_employee")

        pager = request.website.pager(
            url="/employee/my-pip-appraisals",
            url_args={'sortby': sortby, 'filterby': filterby},
            total=appraisal_count,
            page=page,
            step=self._items_per_page
        )

        data = self.query_appraisals_data(order=order, domain=domain, limit=self._items_per_page, offset=pager['offset'], query_type="by_employee")
        values = {}
        values.update({
            'appraisals': data,
            'all_states': STATES_DICT,
            'all_appraisal_types': APPRAISAL_TYPES,
            'searchbar_sortings': searchbar_sortings,
            'default_url': '/employee/my-pip-appraisals',
            'sortby': sortby,
            'search_in': search_in,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'page_name': 'My Performance Improvement Plans',
            'pager': pager,
        })
        return http.request.render('nl_appraisal.my_pip_appraisals', values)


    @http.route('/employee/get-my-pip-appraisals', type='json', method=['POST'], auth='user')
    def get_my_pip_single_appraisal(self, **kw):
        data = request.jsonrequest
        record = self.query_appraisals_data(view_type="form_view", appraisal_pip_id = data.get('appraisal_pip_id'), query_type="by_employee")
        return json.dumps(record, indent=4, sort_keys=True, default=str)

    @http.route('/employee/update-my-pip-appraisals', type='json', method=['POST'], auth='user')
    def update_my_pip_appraisal(self, **kw):
        """ update my Appraisal Record for"""
        has_error = False
        errors = ''

        data = request.jsonrequest
        appraisal_pip_id = data.get('appraisal_pip_id')
        record = request.env['appraisal.pip'].browse(appraisal_pip_id).sudo()

        # If changing state
        if data.get('setting_state', False):
            target_state = data.get('target_state', '')
            if record.state == 'final_comments' and target_state == 'done':
                record.move_to_done()
           

        response = {'update_status': 'success'} 
        if  has_error: 
           response = {'update_status': 'fail', 'errors': errors}
        return json.dumps(response)

    @http.route('/appraisal-pip-view/<model("appraisal.pip"):appraisal_pip>', type='http', website=True, auth='user')
    def appraisal_pip_view(self, appraisal_pip, **kw):
        return request.render('nl_appraisal.appraisal_pip_view', {'appraisal_pip': appraisal_pip, 'creteria_dict': CETERIA_DICT}) if appraisal_pip else request.render('website.page_404')