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
    'performance_period', 
    'self_review', 
    'supervisor_review', 
    '2nd_supervisor_review', 
    'final_comments', 
    'done',
    'cancel'
]
FIELD_STAFF_STATES = [
    'draft', 
    'supervisor_review', 
    'done',
    'cancel'
]
STATES_DICT = {
    'draft': 'Draft',
    'objective_setting': 'Objective Setting',
    'performance_period': 'Performance Period',
    'self_review': 'Self Assessment',
    'supervisor_review': 'Supervisor Assessment',
    '2nd_supervisor_review': '2nd Supervisor Assessment',
    'final_comments': 'Final Comments',
    'done': 'Done',
    'cancel': 'Cancel'
}
APPRAISAL_TYPES = {
    'none': 'N/A',
    'admin_staff': 'Annual Performance Review',
    'field_staff': 'Entry Level/Support Staff',
}
CONTRACT_REC = {
    'extension_of_contract': 'Extension of contract',
    'non_renewal_of_contract': 'Non-renewal of contract',
    'termination_of_contract': 'Termination of contract', 
    'performance_improvement_plan': 'Performance Improvement plan (Consult HR for process)',
}

SUP_ASSESSMENT_FIELDS = [
    'p3_q1_sup_comments', 
    'p3_q2_sup_comments', 
    'p3_q3_sup_comments', 
    'p3_q4_sup_comments'
    ]
SUP_CAREER_ASPIRATION_FIELDS = [
    'p4_sup_comments'
]
SUP_NEXT_YEAR_LEARNING_OBJECTIVES = [
    'next_individual_obj1',
    'next_individual_obj2'
]
SUP_RATING_FIELDS = [
    'p7_overall_rating',
    'p7_overall_rating_not_applicable',
    'p7_emp_contract_rec'
]
SECOND_SUP_FIELDS = [
    'p8_2sup_q1',
    'p8_2sup_q1_reason',
    'p8_2sup_q2',
]
ALLOWED_SUP_FIELDS = SUP_ASSESSMENT_FIELDS + SUP_CAREER_ASPIRATION_FIELDS + SUP_NEXT_YEAR_LEARNING_OBJECTIVES + SUP_RATING_FIELDS + SECOND_SUP_FIELDS

SUP_FIELD_STAFF_ASSESSMENT_FIELDS = [
    'field_p1_rating1',
    'field_p1_rating2',
    'field_p1_rating3',
    'field_p1_rating4',
    'field_p1_rating5',
    'field_p1_rating6',
    'field_p1_rating7',
    'field_p1_rating8',
    'field_p1_rating9',
    'field_p1_rating10',
    'field_p1_total_score'
]
SUP_FIELD_STAFF_EMP_FEEDBACK_REQUIRED_FIELDS = [
    "field_p2_q1",
    "field_p2_q2",
    "field_p2_q3",
    "field_p2_emp_comments"
]
SUP_FIELD_STAFF_EMP_FEEDBACK_NOT_REQUIRED_FIELDS = [
    "field_p2_q1_training_type",
]
SUP_FIELD_RATING_FIELDS = [
    'p7_overall_rating',
    'p7_overall_rating_not_applicable',
]
SUP_FIELD_OVERALL_ASSESSMENT_FIELDS = [
    'field_overall_assessment'
]

ALLOWED_SUP_Field_STAFF_FIELDS = SUP_FIELD_STAFF_ASSESSMENT_FIELDS + SUP_FIELD_STAFF_EMP_FEEDBACK_REQUIRED_FIELDS + SUP_FIELD_STAFF_EMP_FEEDBACK_NOT_REQUIRED_FIELDS + SUP_FIELD_RATING_FIELDS + SUP_FIELD_OVERALL_ASSESSMENT_FIELDS

EMP_ASSESSMENT_FIELDS = [
    'p3_q1_emp_comments', 
    'p3_q2_emp_comments', 
    'p3_q3_emp_comments', 
    'p3_q4_emp_comments'
    ]
EMP_CAREER_ASPIRATION_FIELDS = [
    'p4_emp_feed1',
    'p4_emp_feed2',
    'p4_emp_feed3',
    'p4_emp_feed4',
    'p4_emp_comments'     
]
EMP_UPWARD_FEEDBACK_FIELDS = [
    'p6_emp_feed1'
]
EMP_FINAL_COMMENTS_FIELDS = [
    'p9_emp_feed',
    'p9_emp_feed_comments'
]
ALLOWED_EMP_FIELDS = EMP_ASSESSMENT_FIELDS + EMP_CAREER_ASPIRATION_FIELDS + EMP_UPWARD_FEEDBACK_FIELDS + EMP_FINAL_COMMENTS_FIELDS

def split_list(custom_list, split_key):
    index = custom_list.index(split_key)
    lower_sequence_states = custom_list[:index]
    higher_sequence_states = custom_list[index+1:]

    return [lower_sequence_states, higher_sequence_states]


