from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import urllib.parse as urlparse
from urllib.parse import parse_qs
from datetime import date, datetime, timedelta, time

class References(http.Controller):
    @http.route('/reference', type="http", auth="public", website=True)
    def reference(self, **kw):

        token = request.params.get('token')

        if not token:
            return http.request.render('nl_reference.thankyou')

        url_employee_id = request.params.get('id')
        today = datetime.today()

        print(token)
        print(url_employee_id) 
        company_id = request.env['res.company'].search([])
        employee_id = request.env['hr.employee'].sudo().search([('id','=',url_employee_id)])
        reference_details = request.env['employee.references'].sudo().search([('token','=',token)])


        return http.request.render('nl_employee.create_reference', {
            'employee_id': employee_id,
            'o':company_id,
            'referee': reference_details,
            'token': token,
            'today': today
        })



    @http.route('/reference/general/submit', type="http", auth="public", website=True)
    def submit_reference_general(self, **kw):
        print("Data Received.....", kw)

        token = kw.get('token')

        reference = request.env['employee.references'].sudo().search([('token','=',token)])
        print(token)

        reference.update({
            'candidate_capacity' : kw.get('candidate_capacity'),
            'key_responsibilities' : kw.get('key_responsibilities'),
            'candidate_performance' : kw.get('candidate_performance'),
            'improvement_areas' : kw.get('improvement_areas'),
            'good_terms' : kw.get('good_terms'),
            'work_quality' : kw.get('work_quality'),
            'candidate_rehiring' : kw.get('candidate_rehiring'),
            'team_work_rating' : kw.get('team_work_rating'),
            'candidate_punctuality' : kw.get('candidate_punctuality'),
            'multi_tasking' : kw.get('multi_tasking'),
            'employee_self_sufficincies' : kw.get('employee_self_sufficincies'),
            'other_skills' : kw.get('other_skills'),
            'further_reservations' : kw.get('further_reservations'),
            'comments_explanation' : kw.get('comments_explanation'),
            
            'token': '',
            'state': 'done'
            
        })



        employee_id = request.env['hr.employee'].sudo().search([('id','=',reference.empl_id.id)])
        reference_details = request.env['employee.references'].sudo().search([('token','=',token)])
        company_id = request.env['res.company'].search([])

        return http.request.render('nl_employee.thankyou', {
            'employee_id': employee_id,
            'company_id':company_id
            
        })

        

    
