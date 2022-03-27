from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import urllib.parse as urlparse
from urllib.parse import parse_qs

class References(http.Controller):
    @http.route('/interview', type="http", auth="public", website=True)
    def exit_interview(self, **kw):

        token = request.params.get('token')

        if not token:
            return http.request.render('nl_separation.exit_interview')

        url_employee_id = request.params.get('id') 

        print(token)
        print(url_employee_id) 

        employee_id = request.env['hr.employee'].sudo().search([('id','=',url_employee_id)])
        form_id = request.env['exit.interview.form'].sudo().search([('token','=',token)])

        if form_id:

            return http.request.render('nl_separation.exit_interview',{
                'employee_id': employee_id,
                'token': token,
            })
        
    @http.route('/interview/submit', type="http", auth="public", website=True)
    def submit_interview(self, **kw):
        print("Data Received.....", kw)
        token = request.params.get('token')
        selected_list = request.httprequest.form.getlist('leaving_reason')
        print(selected_list)
        form_id = request.env['exit.interview.form'].sudo().search([('token','=',token)])
        
        for item in selected_list:
            if item == 'Better employment elsewhere':
                form_id.better_employement_elsewhere = True
            if item == 'Difficulty with work &amp; family balance':
                form_id.diffucilt_with_work = True
            if item == 'Limited career advancement opportunities':
                form_id.limited_career = True
            if item == 'Pay/Compensation issues':
                form_id.pay_compensation = True
            if item == 'Benefits/entitlements issues':
                form_id.benefits = True
            if item == 'Dissatisfied with job duties':
                form_id.dissatisfied_job = True
            if item == 'Dissatisfied with working conditions':
                form_id.dissatisfied_working_condition = True
            if item == 'Supervision issues':
                form_id.supervision_issues = True
            if item == 'Concerned about own security':
                form_id.own_security = True
            if item == 'Continuation of higher education':
                form_id.higher_education = True
            

        

        if kw.get('place_of_work'):
            form_id.place_of_work = kw.get('place_of_work')

        if kw.get('working_condition'):
            form_id.working_condition = kw.get('working_condition')

        if kw.get('supervisor_relationship'):
            form_id.supervisor_relationship = kw.get('supervisor_relationship')

        if kw.get('understand_job'):
            form_id.understand_job = kw.get('understand_job')

        if kw.get('goals_and_objectives'):
            form_id.goals_and_objectives = kw.get('goals_and_objectives')

        if kw.get('ahead_of_time'):
            form_id.ahead_of_time = kw.get('ahead_of_time')

        if kw.get('well_done_recognition'):
            form_id.well_done_recognition = kw.get('well_done_recognition')

        if kw.get('constructive_feedback'):
            form_id.constructive_feedback = kw.get('constructive_feedback')

        if kw.get('problem_solving'):
            form_id.problem_solving = kw.get('problem_solving')

        if kw.get('respect'):
            form_id.respect = kw.get('respect')

        if kw.get('staff_concern'):
            form_id.staff_concern = kw.get('staff_concern')

        if kw.get('effort_keep'):
            form_id.effort_keep = kw.get('effort_keep')

        if kw.get('level_of_concern'):
            form_id.level_of_concern = kw.get('level_of_concern')

        if kw.get('compare'):
            form_id.compare = kw.get('compare')

        if kw.get('pay'):
            form_id.pay = kw.get('pay')

        if kw.get('increment'):
            form_id.increment = kw.get('increment')

        if kw.get('development'):
            form_id.development = kw.get('development')

        if kw.get('culture'):
            form_id.culture = kw.get('culture')

        if kw.get('cooperation'):
            form_id.cooperation = kw.get('cooperation')

        if kw.get('guidance_hr'):
            form_id.guidance_hr = kw.get('guidance_hr')

        if kw.get('guidance_finance'):
            form_id.guidance_finance = kw.get('guidance_finance')


        if kw.get('guidance_admin'):
            form_id.guidance_admin = kw.get('guidance_admin')

        if kw.get('guidance_procurement'):
            form_id.guidance_procurement = kw.get('guidance_procurement')

        if kw.get('guidance_tr'):
            form_id.guidance_tr = kw.get('guidance_tr')

        if kw.get('specific_expereinces'):
            form_id.specific_expereinces = kw.get('specific_expereinces')
        if kw.get('conditions'):
            form_id.conditions = kw.get('conditions')
        if kw.get('one_thing'):
            form_id.one_thing = kw.get('one_thing')
        if kw.get('lose_employee'):
            form_id.lose_employee = kw.get('lose_employee')
       
        if kw.get('reconsider_working'):
           form_id.reconsider_working = kw.get('reconsider_working')

        if kw.get('other_comments'):
            form_id.other_comments = kw.get('other_comments')
  
        form_id.token = ''

        return http.request.render('nl_employee.thankyou', {
            'company_id': request.env.company,
            
        })

        

        

        
        


        
           
        

            

    

        

    