class WebsiteProfileExtended(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(WebsiteProfileExtended, self)._prepare_portal_layout_values()
        show_subordinates_appraisals = False
        subordinates_appraisals_count = 0
        if request.env.user.employee_id:
            request._cr.execute("""
                SELECT
                    count(app.id)
                FROM
                    employee_appraisal as app
                    INNER JOIN hr_employee AS employee ON employee.id = app.employee_id
                    INNER JOIN hr_employee AS manager ON  manager.id = employee.parent_id
                    LEFT JOIN hr_employee AS second_manager ON  second_manager.id = manager.parent_id
                WHERE
                    employee.active = 't'
                AND
                    app.active = 't'
                AND 
                CASE 
                    WHEN app.appraisal_type != 'field_staff' THEN app.state NOT IN ('draft', 'cancel') ELSE app.field_state NOT IN ('draft', 'cancel') END
                AND
                    manager.active = 't'
                AND
                    (manager.id = %s OR second_manager.id = %s)
            """, (request.env.user.employee_id.id, request.env.user.employee_id.id))
            appraisals = request._cr.dictfetchone()
            if appraisals.get('count', 0) > 0:
                show_subordinates_appraisals = True
                subordinates_appraisals_count = appraisals.get('count', 0)

        values.update({
            'show_subordinates_appraisals': show_subordinates_appraisals,
            'subordinates_appraisals_count': subordinates_appraisals_count
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
                    LEFT JOIN hr_job AS m_job ON manager.job_id = m_job.id
                    LEFT JOIN hr_employee AS second_manager ON  second_manager.id = manager.parent_id
                """
                domain += """ 
                    AND (manager.id = %s OR second_manager.id = %s)"""% (employee.id, employee.id )
                fields += """,
                    CASE
                        WHEN manager.id = %s AND (second_manager.id != %s OR second_manager.id IS NULL ) THEN 'is_only_manager'
                        WHEN second_manager.id = %s AND (manager.id != %s OR manager.id is NULL ) THEN 'is_only_second_manager'
                        WHEN manager.id = %s AND second_manager.id = %s THEN 'both_user'
                    END manager_type,
                    manager.name as manager_name, 
                    second_manager.name as second_manager_name,
                    m_job.name as manager_job
                    """% (employee.id, employee.id, employee.id, employee.id, employee.id, employee.id )
            else:
                joins += """ 
                    LEFT JOIN hr_employee AS manager ON  manager.id = employee.parent_id 
                    LEFT JOIN hr_job AS m_job ON manager.job_id = m_job.id
                    LEFT JOIN hr_employee AS second_manager ON  second_manager.id = manager.parent_id 
                """
                fields += """, 
                    m_job.name as manager_job,
                    manager.name as manager_name, 
                    second_manager.name as second_manager_name """
                domain += """ AND app.employee_id = %s """% (employee.id,)
                appraisal_id = kw.get('appraisal_id', False)
                if appraisal_id: 
                    domain += """ AND app.id = %s """% (appraisal_id)

            if view_type == "list_view":
                limit_and_offset_order = """
                    ORDER BY %s
                    LIMIT %s
                    OFFSET %s
                """% (order, limit, offset)
            else:
                fields += """,
                    app.p3_q1_sup_comments,
                    app.p3_q2_sup_comments,
                    app.p3_q3_sup_comments,
                    app.p3_q4_sup_comments,
                    app.p4_sup_comments,
                    app.next_individual_obj1,
                    app.next_individual_obj2,
                    app.p7_overall_rating,
                    app.p7_overall_rating_not_applicable,
                    app.p7_emp_contract_rec,
                    app.p8_2sup_q1,
                    app.p8_2sup_q1_reason,
                    app.p8_2sup_q2,
                    app.create_date,
                    -- Employee Self Assessment
                    app.p3_q1_emp_comments,
                    app.p3_q2_emp_comments,
                    app.p3_q3_emp_comments,
                    app.p3_q4_emp_comments,
                    -- Employee Career Aspiration
                    app.p4_emp_feed1,
                    app.p4_emp_feed2,
                    app.p4_emp_feed3,
                    app.p4_emp_feed4,
                    app.p4_emp_comments,
                    -- Employee Upward Comments
                    app.p6_emp_feed1,
                    -- Employee final comments
                    app.p9_emp_feed,
                    app.p9_emp_feed_comments,
                    -- signature part
                    app.employee_sign_date,
                    app.manager_sign_date,
                    app.second_manager_sign_date,

                    -- field staff appraisal fields
                    -- performance assessments
                    app.field_p1_rating1,
                    app.field_p1_rating2,
                    app.field_p1_rating3,
                    app.field_p1_rating4,
                    app.field_p1_rating5,
                    app.field_p1_rating6,
                    app.field_p1_rating7,
                    app.field_p1_rating8,
                    app.field_p1_rating9,
                    app.field_p1_rating10,
                    app.field_p1_total_score,
                    
                    -- employee feed back fields staff by manager
                    app.field_p2_q1,
                    app.field_p2_q1_training_type,
                    app.field_p2_q2,
                    app.field_p2_q3,
                    app.field_p2_emp_comments,
                    app.field_overall_assessment
                """

            request._cr.execute("""
                SELECT
                    app.id,
                    app.state,
                    app.appraisal_type,
                    app.field_state,
                    employee.id as emp_id,
                    employee.name as employee_name,
                    employee.idc_no as employee_idc_no,
                    app.review_period_start_date as from_date,
                    app.review_period_end_date as to_date,
                    job.name as position,
                    unit.name as unit_name,
                    office.name as office,
                    department.name as department_name
                    %s
                FROM
                    employee_appraisal as app
                    INNER JOIN hr_employee AS employee ON employee.id = app.employee_id
                    LEFT JOIN office AS office ON employee.office_id = office.id
                    LEFT JOIN hr_job AS job ON employee.job_id = job.id
                    LEFT JOIN hr_unit as unit ON employee.unit_id = unit.id
                    LEFT JOIN hr_department as department ON employee.department_id = department.id
                    %s
                WHERE
                    employee.active = 't'
                AND
                CASE 
                    WHEN app.appraisal_type != 'field_staff' THEN app.state NOT IN ('draft', 'cancel') ELSE app.field_state NOT IN ('draft', 'cancel') END
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
                    meta_info =  {
                        'hasCurrentComponentAccess': True,
                        'hasCurrentComponentAccessMessage': '',
                        'setSubmitAccess': True,
                        }
                    # Field Staff Data
                    if appraisal.get('appraisal_type', '') == "field_staff":
                        state = appraisal.get('field_state', '')
                        meta_info.update({
                            'next_stage': FIELD_STAFF_STATES[FIELD_STAFF_STATES.index(state)+1] if FIELD_STAFF_STATES.index(state) and FIELD_STAFF_STATES.index(state)+1  < len(FIELD_STAFF_STATES) else '',
                            'state': state,
                        })

                        # Field staff Managers Data
                        if by_managers:
                            meta_info.update({
                                'field_staff_performance_assessments_state': False,
                                'field_staff_employee_feedback_state': False,
                                'field_staff_overall_rating_state': False,
                                'field_staff_overall_assessment_state': False,
                                })
                            
                            # Set state each section data state. Has full data or not. (For showing Check sign and 'save and next' functionality)
                            if all(appraisal.get(field, False) for field in SUP_FIELD_STAFF_ASSESSMENT_FIELDS):
                                meta_info.update({"field_staff_performance_assessments_state": True})
                            
                            if all(appraisal.get(field, False) for field in SUP_FIELD_STAFF_EMP_FEEDBACK_REQUIRED_FIELDS):
                                meta_info.update({"field_staff_employee_feedback_state": True})
                                if appraisal.get('field_p2_q1', '') and appraisal.get('field_p2_q1') == 'yes' and not appraisal.get('field_p2_q1_training_type', ''):
                                    meta_info.update({"field_staff_employee_feedback_state": False})
                            
                            if  (appraisal.get("p7_overall_rating") and not appraisal.get("p7_overall_rating_not_applicable")) or appraisal.get("p7_overall_rating_not_applicable") or appraisal.get('field_p1_total_score'):
                                meta_info.update({"field_staff_overall_rating_state": True})
                            
                            if all(appraisal.get(field, False) for field in SUP_FIELD_OVERALL_ASSESSMENT_FIELDS):
                                meta_info.update({"field_staff_overall_assessment_state": True})

                            if state not in  ['supervisor_review']:
                                meta_info['hasCurrentComponentAccess'] = False
                                meta_info['setSubmitAccess'] = False
                                meta_info['hasCurrentComponentAccessMessage'] = "Not editable at this stage"
                                if state == 'done':
                                    meta_info['hasCurrentComponentAccessMessage'] = "This appraisal record has been finalized and can only be viewed"
                        
                        # Field Staff Employees Data
                        else:
                            meta_info['hasCurrentComponentAccess'] = False
                            meta_info['setSubmitAccess'] = False
                            meta_info['hasCurrentComponentAccessMessage'] = "Not editable at this stage"
                            if state == 'supervisor_review':
                                meta_info['hasCurrentComponentAccessMessage'] = "This appraisal record is under supervisor review."
                            if state == 'done':
                                meta_info['hasCurrentComponentAccessMessage'] = "This appraisal record has been finalized and can only be viewed"
                    
                    # Admin Staff Data
                    elif appraisal.get('appraisal_type', '') == 'admin_staff':
                        state = appraisal.get('state', '')
                        meta_info.update({
                            'general_objective_feed_state': False,
                            'learning_objective_feed_state': False,
                            'employee_assessment_state': False,
                            'employee_career_aspiration_state': False,
                            'next_stage': STATES[STATES.index(state)+1] if STATES.index(state) and STATES.index(state)+1  < len(STATES) else '',
                            'state': state,
                            })

                        # Admin Staff Managers Data
                        if by_managers:
                            meta_info.update({
                                'setting_general_objective_state': False,
                                'setting_learning_objective_state': False,
                                'setting_general_objective_state_next': False,
                                'setting_learning_objective_state_next': False,
                                'setting_performance_rating_state': False,
                                })

                            # Set state each section data state. Has full data or not. (For showing Check sign and 'save and next' functionality)
                            if all(appraisal.get(field, False) for field in SUP_ASSESSMENT_FIELDS):
                                meta_info.update({"employee_assessment_state": True})
                            
                            if all(appraisal.get(field, False) for field in SUP_CAREER_ASPIRATION_FIELDS):
                                meta_info.update({"employee_career_aspiration_state": True})
                            
                            if all(appraisal.get(field, False) for field in SUP_NEXT_YEAR_LEARNING_OBJECTIVES):
                                meta_info.update({"setting_learning_objective_state_next": True})
                                
                            if appraisal.get("p7_emp_contract_rec") and ((appraisal.get("p7_overall_rating") and not appraisal.get("p7_overall_rating_not_applicable")) or appraisal.get("p7_overall_rating_not_applicable")):
                                meta_info.update({"setting_performance_rating_state": True})

                            # Set Access Data (To Show warning message, show hide edit buttons and disable/enable submit form part.)
                            if state not in  ['objective_setting', 'performance_period', 'supervisor_review', '2nd_supervisor_review']:
                                meta_info['hasCurrentComponentAccess'] = False
                                meta_info['setSubmitAccess'] = False
                                meta_info['hasCurrentComponentAccessMessage'] = "Not editable at this stage"
                                if state == 'self_review':
                                    meta_info['hasCurrentComponentAccessMessage'] = "You cannot edit this appraisal record at this stage. You can view the feedback that the employee provides here as they conduct their self-assessment. You will be notified once the self assessment stage is complete"
                                elif state == 'final_comments':
                                    meta_info['hasCurrentComponentAccessMessage'] = "You cannot edit this appraisal record at this stage."
                                elif state == 'done':
                                    meta_info['hasCurrentComponentAccessMessage'] = "This appraisal record has been finalized and can only be viewed"


                            elif state in ['objective_setting', 'performance_period', 'supervisor_review'] and appraisal.get('manager_type', '') not in ['is_only_manager', 'both_user']:
                                meta_info['hasCurrentComponentAccess'] = False
                                meta_info['hasCurrentComponentAccessMessage'] = "Only editable by first line manager."
                                meta_info['setSubmitAccess'] = False
                            elif state == '2nd_supervisor_review' and appraisal.get('manager_type', '') not in ['is_only_second_manager', 'both_user']:
                                meta_info['hasCurrentComponentAccess'] = False
                                meta_info['hasCurrentComponentAccessMessage'] = "Only editable by second line manager."
                                meta_info['setSubmitAccess'] = False
                            elif (state == 'performance_period'):
                                meta_info['setSubmitAccess'] = False

                        # Admin Staff Employees Data
                        else:
                            meta_info.update({'emp_upward_feedback_state': False})

                            # Set state each section data state. Has full data or not. (For showing Check sign and 'save and next' functionality)
                            if all(appraisal.get(field, False) for field in EMP_ASSESSMENT_FIELDS):
                                meta_info.update({"employee_assessment_state": True})
                            
                            if all(appraisal.get(field, False) for field in EMP_CAREER_ASPIRATION_FIELDS):
                                meta_info.update({"employee_career_aspiration_state": True})

                            if all(appraisal.get(field, False) for field in EMP_UPWARD_FEEDBACK_FIELDS):
                                meta_info.update({"emp_upward_feedback_state": True})

                            # Set Access Data (To Show warning message, show hide edit buttons and disable/enable submit form part.)
                            if state not in ['self_review', 'final_comments']:
                                meta_info['hasCurrentComponentAccess'] = False
                                meta_info['hasCurrentComponentAccessMessage'] = "Not editable at this stage."
                                if state == 'objective_setting':
                                    meta_info['hasCurrentComponentAccessMessage'] = "You can not edit this appraisal record at this stage. Your supervisor is in the process of setting your objectives for the upcoming appraisal period."
                                elif state == 'performance_period':
                                    meta_info['hasCurrentComponentAccessMessage'] = "You cannot edit this appraisal record at this stage. Should you feel the need to revise your objectives for the current appraisal period, please contact your supervisor."
                                elif state in ['supervisor_review', '2nd_supervisor_review']:
                                    meta_info['hasCurrentComponentAccessMessage'] = "You cannot edit this appraisal record. Please contact HR should you have any comments or questions."
                                elif state == 'done':
                                    meta_info['hasCurrentComponentAccessMessage'] = "This appraisal record has been finalized and can only be viewed"
                                meta_info['setSubmitAccess'] = False
                            

                        # Objective ids
                        request._cr.execute("""
                            SELECT 
                                id,
                                name,
                                manager_feedback,
                                employee_feedback,
                                expected_outcome,
                                rating
                            FROM
                                employee_appraisal_objectives
                            WHERE
                                appraisal_id = %s
                            ORDER BY
                                id asc
                        """, (kw.get('appraisal_id'),))
                        objectives = request._cr.dictfetchall()
                        appraisal.update({'objectives': objectives})
                        if by_managers:
                            if objectives and len(list(filter( lambda x: ( not x.get('manager_feedback', '') or not x.get('rating', False)), objectives))) < 1:
                                meta_info.update({"general_objective_feed_state": True})
                            meta_info.update({"setting_general_objective_state": objectives and True or False})
                        else:
                            if objectives and len(list(filter( lambda x: ( not x.get('employee_feedback', '')), objectives))) < 1:
                                meta_info.update({"general_objective_feed_state": True})
                        # Individual Objective ids
                        request._cr.execute("""
                            SELECT 
                                id,
                                name,
                                manager_feedback,
                                employee_feedback,
                                rating
                            FROM
                                employee_appraisal_objectives
                            WHERE
                                individual_appraisal_id = %s
                            ORDER BY 
                                id asc
                        """, (kw.get('appraisal_id'),))
                        objectives = request._cr.dictfetchall()
                        appraisal.update({'individual_objectives': objectives})
                        if by_managers:
                            if objectives and len(list(filter( lambda x: ( not x.get('manager_feedback', '')), objectives))) < 1:
                                meta_info.update({"learning_objective_feed_state": True})
                            meta_info.update({"setting_learning_objective_state": objectives and True or False})
                        else:
                            if objectives and len(list(filter( lambda x: ( not x.get('employee_feedback', '')), objectives))) < 1:
                                meta_info.update({"learning_objective_feed_state": True})

                        # Objective next year ids
                        request._cr.execute("""
                            SELECT 
                                id,
                                name,
                                expected_outcome
                            FROM
                                employee_appraisal_objectives
                            WHERE
                                next_appraisal_id = %s
                            ORDER BY 
                                id asc
                        """, (kw.get('appraisal_id'),))
                        objectives = request._cr.dictfetchall()
                        appraisal.update({'next_year_objectives': objectives})
                        if objectives and len(list(filter( lambda x: ( not x.get('name', '') or not x.get('expected_outcome', False)), objectives))) < 1:
                            meta_info.update({"setting_general_objective_state_next": True})

                    appraisal.update({"metaInfo": meta_info})
                    data = appraisal
                    data.update({"all_states": STATES_DICT, 'contract_rec': CONTRACT_REC, 'all_appraisal_types': APPRAISAL_TYPES})
                    data.update({'by_managers': by_managers or False})
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
                    count(app.id)
                FROM
                    employee_appraisal as app
                    INNER JOIN hr_employee AS employee ON employee.id = app.employee_id
                    %s
                WHERE
                    employee.active = 't'
                AND
                CASE
                    WHEN app.appraisal_type != 'field_staff' THEN app.state NOT IN ('draft', 'cancel') ELSE app.field_state NOT IN ('draft', 'cancel') END
                AND
                    app.active = 't'
                %s
            """% (joins, domain,))
            appraisals = request._cr.dictfetchone()
            count = appraisals.get('count', 0)
        return count

    @http.route(['/supervisor/employee-appraisals', '/supervisor/employee-appraisals/<int:id>' ,'/supervisor/employee-appraisals/page/<int:page>'], type='http', auth='user', website=True)
    def index(self, page=1, filterby=None, search_in='all', sortby=None, **kw):

        if kw.get('id'):
            appraisal = request.env['employee.appraisal'].sudo().search([('id', '=', kw.get('id'))], limit=1)
            if appraisal and appraisal.appraisal_type  == 'field_staff':
                return http.request.render('nl_appraisal.field_staff_single_appraisal', {"id": kw.get('id'), 'appraisal': appraisal})
            else:
                return http.request.render('nl_appraisal.single_appraisal', {"id": kw.get('id'), 'appraisal': appraisal})

        if not request.env.user.employee_id:
            raise NotFound()

        current_year_start = fields.Date.today().replace(day=1, month=3)
        current_year_end = fields.Date.today().replace(current_year_start.year+1, day=28, month=2)
        searchbar_sortings = {
            'date_from_desc': {'label': _('Latest'), 'order': 'app.review_period_start_date desc'},
            'date_from_asc': {'label': _('Oldest'), 'order': 'app.review_period_start_date asc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': ''},
            'current_year': {'label': _('This Year'), 'domain': f" AND (app.review_period_start_date BETWEEN '{current_year_start}' AND '{current_year_end}')"},
            'admin_staff': {'label': _('Annual Performance Review'), 'domain': f" AND (app.appraisal_type = 'admin_staff') "},
            'field_staff': {'label': _('Entry Level/Support Staff'), 'domain': f" AND (app.appraisal_type = 'field_staff') "},
        }
        if not sortby:
            sortby = 'date_from_desc'
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']
        order = searchbar_sortings[sortby]['order']

        appraisal_count = self.get_appraisals_count(domain=domain, query_type="by_manager")

        pager = request.website.pager(
            url="/supervisor/employee-appraisals",
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
            'default_url': '/supervisor/employee-appraisals',
            'sortby': sortby,
            'search_in': search_in,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'page_name': 'Subordinates Appraisals',
            'pager': pager,
        })

        return http.request.render('nl_appraisal.all_appraisals', values)
    
    @http.route('/supervisor/get-employee-appraisals', type='json', method=['POST'], auth='user')
    def get_sup_single_appraisal(self, **kw):
        data = request.jsonrequest
        domain = f" AND app.id = {data.get('appraisal_id')}"
        record = self.query_appraisals_data(domain=domain, view_type="form_view", appraisal_id = data.get('appraisal_id'), query_type="by_manager")
        return json.dumps(record, indent=4, sort_keys=True, default=str)
    
    @http.route('/supervisor/update-employee-appraisals', type='json', method=['POST'], auth='user')
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
        OBJECTIVE_TYPES = [
            {
                'name': 'set_objectives', 
                'appraisal_id_field': 'appraisal_id', 
                'feedback_key': 'sup_objectives_feedback', 
                'validation_function': 'validate_general_objectives',
                'feedback_validation_function': 'validate_general_objectives_sup_feedback'
            },
            {
                'name': 'set_individual_objectives', 
                'appraisal_id_field': 'individual_appraisal_id', 
                'feedback_key': 'sup_individual_objectives_feedback', 
                'validation_function': 'validate_learning_objectives',
                'feedback_validation_function': 'validate_learning_objectives_sup_feedback'
            }
        ]
        data = request.jsonrequest
        appraisal_id = data.get('appraisal_id')
        to_update_data = dict(filter(lambda elem: elem[0] in ALLOWED_SUP_FIELDS, data.items()))
        record = request.env['employee.appraisal'].browse(appraisal_id).sudo()
        objective_obj = request.env['employee.appraisal.objectives'].sudo()

        if to_update_data and not has_error:
            record.write(to_update_data)
    
            # Assessment Validations
            if data.get('has_sup_assessments_feed', False):
                record.validate_employee_sup_assessments()
            # Career aspiration validations
            if data.get('has_sup_career_aspiration', False):
                record.validate_employee_sup_career()
            # Next Year two learing ovbjectives.
            if data.get('setting_next_year_learning_objectives', False):
                record.validate_next_year_learning_obj()
            # Performance Rating validates
            if data.get('has_sup_performance_rating', False):
                record.validate_sup_performance_rating()
            # Validate second supervisor
            if data.get('setting_2nd_supervisor_data', False):
                record.validate_2nd_sup_fields()

        if data.get('state_returning', False):
            if not data.get('sup_state_comment', False):
                raise ValidationError('Please fill in the required input.')
            if record.state == 'supervisor_review':
                record.write({'state': 'self_review'})
            elif record.state in ['final_comments', '2nd_supervisor_review']:
                record.write({'state': 'supervisor_review'})
            record.message_post(body=data.get('sup_state_comment'), message_type="comment", subtype_xmlid= "mail.mt_comment")

        # If changing state
        elif data.get('setting_state', False):
            target_state = data.get('target_state', '')
            
            if record.state == 'supervisor_review': 
                if target_state == '2nd_supervisor_review':
                    record.move_to_2ndsup_review()
                elif target_state == 'final_comments':
                    record.move_to_final_comments()

            elif record.state == 'objective_setting' and target_state == 'performance_period':
                record.move_to_performance_period()
            elif record.state == '2nd_supervisor_review' and target_state == 'final_comments':
                record.move_to_final_comments()


        # For updating and creating objective records
        if data.get('setting_objectives', False) and not has_error:
            if 'set_objectives' in data:
                notify_employee = False
                for objective in data.get('set_objectives', {}).values():
                    objective_name = objective.get('name')
                    objective_outcome = objective.get('expected_outcome')
                    if objective.get('id', False):
                        objective_rec = objective_obj.browse(objective.get('id')).sudo()
                        
                        if not objective_name and not objective_outcome:
                            objective_rec.unlink()
                        elif (objective_rec.name != objective_name) or (objective_rec.expected_outcome != objective_outcome):
                            objective_rec.write({'name': objective_name, 'expected_outcome': objective_outcome})
                        record.validate_general_objectives()
                        
                        if record.state == 'performance_period':
                            notify_employee = True
                    
                    else:
                        if objective_name or objective_outcome:
                            objective_rec = objective_obj.create({'name': objective_name, 'expected_outcome': objective_outcome, 'appraisal_id': appraisal_id})
                        record.validate_general_objectives()

                if notify_employee:
                    record.notify_objectives_changes()

            elif 'set_individual_objectives' in data:
                notify_employee = False
                for objective in data.get('set_individual_objectives', {}).values():
                    objective_name = objective.get('name')
                    if objective.get('id', False):
                        objective_rec = objective_obj.browse(objective.get('id')).sudo()
                        
                        if not objective_name:
                            objective_rec.unlink()
                        elif (objective_rec.name != objective_name):
                            objective_rec.write({'name': objective_name})
                        
                        record.validate_learning_objectives()
                        
                        if record.state == 'performance_period':
                            notify_employee = True
                    else:
                        if objective_name:  
                            objective_rec = objective_obj.create({'name': objective_name, 'individual_appraisal_id': appraisal_id})
                        record.validate_learning_objectives()

                if notify_employee:
                    record.notify_objectives_changes()
                                
        # for manager feedback on objectives
        if data.get('has_sup_objective', False) and not has_error:
            for objective_type in OBJECTIVE_TYPES:
                if objective_type.get('feedback_key', False) in data:
                    for objective in data.get(objective_type.get('feedback_key', False)).values():
                        objecive_record = objective_obj.browse(objective.get('id'))
                        rating = str(objective.get('rating')) if objective.get('rating') else ''
                        if objecive_record.manager_feedback != objective.get('sup_feedback') or objecive_record.rating != rating:
                            objecive_record.sudo().write({'manager_feedback': objective.get('sup_feedback'), 'rating': rating})
                    getattr(record, objective_type.get('feedback_validation_function'))()
                    if objective_type.get('feedback_key', False) == 'sup_objectives_feedback':
                        record.calculate_performance_rating()


        # Next Year objectives
        if data.get('setting_next_year_objectives', False) and 'set_next_year_objectives' in data and not has_error:
            for objective in data.get('set_next_year_objectives', {}).values():
                objective_name = objective.get('name')
                objective_outcome = objective.get('expected_outcome')
                if objective.get('id', False):
                    old_objective = objective_obj.browse(objective.get('id')).sudo()
                    if not objective_name and not objective_outcome:
                        old_objective.unlink()
                    elif (old_objective.name != objective_name) or (old_objective.expected_outcome != objective_outcome):
                        old_objective.write({'name': objective_name, 'expected_outcome': objective_outcome})
                    record.validate_general_objectives_next()
                else:
                    if objective_name or objective_outcome:
                        objective_obj.create({'name': objective_name, 'expected_outcome': objective.get('expected_outcome'), 'next_appraisal_id': appraisal_id})
                    record.validate_general_objectives_next()

        response = {'update_status': 'success'} 
        if  has_error: 
           response = {'update_status': 'fail', 'errors': errors}
        return json.dumps(response)

    @http.route('/supervisor/update-field-employee-appraisals', type='json', method=['POST'], auth='user')
    def update_sup_single_field_appraisal(self, **kw):
        """ Update Field Staff Appraisal Record for an employee by manager."""
        has_error = False
        errors = ''

        data = request.jsonrequest
        appraisal_id = data.get('appraisal_id')
        to_update_data = dict(filter(lambda elem: elem[0] in ALLOWED_SUP_Field_STAFF_FIELDS, data.items()))
        record = request.env['employee.appraisal'].browse(appraisal_id).sudo()
    
        if to_update_data and not has_error:
            record.write(to_update_data)
    
            # Assessment Validations
            if data.get('has_sup_fieldstaff_performance_assessments', False):
                record.validate_performance_field_staf_assessments()
                record.write({"p7_overall_rating": record.field_p1_total_score})

            # Manager feedback on behaf of Employee
            if data.get('has_sup_fieldstaff_employee_feedback', False):
                record.validate_employee_feedback_field_staff()

            # Manager overall feedback
            if data.get('has_sup_field_performance_rating', False):
                record.validate_sup_field_overall_rating()

            # Manager overall Assessment
            if data.get('has_sup_field_overall_assessment', False):
                record.validate_sup_field_overall_assessment()

         # If changing state
        if data.get('setting_state', False):
            target_state = data.get('target_state', '')
            
            if record.field_state == 'supervisor_review' and target_state == 'done':
                record.move_to_done_stage_field_staff()

        response = {'update_status': 'success'} 
        if  has_error: 
           response = {'update_status': 'fail', 'errors': errors}
        return json.dumps(response)
    

    # For My Appraisals
    @http.route(['/employee/my-appraisals', '/employee/my-appraisals/<int:id>', '/employee/my-appraisals/page/<int:page>'], type='http', auth='user', website=True)
    def index_my_appraisals(self, page=1, filterby=None, search_in='all', sortby=None, **kw):
        """ Return my appraisals portal view for an employee. """

        if kw.get('id'):
            appraisal = request.env['employee.appraisal'].sudo().search([('id', '=', kw.get('id'))], limit=1)
            if appraisal and appraisal.appraisal_type  == 'field_staff':
                return http.request.render('nl_appraisal.my_field_appraisal', {"id": kw.get('id'), 'appraisal': appraisal})
            else:
                return http.request.render('nl_appraisal.my_appraisal', {"id": kw.get('id'), 'appraisal': appraisal})

        if not request.env.user.employee_id:
            raise NotFound()
        current_year_start = fields.Date.today().replace(day=1, month=3)
        current_year_end = fields.Date.today().replace(current_year_start.year+1, day=28, month=2)
        searchbar_sortings = {
            'date_from_desc': {'label': _('Latest'), 'order': 'app.review_period_start_date desc'},
            'date_from_asc': {'label': _('Oldest'), 'order': 'app.review_period_start_date asc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': ''},
            'current_year': {'label': _('This Year'), 'domain': f" AND (app.review_period_start_date BETWEEN '{current_year_start}' AND '{current_year_end}')"},
            'admin_staff': {'label': _('Annual Performance Review'), 'domain': f" AND (app.appraisal_type = 'admin_staff') "},
            'field_staff': {'label': _('Entry Level/Support Staff'), 'domain': f" AND (app.appraisal_type = 'field_staff') "},
        }
        if not sortby:
            sortby = 'date_from_desc'
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']
        order = searchbar_sortings[sortby]['order']

        appraisal_count = self.get_appraisals_count(domain=domain, query_type="by_employee")

        pager = request.website.pager(
            url="/employee/my-appraisals",
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
            'default_url': '/employee/my-appraisals',
            'sortby': sortby,
            'search_in': search_in,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'page_name': 'Subordinates Appraisals',
            'pager': pager,
        })
        return http.request.render('nl_appraisal.all_my_appraisals', values)

    @http.route('/employee/get-my-appraisal', type='json', method=['POST'], auth='user')
    def get_my_appraisal(self, **kw):
        """ Get my appraisal data for an employee called from vue.js """
        data = request.jsonrequest
        if data.get('appraisal_id', False):
            record = self.query_appraisals_data(view_type='form_view', query_type="by_employee", appraisal_id=data.get('appraisal_id'))
        else:
            record = self.query_appraisals_data(view_type='form_view')
        return json.dumps(record, indent=4, sort_keys=True, default=str)
    
    @http.route('/employee/update-my-appraisal', type='json', method=['POST'], auth='user')
    def update_my_appraisal(self, **kw):
        """ Update my appraisal record for an employee.
        
            ALLOWED_FIELDS: fields that are allowed to be updated by an emplooyee
            OBJECTIVE_TYPE: objective types that are udateable by an employee.
         """
        has_error = False
        errors = {}
        OBJECTIVE_TYPES = [
            {
                "name": 'emp_objectives_feedback',
                'feedback_validation_function': 'validate_general_objectives_emp_feedback'
            },
            {
                "name": 'emp_individual_objectives_feedback',
                'feedback_validation_function': 'validate_leaning_objectives_emp_feedback'
            },
        ]
        data = request.jsonrequest
        to_update_data = dict(filter(lambda elem: elem[0] in ALLOWED_EMP_FIELDS, data.items()))
        record = request.env['employee.appraisal'].sudo().browse(data.get('appraisal_id'))
        objective_obj = request.env['employee.appraisal.objectives'].sudo()

        if to_update_data and not has_error:
            record.sudo().write(to_update_data)

            # Assessment Validations
            if data.get('has_emp_assessments_feed', False):
                record.sudo().validate_employee_emp_assessments()
            # Career aspiration validations
            if data.get('has_emp_career_aspiration', False):
                record.sudo().validate_employee_emp_career()
            # Upward Feedback validations
            if data.get('has_emp_upward_feedback', False):
                record.sudo().validate_employee_upward_feedback()
            # Validate final comments
            if data.get('setting_final_comments_data', False):
                record.sudo().validate_emp_final_comments()
    
        # If changing state
        if data.get('setting_state', False):
            target_state = data.get('target_state', '')
            if record.state == 'self_review' and target_state == 'supervisor_review':
                record.sudo().move_to_sup_review()
            elif record.state == 'final_comments' and target_state == 'done':
                record.sudo().move_to_done_stage()

        # updating employee feedback
        if data.get('has_emp_objective', False) and not has_error:
            for objective_type in OBJECTIVE_TYPES:
                if objective_type.get('name', False) in data:
                    for objective in data.get(objective_type.get('name', False)).values():
                        objective_record = objective_obj.browse(objective.get('id'))
                        if objective_record.employee_feedback != objective.get('emp_feedback'):
                           objective_record.sudo().write({'employee_feedback': objective.get('emp_feedback')})
                    getattr(record, objective_type.get('feedback_validation_function'))()

        response = {'update_status': 'success'} 
        if  has_error: 
           response = {'update_status': 'fail', 'errors': errors}
        return json.dumps(response)


    @http.route('/appraisal-view/<model("employee.appraisal"):appraisal>', type='http', website=True, auth='user')
    def appraisal_view(self, appraisal, **kw):
        if appraisal and appraisal.appraisal_type == 'field_staff':
            return request.render('nl_appraisal.field_appraisal_view', {'appraisal': appraisal}) if appraisal else request.render('website.page_404')
        return request.render('nl_appraisal.appraisal_view', {'appraisal': appraisal}) if appraisal else request.render('website.page_404')