from odoo import http, _, fields
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
import json
from werkzeug.exceptions import NotFound
from odoo.tools.translate import _
from collections import OrderedDict
from odoo.exceptions import ValidationError


STATES = [
    'draft', 
    'objective_setting', 
    'probation_period',
    'self_assessment',
    'supervisor_assessment', 
    'final_comments', 
    'done', 
    'cancel'
]
STATES_DICT = {
    'draft': 'Draft',
    'objective_setting': 'Objective Setting',
    'probation_period': 'Probation Period',
    'self_assessment': 'Self Assessment',
    'supervisor_assessment': 'Supervisor Assessment',
    'final_comments': 'Final Comments',
    'done': 'Done',
    'cancel': 'Cancel'
}

SUP_ASSESSMENT_FIELDS = [
    'p2_q1', 
    'p2_q2', 
    'p2_q3', 
    'p2_q4',
    'p2_q5',
    ]

SUP_PERFORMANCE_FEEDBACK = [
    'p3_q1',
    'p3_q2',
    'p3_q3',
    'p3_sup_comments'
]

SUP_WAY_FORWARD_FIELDS = [
    'p4_q1',
    'p4_q2'
]

EMP_COMMENTS = [
    'p3_emp_comments',
    'emp_major_achievements'
]   
    # 'p4_q1',
    # 'p4_q2',
    # 'manager_sign_date'

ALLOWED_SUP_FIELDS = SUP_ASSESSMENT_FIELDS + SUP_PERFORMANCE_FEEDBACK + SUP_WAY_FORWARD_FIELDS


# EMP_ASSESSMENT_FIELDS = [
#     'p3_q1',
#     'employee_sign_date'
#     ]

# ALLOWED_EMP_FIELDS = EMP_ASSESSMENT_FIELDS


class WebsiteProfileExtended(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(WebsiteProfileExtended, self)._prepare_portal_layout_values()
        show_subordinates_probation_appraisals = False
        subordinates_probation_appraisals_count = 0
        show_my_probation_appraisals = False
        my_probation_appraisals_count = 0
        if request.env.user.employee_id:
            request._cr.execute("""
                SELECT
                    count(app.id)
                FROM
                    probation_appraisal as app
                    INNER JOIN hr_employee AS employee ON employee.id = app.employee_id
                    INNER JOIN hr_employee AS manager ON  manager.id = employee.parent_id
                WHERE
                    employee.active = 't'
                AND
                    app.active = 't'
                AND 
                    app.state != 'draft'
                AND 
                    app.state != 'cancel'
                AND
                    manager.active = 't'
                AND
                    manager.id = %s
            """, (request.env.user.employee_id.id,))
            appraisals = request._cr.dictfetchone()
            if appraisals.get('count', 0) > 0:
                show_subordinates_probation_appraisals = True
                subordinates_probation_appraisals_count = appraisals.get('count', 0)
            request._cr.execute("""
                SELECT
                    count(app.id)
                FROM
                    probation_appraisal as app
                    INNER JOIN hr_employee AS employee ON employee.id = app.employee_id
                WHERE
                    employee.active = 't'
                AND
                    app.active = 't'
                AND 
                    app.state != 'draft'
                AND 
                    app.state != 'objective_setting'
                AND 
                    app.state != 'cancel'
                AND
                    employee.id = %s
            """, (request.env.user.employee_id.id,))
            appraisals = request._cr.dictfetchone()
            if appraisals.get('count', 0) > 0:
                show_my_probation_appraisals = True
                my_probation_appraisals_count = appraisals.get('count', 0)

        values.update({
            'show_subordinates_probation_appraisals': show_subordinates_probation_appraisals,
            'subordinates_probation_appraisals_count': subordinates_probation_appraisals_count,
            'show_my_probation_appraisals': show_my_probation_appraisals,
            'my_probation_appraisals_count': my_probation_appraisals_count
            })
        return values



class AppraisalController(http.Controller):
    """ This Class handles CRUD operations of appraisal by manger for employee. """
    _items_per_page = 20

    def query_appraisals_data(self, limit='', offset='', order='', domain='', view_type='list_view', **kw):
        data = {}
        fields = ""
        joins = ""
        limit_and_offset_order = ""
        if request.env.user.employee_id:
            employee = request.env.user.employee_id
            by_managers = True if kw.get('query_type', 'by_manager') == 'by_manager' else False
            if by_managers:
                joins += """ 
                    INNER JOIN hr_employee AS manager ON  manager.id = employee.parent_id 
                    LEFT JOIN hr_job AS m_job ON m_job.id = manager.job_id 
                """
                domain += """ 
                    AND 
                        manager.id = %s 
                    """% (employee.id, )
                fields += """,
                    manager.name as manager_name
                    """
            else:
                joins += """ 
                    LEFT JOIN hr_employee AS manager ON  manager.id = employee.parent_id 
                    LEFT JOIN hr_job AS m_job ON m_job.id = manager.job_id 
                """
                fields += """, 
                    manager.name as manager_name,
                    manager.name as manager_name
                    """
                domain += """ AND app.employee_id = %s """% (employee.id,)
                appraisal_id = kw.get('appraisal_id', False)
                if appraisal_id: 
                    domain += """ AND app.id = %s """% (appraisal_id)
                domain += " AND app.state != 'objective_setting' "

            if view_type == "list_view":
                limit_and_offset_order = """
                    ORDER BY %s
                    LIMIT %s
                    OFFSET %s
                """% (order, limit, offset)
            else:
                fields += """,
                    app.p2_q1,
                    app.p2_q2,
                    app.p2_q3,
                    app.p2_q4,
                    app.p2_q5,
                    app.p3_q1,
                    app.p3_q2,
                    app.p3_q3,
                    app.p3_emp_comments,
                    app.emp_major_achievements,
                    app.p3_sup_comments,
                    app.p4_q1,
                    app.p4_q2,
                    app.employee_sign_date,
                    app.manager_sign_date
                """

            request._cr.execute("""
                SELECT
                    app.id,
                    app.state,
                    employee.id as emp_id,
                    employee.name as employee_name,
                    employee.idc_no as employee_idc_no,
                    app.start_date as from_date,
                    app.end_date as to_date,
                    job.name as position,
                    unit.name as unit_name,
                    office.name as office,
                    department.name as department_name,
                    manager.name as manager_name,
                    m_job.name as manager_position
                    %s
                FROM
                    probation_appraisal as app
                    INNER JOIN hr_employee AS employee ON employee.id = app.employee_id
                    LEFT JOIN office AS office ON employee.office_id = office.id
                    LEFT JOIN hr_job AS job ON employee.job_id = job.id
                    LEFT JOIN hr_unit as unit ON employee.unit_id = unit.id
                    LEFT JOIN hr_department as department ON employee.department_id = department.id
                    %s
                WHERE
                    employee.active = 't'
                AND
                    app.state != 'draft'
                AND
                    app.state != 'cancel'
                AND
                    app.active = 't'
                %s
                %s
            """% (fields, joins, domain, limit_and_offset_order))
            if view_type == 'list_view':
                appraisals = request._cr.dictfetchall()
                data = appraisals if appraisals else False
            else:
                appraisal = request._cr.dictfetchone()
                if appraisal:
                    # Meta info
                    state = appraisal.get('state', '')
                    meta_info = {
                        'hasCurrentComponentAccess': True,
                        'hasCurrentComponentAccessMessage': '',
                        'setSubmitAccess': True,
                        'objective_setting_feed_state': False,
                        'probation_period_feed_state': False,
                        'supervisor_assessment_state': False,
                        'performance_feedback': False,
                        'final_comments_state': False,
                        'next_stage': STATES[STATES.index(state)+1] if STATES.index(state) and STATES.index(state)+1  < len(STATES) else '',
                        'state': state,
                        }
                    if by_managers:
                        meta_info.update({
                            'setting_general_objective_state': False,
                            'setting_overall_assessment_state': False,
                            'setting_performance_feedback_state': False,
                            'setting_way_forward_state': False,
                            'setting_self_assessment_state': False,
                            })

                        # Set state each section data state. Has full data or not. (For showing Check sign and 'save and next' functionality) 
                        if all(appraisal.get(field, False) for field in SUP_ASSESSMENT_FIELDS):
                            meta_info.update({"setting_overall_assessment_state": True})

                        if all(appraisal.get(field, False) for field in SUP_PERFORMANCE_FEEDBACK):
                            meta_info.update({"setting_performance_feedback_state": True})

                        if appraisal.get('p4_q1', False):
                            if (appraisal.get('p4_q1') == 'no' and appraisal.get('p4_q2')) or appraisal.get('p4_q1'):
                                meta_info.update({'setting_way_forward_state': True})
          
                        # Set Access Data (To Show warning message, show hide edit buttons and disable/enable submit form part.)
                        if state not in  ['objective_setting', 'probation_period', 'supervisor_assessment']:
                            meta_info['hasCurrentComponentAccess'] = False
                            meta_info['hasCurrentComponentAccessMessage'] = "Not editable at this stage"
                            meta_info['setSubmitAccess'] = False

                    else:
                        meta_info.update({'emp_upward_feedback_state': False})

                        # Set state each section data state. Has full data or not. (For showing Check sign and 'save and next' functionality)
                        if all(appraisal.get(field, False) for field in EMP_COMMENTS):
                            meta_info.update({"setting_self_assessment_state": True})

                        # Set Access Data (To Show warning message, show hide edit buttons and disable/enable submit form part.)
                        if state not in ['final_comments', 'self_assessment']:
                            meta_info['hasCurrentComponentAccess'] = False
                            meta_info['hasCurrentComponentAccessMessage'] = "Not editable at this stage."
                            meta_info['setSubmitAccess'] = False
                        
                    appraisal.update({"metaInfo": meta_info})

                    # Objective ids
                    request._cr.execute("""
                        SELECT 
                            id,
                            name,
                            expected_outcome
                        FROM
                            probation_appraisal_objectives
                        WHERE
                            probation_appraisal_id = %s
                        ORDER BY
                            id asc
                    """, (kw.get('appraisal_id'),))
                    objectives = request._cr.dictfetchall()
                    appraisal.update({'objectives': objectives})
                    if objectives and len(list(filter( lambda x: ( not x.get('name', '') or not x.get('expected_outcome', False)), objectives))) < 1:
                        meta_info.update({"general_objective_feed_state": True})
                    if by_managers:
                        meta_info.update({"setting_general_objective_state": objectives and True or False})

                    data = appraisal
                    data.update({"all_states": STATES_DICT})
                    data.update({'by_managers': by_managers or False})
        return data

    @http.route('/supervisor/update-employee-probation-appraisals', type='json', method=['POST'], auth='user')
    def update_sup_single_appraisal(self, **kw):
        """ Update Appraisal Record for an employee by manager.
            
            setting_objective: Means manager is setting new objectives or updating name of objectives.
            set_objectives: Dictionary containing objectives to be created/updated.
            set_individual_objectives: Dictionary containing  individual objectives to be created/updated.
            Create New objective if the objective has no old id and should have atleast one field changed.
            Update objective record if atleast one field is changed and delete if the field name is blank.

         """
        has_error = False
        errors = ''

        data = request.jsonrequest
        appraisal_id = data.get('appraisal_id')
        to_update_data = dict(filter(lambda elem: elem[0] in ALLOWED_SUP_FIELDS, data.items()))
        record = request.env['probation.appraisal'].browse(appraisal_id).sudo()
        objective_obj = request.env['probation.appraisal.objectives'].sudo()
        if to_update_data and not has_error:
            record.write(to_update_data)

            # Assessment Validations
            if data.get('has_sup_assessment', False):
                record.validate_assessments()

            # Performance Validation
            if data.get('has_sup_performance', False):
                record.validate_performance()

            # Way Forward Validation
            if data.get('has_sup_way_forward', False):
                record.validate_way_forward()



        # # If changing state
        if data.get('setting_state', False):
            target_state = data.get('target_state', '')
            
            if record.state == 'objective_setting' and  target_state == 'probation_period':
                record.move_to_probation_period()

            if record.state == 'supervisor_assessment' and  target_state == 'final_comments':
                record.move_to_final_commnets()
        
        if data.get('state_returning', False):
            if not data.get('sup_state_comment', False):
                raise ValidationError('Please fill in the required input.')
            if record.state == 'supervisor_assessment':
                record.write({'state': 'self_assessment'})
            elif record.state == 'final_comments':
                record.write({'state': 'supervisor_assessment'})
            record.message_post(body=data.get('sup_state_comment'), message_type="comment", subtype_xmlid= "mail.mt_comment")

        # For updating and creating objective records
        if data.get('setting_objectives', False) and not has_error:
            if 'set_objectives' in data:
                for objective in data.get('set_objectives').values():
                    objective_name = objective.get('name')
                    objective_outcome = objective.get('expected_outcome')
                    if objective.get('id', False):
                        objective_rec = objective_obj.browse(objective.get('id')).sudo()
                        if not objective_name and not objective_outcome:
                            objective_rec.unlink()
                        elif (objective_rec.name != objective_name) or (objective_rec.expected_outcome != objective_outcome):
                            objective_rec.write({'name': objective_name, 'expected_outcome': objective_outcome})
                        record.validate_general_objectives()
                    else:
                        if objective_name or objective_outcome:
                            objective_rec = objective_obj.create({'name': objective_name, 'expected_outcome': objective_outcome, 'probation_appraisal_id': appraisal_id})
                        record.validate_general_objectives()


        response = {'update_status': 'success'} 
        if  has_error: 
           response = {'update_status': 'fail', 'errors': errors}
        return json.dumps(response)

    @http.route('/supervisor/get-employee-probation-appraisals', type='json', method=['POST'], auth='user')
    def get_sup_single_appraisal(self, **kw):
        data = request.jsonrequest
        domain = f" AND app.id = {data.get('appraisal_id')}"
        record = self.query_appraisals_data(domain=domain, view_type="form_view", appraisal_id = data.get('appraisal_id'), query_type="by_manager")
        return json.dumps(record, indent=4, sort_keys=True, default=str)

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
                domain += """ AND app.state != 'objective_setting' AND employee.id = %s """% (employee.id)

            request._cr.execute("""
                SELECT
                    count(app.id)
                FROM
                    probation_appraisal as app
                    INNER JOIN hr_employee AS employee ON employee.id = app.employee_id
                    %s
                WHERE
                    employee.active = 't'
                AND
                    app.state != 'draft'
                AND
                    app.state != 'cancel'
                AND
                    app.active = 't'
                %s
            """% (joins, domain,))
            appraisals = request._cr.dictfetchone()
            count = appraisals.get('count', 0)
        return count

    @http.route(['/supervisor/employee-probation-appraisals', '/supervisor/employee-probation-appraisals/<int:id>' ,'/supervisor/employee-probation-appraisals/page/<int:page>'], type='http', auth='user', website=True)
    def index(self, page=1, filterby=None, search_in='all', sortby=None, **kw):

        if kw.get('id'):
            appr = request.env['probation.appraisal'].sudo().search([('id','=' ,kw.get('id'))])
            return http.request.render('nl_appraisal.single_probation_appraisal', {"id": kw.get('id'), 'appraisal': appr})


        if not request.env.user.employee_id:
            raise NotFound()
        current_year_start = fields.Date.today().replace(day=1, month=1)
        current_year_end = fields.Date.today().replace(current_year_start.year+1, day=31, month=12)
        searchbar_sortings = {
            'date_from_desc': {'label': _('Latest'), 'order': 'app.start_date desc'},
            'date_from_asc': {'label': _('Oldest'), 'order': 'app.end_date asc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': ''},
            'current_year': {'label': _('This Year'), 'domain': f" AND (app.start_date BETWEEN '{current_year_start}' AND '{current_year_end}')"},
        }
        if not sortby:
            sortby = 'date_from_desc'
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']
        order = searchbar_sortings[sortby]['order']

        appraisal_count = self.get_appraisals_count(domain=domain, query_type="by_manager")

        pager = request.website.pager(
            url="/supervisor/employee-probation-appraisals",
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
            'searchbar_sortings': searchbar_sortings,
            'default_url': '/supervisor/employee-probation-appraisals',
            'sortby': sortby,
            'search_in': search_in,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'page_name': 'Subordinates Probation Appraisals',
            'pager': pager,
        })
        return http.request.render('nl_appraisal.all_probation_appraisals', values)



    # For My Appraisals
    @http.route(['/employee/my-probation-appraisals', '/employee/my-probation-appraisals/<int:id>', '/employee/my-probation-appraisals/page/<int:page>'], type='http', auth='user', website=True)
    def index_my_appraisals(self, page=1, filterby=None, search_in='all', sortby=None, **kw):
        """ Return my appraisals portal view for an employee. """

        if kw.get('id', False):
            appr = request.env['probation.appraisal'].sudo().search([('id','=' ,kw.get('id'))])
            return http.request.render('nl_appraisal.my_probation_appraisal', {"id": kw.get('id'), 'appraisal': appr})

        if not request.env.user.employee_id:
            raise NotFound()
        current_year_start = fields.Date.today().replace(day=1, month=1)
        current_year_end = fields.Date.today().replace(current_year_start.year+1, day=31, month=12)
        searchbar_sortings = {
            'date_from_desc': {'label': _('Latest'), 'order': 'app.start_date desc'},
            'date_from_asc': {'label': _('Oldest'), 'order': 'app.end_date asc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': ''},
            'current_year': {'label': _('This Year'), 'domain': f" AND (app.start_date BETWEEN '{current_year_start}' AND '{current_year_end}')"},
        }
        if not sortby:
            sortby = 'date_from_desc'
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']
        order = searchbar_sortings[sortby]['order']

        appraisal_count = self.get_appraisals_count(domain=domain, query_type="by_employee")

        pager = request.website.pager(
            url="/employee/my-probation-appraisals",
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
            'searchbar_sortings': searchbar_sortings,
            'default_url': '/employee/my-probation-appraisals',
            'sortby': sortby,
            'search_in': search_in,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'page_name': 'Probation Appraisals',
            'pager': pager,
        })
        return http.request.render('nl_appraisal.all_my_probation_appraisals', values)


    @http.route('/employee/get-my-probation-appraisal', type='json', method=['POST'], auth='user')
    def get_my_appraisal(self, **kw):
        """ Get my appraisal data for an employee called from vue.js """
        data = request.jsonrequest
        if data.get('appraisal_id', False):
            record = self.query_appraisals_data(view_type='form_view', query_type="by_employee", appraisal_id=data.get('appraisal_id'))
        else:
            record = self.query_appraisals_data(view_type='form_view')
        return json.dumps(record, indent=4, sort_keys=True, default=str)


    @http.route('/employee/update-my-probation-appraisal', type='json', method=['POST'], auth='user')
    def update_my_appraisal(self, **kw):
        """ Update my appraisal record for an employee.
        
            ALLOWED_FIELDS: fields that are allowed to be updated by an emplooyee
            OBJECTIVE_TYPE: objective types that are udateable by an employee.
         """
        has_error = False
        errors = {}

        data = request.jsonrequest
        to_update_data = dict(filter(lambda elem: elem[0] in EMP_COMMENTS, data.items()))
        record = request.env['probation.appraisal'].sudo().browse(data.get('appraisal_id'))

        if to_update_data and not has_error:
            record.sudo().write(to_update_data)

            # Validate final comments
            if data.get('setting_final_comments_data', False):
                record.sudo().validate_self_assessments()
            # Validate Self Assessment
            if data.get('setting_self_assessment_data', False):
                record.sudo().validate_self_assessments()
    
        # If changing state
        if data.get('setting_state', False):
            target_state = data.get('target_state', '')
            if record.state == 'final_comments' and target_state == 'done':
                record.sudo().validate_self_assessments()
                record.sudo().move_to_done_stage()
            elif record.state == 'self_assessment' and target_state == 'supervisor_assessment':
                record.sudo().validate_self_assessments()
                record.sudo().move_to_supervisor_assessment()

        response = {'update_status': 'success'} 
        if  has_error: 
           response = {'update_status': 'fail', 'errors': errors}
        return json.dumps(response)
    
    @http.route('/probation-appraisal-view/<model("probation.appraisal"):appraisal>', type='http', website=True, auth='user')
    def appraisal_view(self, appraisal, **kw):
        return request.render('nl_appraisal.probation_appraisal_view', {'appraisal': appraisal}) if appraisal else request.render('website.page_404')