# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from lxml import etree
from odoo import models, fields, api,_
from odoo.addons.nl_master.helpers import master_data
from odoo.addons.hr_skills.models.hr_resume import Employee as ExtendedEmployee
from odoo.addons.hr_holidays.models.hr_employee import HrEmployeeBase as HrEmployeeBaseExtended
import base64
import random
import string

import re

blood_group_type_list = [
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('O+', 'O+'),
    ('O-', 'O-')
]

class ContactPerson(models.Model):
    _name = 'contact.person'
    _description = 'Contact Person'

    name = fields.Char(
        string="Name"
    )
    employee_id = fields.Many2one('hr.employee')
    phone_number = fields.Char("Number")
    email = fields.Char("Email")
    address = fields.Text("Address")
    
class EmployeeBaseExtended(models.AbstractModel):
    _inherit = 'hr.employee.base'

    work_phone = fields.Char('Work Phone', compute="_compute_phones",  readonly=False)
    office_id = fields.Many2one('office',string="Office")

    @api.depends('address_id')
    def _compute_phones(self):
        for employee in self:
            return True

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
        
    @api.depends('birthday')
    def calculate_age(self):
        self.age = 0
        today = date.today() 
        if self.birthday:
            calculated_age = today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day)) 
            self.age = calculated_age

    private_email = fields.Char(related='address_home_id.email', string="Other Email", groups="hr.group_hr_user")
    phone = fields.Char(related='address_home_id.phone', related_sudo=False, readonly=False, string="Other Phone", groups="hr.group_hr_user")
    gender = fields.Selection( master_data.GENDER )
    
    second_manager_id = fields.Many2one('hr.employee','2nd Manager/Supervisor')
    leave_responsible_substitue = fields.Many2one('hr.employee','Leave Substitue Responsible')
    is_attendance_exemption = fields.Boolean('Is Exempted From Attendance',default=False)
    fingerprint_id = fields.Integer()
    staff_type = fields.Selection([
        ('suppprt', 'Support Staff'),
        ('technical','Technical Staff')
        ])

    unit_id = fields.Many2one('hr.unit',string="Unit")
    unit_name = fields.Char(related="unit_id.name", string="Unit Name", store=True)
    statistic_number = fields.Char(string="Statistic Number", tracking=True)
    donor_code = fields.Char(string="Donor Code", tracking=True)
    cost_center = fields.Char(string="Cost Center", tracking=True)
    payroll_group_id = fields.Many2one('payroll.group',string="Payroll Group")
    project_id = fields.Many2one('contract.project',string="Project")
    payment_type = fields.Selection([
        ('bank', 'Bank'),
        ('cash','Cash')
        ])
    employee_type = fields.Selection(master_data.EMPLOYEE_TYPE)
    join_date = fields.Date(
        string="Employment Date",
        groups="hr.group_hr_user",
        help="Joining Date of an employee!"
    )
    birthday = fields.Date('Date of Birth', groups="hr.group_hr_user")
    is_local = fields.Selection([
        ('local','Local'),
        ('expat', 'International'),
    ], groups="hr.group_hr_user", string="Local/International",tracking=True)
   
    
    community = fields.Selection([
        ('community', 'Community'),
        ('non_community','Non Community')
        ], string="Community/Non Community")


    idc_no = fields.Char(
        string="ID No",
        default=lambda self: _('New')
        )
    
    fingerprint_id = fields.Char("Fingerprint ID", groups="hr.group_hr_user")

    name_in_dari = fields.Char(
        string="Name in Dari",
        groups="hr.group_hr_user"
    )
    father_name_in_dari = fields.Char(string="Father Name in Dari", groups="hr.group_hr_user")
    
    bank_account = fields.Char(
        string="Bank Account Number",
        groups="hr.group_hr_user"
    )
    bank_id = fields.Many2one(
        'bank.bank',
        string="Bank Name",
        groups="hr.group_hr_user",
        
    )
    
    account_account = fields.Char(
        string="Account",
        groups="hr.group_hr_user"
    )
    
    province_id = fields.Many2one('province', string="Work Province")
    district_id = fields.Many2one('district', string="District")
    village = fields.Char(string='Village')
    office_id = fields.Many2one('office', string="Office")

    personal_province_id = fields.Many2one('province', string="Province")
    
    
    personal_mobile = fields.Char(
        string="Personal Mobile",
        groups="hr.group_hr_user"
    )
    personal_email = fields.Char(
        string="Personal Email",
        groups="hr.group_hr_user"
    )
       
    key_staff = fields.Selection([
    ('yes','Yes'),
    ('no','No')
    ], string="Key Staff", groups="hr.group_hr_user" )
    
    skype = fields.Char(
        string="Skype",
        groups="hr.group_hr_user"
    )
    tin_no = fields.Char(
        string="TIN No",
        groups="hr.group_hr_user"
    )
    blood_group_type = fields.Selection(
        blood_group_type_list,
        string="Blood Group",
        groups="hr.group_hr_user"
    )
    age = fields.Integer(
        string="Age",
        compute="calculate_age",
        groups="hr.group_hr_user",
        
    ) 
    father_name = fields.Char(
        string="Father's Name",
        groups="hr.group_hr_user"
    )
    grand_father_name = fields.Char(
        string="Grand Father's Name",
        groups="hr.group_hr_user"
    )
    mother_name = fields.Char(
        string="Mother's Name",
        groups="hr.group_hr_user"
    )
    current_address = fields.Char(
        string="Current Address",
        groups="hr.group_hr_user"
    )
    permanent_address = fields.Char(
        string="Permanent Address",
        groups="hr.group_hr_user"
    )
    passport_expiry_date = fields.Date(
        string="Passport Expiry Date",
        groups="hr.group_hr_user"
    )
    emergency_contacts_ids = fields.One2many(
        'emergency.contacts',
        'contacts',
        groups="hr.group_hr_user",
        string="Next of Kin"
    )
    references_ids = fields.One2many(
        'employee.references',
        'empl_id',
        string="References",
        groups="hr.group_hr_user"
    )

    beneficiary_ids = fields.One2many(
        'beneficiary.contacts',
        'contacts',
        string="Beneficiary Details",
        groups="hr.group_hr_user"
    )

    contact_person_ids = fields.One2many(
        'contact.person',
        'employee_id',
        string="Contact Person",
        groups="hr.group_hr_user"
    )

    completed_police_clearance = fields.Boolean(
        string="Work Permit Documents",
        groups="hr.group_hr_user,nl_master.group_hr_employee_read_only"
    )
    completed_pikaz_clearance = fields.Boolean(
        string="Medical Checkup Documents",
        groups="hr.group_hr_user,nl_master.group_hr_employee_read_only"
    )
    police_clearance_ids = fields.One2many(
        'completed.police.clearance',
        'police_id',
        string="Work Permit Documents",
        groups="hr.group_hr_user,nl_master.group_hr_employee_read_only"
    )
    pikaz_clearance_ids = fields.One2many(
        'completed.pikaz.clearance',
        'pikaz_id',
        string="Medical Checkup Documents",
        groups="hr.group_hr_user,nl_master.group_hr_employee_read_only"
    )
    doc_ids = fields.One2many(
        'employee.document', 'emp_id',
        string="Documents",
        groups="hr.group_hr_user,nl_master.group_hr_employee_read_only"
    )
    blacklisted = fields.Boolean(
        string="Blacklisted",
        groups="hr.group_hr_user,nl_master.group_hr_employee_read_only"
    )

    # education_level = fields.Char(compute='compute_education_level',store=True)
    edu_level = fields.Char()
    education_level = fields.Selection(master_data.EMPLOYEE_EDUCATION_LEVEL ,string="Education Level")
    
    education_name = fields.Char(string="Education Name")
    education_start_date = fields.Date(string="Start Date")
    education_end_date = fields.Date(string="End Date")
    education_institution = fields.Char(string="Institution")

    employee_salary = fields.Float(string="Latest Salary")
    employee_grade = fields.Char(string="Latest Grade")
    employee_step = fields.Char(string="Latest Step")

    last_promotion_date = fields.Date(string="Last Promotion/Increment Date")
    previous_grade = fields.Char(string="Previous Grade")
    previous_step = fields.Char(string="Previous Step")
    previous_salary = fields.Float(string="Previous Salary")

    employee_language = fields.Char(string="Languages")
    id_received_date = fields.Date('ID Received Date')
    is_illiterate = fields.Boolean('Is Illiterate')
    illiteracy_value = fields.Char('Education Level')
    is_returnee = fields.Boolean(string="Returnee")
    rejoin_date = fields.Date(string="Rejoining Date")


    active = fields.Boolean('Active', related='resource_id.active', default=True, store=True, readonly=False,tracking=True)
    color = fields.Integer('Color Index', default=0, groups="hr.group_hr_user,nl_appraisal.group_appraisee")
    employment_type = fields.Selection(master_data.EMPLOYEMENT_TYPE, compute="_compute_employment_type")
    employee_leave_balance_ids = fields.One2many('employee.leave.balance', 'employee_id', string='')
    contracts_count = fields.Integer(compute='_compute_contracts_count', string='Contract Count') 
    contract_warning = fields.Boolean(string='Contract Warning', store=True, compute='_compute_contract_warning', groups="hr.group_hr_user,nl_master.group_hr_employee_read_only")
    first_contract_date = fields.Date(compute='_compute_first_contract_date', groups="hr.group_hr_user,nl_master.group_hr_employee_read_only")
    vehicle = fields.Char(string='Company Vehicle', groups="hr.group_hr_user,nl_master.group_hr_employee_read_only")
    barcode = fields.Char(string="Badge ID", help="ID used for employee identification.", groups="hr.group_hr_user,nl_master.group_hr_employee_read_only", copy=False)
    payslip_count = fields.Integer(compute='_compute_payslip_count', string='Payslip Count', groups="hr_payroll.group_hr_payroll_user,nl_master.group_hr_employee_read_only")



    def open_hr_employee_checklist(self):
        return {
                'name': _('Employee Checklist'),
                'type': 'ir.actions.act_window',
                'res_model': 'hr.employee',
                'view_id' : self.env.ref('nl_employee.view_employee_checklist_form').id,
                'view_mode': 'form',
                'res_id': self.id
                
            }

    def open_hr_employee_personal_checklist(self):
        return {
                'name': _('Employee Personal Checklist'),
                'type': 'ir.actions.act_window',
                'res_model': 'hr.employee',
                'view_id' : self.env.ref('nl_employee.view_employee_personal_checklist_form').id,
                'view_mode': 'form',
                'res_id': self.id
                
            }

    @api.depends('contract_id')
    def _compute_employment_type(self):
        for rec in self:
            if rec.contract_id:
                rec.employment_type = rec.contract_id.employment_type
            else:
                rec.employment_type = False

    def unarchive_employee(self):
        self.is_returnee = True
        self.rejoin_date = fields.Date.today()
        self.active = True
            
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        """
        this function restricts the user to create duplicate record from action menu
        """
        self.ensure_one()
        default = dict(default or {})
        if not self.env.user.has_group('base.user_admin'):
            raise UserError(_("You cannot duplicate record, contact you administrator"))
        else:
            return super(HrEmployee, self).copy(default=default)


    def cleanhtml(self,raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext


    def _sync_user(self, user, employee_has_image=False):
        vals = dict(
            work_email=user.email,
            user_id=user.id,
        )
        # if not employee_has_image:
        #     vals['image_1920'] = user.image_1920
        if user.tz:
            vals['tz'] = user.tz
        return vals

    @api.onchange('job_id')
    def _onchange_job_id(self):
        # super(HrEmployee, self)._onchange_job_id()
        self.job_title = None
        if self.job_id:
            self.job_title = self.job_id.name

    @api.onchange('is_illiterate')
    def onchange_is_illiterate(self):
        self.ensure_one()
        self.illiteracy_value = 'Illiterate'

    # @api.onchange('personal_province_id','district_id')
    # def _set_permanent_address(self):
    #     address = ''
    #     if not self.permanent_address:
    #         if self.personal_province_id:
    #             address = self.personal_province_id.name + ', ' + self.district_id.name
    #         if self.district_id:
    #             address = self.personal_province_id.name + ', ' + self.district_id.name

    #         self.permanent_address = address



    @api.onchange('parent_id')
    def set_manager_as_time_off(self):
        for item in self:
            if item.parent_id and item.parent_id.user_id:
                item.leave_manager_id = item.parent_id.user_id.id
            else:
                return False

    @api.onchange('province_id')
    def get_province_districts(self):
        related_districts = []
        districts_ids = self.env['district'].search([('province_id','=',self.province_id.id)])
        for item in districts_ids:
            related_districts.append(item.id)

        return {'domain': {'district_id': [('id', 'in', related_districts)]}}
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        # Override method to disable create and Edit button for Employe profile
        res = super(HrEmployee, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        hr_manager_group = self.env.user.has_group('hr.group_hr_manager')
        hr_user_group = self.env.user.has_group('hr.group_hr_user')
        doc = etree.XML(res['arch'])
        if not hr_manager_group and not hr_user_group:
            # Disable create and edit button for user group user!
            if view_type == 'tree':
                nodes = doc.xpath("//tree")
                for node in nodes:
                    node.set('create', 'false')
                    node.set('edit', 'false')
                res['arch'] = etree.tostring(doc)
            if view_type == 'form':
                nodes = doc.xpath("//form")
                for node in nodes:
                    node.set('create', 'false')
                    node.set('edit', 'false')
                res['arch'] = etree.tostring(doc)
            if view_type == 'kanban':
                nodes = doc.xpath("//kanban")
                for node in nodes:
                    node.set('create', 'false')
                res['arch'] = etree.tostring(doc)
        res['arch'] = etree.tostring(doc)
        return res

    def get_random_string(self,length):
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str

    
   

    def organize_employee_data_for_email(self, emp_list):
        employee_data = {}
        dummy_id = 5555
        for employee in emp_list:
            if employee.department_id and employee.department_id.id:
                if employee.department_id.id in employee_data.keys():
                    employee_data[employee.department_id.id].append((employee.department_id.name,employee.name))
                else:
                    employee_data[employee.department_id.id] = [(employee.department_id.name,employee.name)]
            else: 
                if dummy_id in employee_data.keys():
                    employee_data[dummy_id].append(('Others',employee.name))
                else:
                    employee_data[dummy_id] = [('Others',employee.name)]

        mini_para  = ''
        for key, datas in employee_data.items():
            dep_group = ''
            flag = True
            for data in datas:
                if flag:
                    dep_group = '<strong>' + data[0] + ':</strong>\n'
                    flag = False
                dep_group += '  - ' + data[1] + '\n'
            dep_group += '\n'
            mini_para += dep_group

        return mini_para

    def send_no_timesheet_reminder_email(self, employee, template, mail_from, emp_with_no_ts_data=False, to_ceo=False):

        return print("Not applicable")
    
    def _get_contracts_extended(self, office,payslip_run_id,master_batch_id,date_from, date_to, states=['open','in_separation'], kanban_state=False):
        """
        Returns the contracts of the employee between date_from and date_to
        """
        state_domain = [('state', 'in', states),('wage','>',0)]
        if kanban_state:
            state_domain = expression.AND([state_domain, [('kanban_state', 'in', kanban_state)]])

        contracts =  self.env['hr.contract'].sudo().search(
            expression.AND([[('employee_id', 'in', self.ids)],
            state_domain,
            [('date_start', '<=', date_to),
                '|',
                    ('date_end', '=', False),
                    ('date_end', '>=', date_from)]]))
        
        not_applicable_employees = self.env['hr.employee'].sudo().search([('contract_id', 'not in', contracts.ids),('office_id', '=', office)])
        for employee in not_applicable_employees:
            self.env['employees.pending'].create({
                    'employee_id':employee.id,
                    'master_batch_id':master_batch_id,
                    'payslip_run_id':payslip_run_id
                    })
        return contracts
      


    def name_get(self):
        result = []
        for employee in self:
            if employee.idc_no == 'New' or not employee.idc_no:
                name = employee.name
                result.append((employee.id,name))
            else:
                name = employee.idc_no + ' | ' + employee.name
                result.append((employee.id,name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('idc_no', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)

    def print_employment_certificate(self):
        action = self.env["ir.actions.actions"]._for_xml_id("nl_employee.action_employment_certificate_signatory_wizard")
        action.update({
            'context': {'default_employee_id':self.id}
        })
        return action
       
    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('employee.id_card')
        vals['idc_no'] = sequence or _('New')
        permanent_address = []
        if not vals.get('permanent_address', False):
            if vals.get('personal_province_id', False):
                province_id = self.env['province'].search([('id','=',vals['personal_province_id'])])
                permanent_address.append(province_id.name)
            if vals.get('district_id', False):
                district = self.env['district'].search([('id','=',vals['district_id'])])
                permanent_address.append(district.name)
            if vals.get('village', False):
                permanent_address.append(vals['village'])
            vals['permanent_address'] = ', '.join([item for item in permanent_address])
        res = super(ExtendedEmployee, self).create(vals)
        return res

ExtendedEmployee.create = HrEmployee.create
    

class Language(models.Model):
    _name = 'language.language'
    _description = 'Language'

    name = fields.Char(
        string="Name"
    )
    code = fields.Char(
        string="Code"
    )


class EmergencyContacts(models.Model):
    _name = 'emergency.contacts'
    _description = 'Emergency Contacts'

    name = fields.Char(
        string="Name"
    )
    relationship = fields.Char(
        string="Relationship"
    )
    number = fields.Char(
        string="Number"
    )
    address = fields.Char("Address")
    tazkira_number = fields.Char("Tazkira Number")
    contacts = fields.Many2one(
        'hr.employee',
        string="Ref."
    )
    description = fields.Char(string="Remarks")

class BeneficiaryDetails(models.Model):
    _name = 'beneficiary.contacts'
    _description = 'Emergency Beneficiary Details'

    name = fields.Char(
        string="Name"
    )
    relationship = fields.Char(
        string="Relationship"
    )
    tazkira_number = fields.Char("Tazkira No")

    number = fields.Char(
        string="Number"
    )
    contacts = fields.Many2one(
        'hr.employee',
        string="Ref."
    )
    address = fields.Char("Address")




class References(models.Model):
    _name = 'employee.references'
    _inherit = ['mail.thread','mail.activity.mixin','resource.mixin']
    _description = 'Reference'

    name = fields.Char( 
        string="Reference Name"
    )
    job_title = fields.Char(
        string="Job Title"
    )
    organization = fields.Char(
        string="Organization"
    )
    contact_number = fields.Char(
        string="Contact Number"
    )
    email = fields.Char(
        string="Email Address"
    )
    checked = fields.Boolean(
        string="Checked",
    )

    confirm = fields.Boolean(
        string="Confirmed by Referee"
    )

    empl_id = fields.Many2one(
        'hr.employee',
        string="Ref."
    )
    reference_document = fields.Binary('Document')

    applicant_id = fields.Many2one('hr.applicant')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('done', 'Done'),
    ], string='Status', default='draft', copy=False)


    @api.constrains('checked')
    def track_checked_uncheck(self):
        for rec in self:
            context = dict(self._context) or {}
            if rec.create_date != rec.write_date or rec.checked:            
                old_string = "un-checked"
                new_string = "checked"
                if not rec.checked:
                    old_string = "checked"
                    new_string = "un-checked"
                if rec.applicant_id:
                    try: 
                        rec.applicant_id.message_post(
                                body=_('Reference: %s:  %s -> %s') % (rec.name, old_string, new_string),
                                subtype_xmlid="nl_employee.mt_applicant_reference")
                    except:
                        pass

                if rec.empl_id:
                    try: 
                        rec.empl_id.message_post(
                                body=_('Reference: %s:  %s -> %s') % (rec.name, old_string, new_string),
                                subtype_xmlid="nl_employee.mt_employee_reference")
                    except:
                        pass
                    
    
    # Referee inputs
    candidate_capacity = fields.Char(
    "How long have you known the candidate professionally and in what capacity? ")
    key_responsibilities = fields.Char(
    "When did the candidate work for your organization and what were his key responsibilities?")
    candidate_performance = fields.Char(
    "Overall, how would you rate the candidate’s performance in those key areas?")
    improvement_areas = fields.Char(
    "Please identify any specific areas that proved challenging to the candidate and/or where he could have improved upon in this role? ")
    good_terms = fields.Boolean(
    "Did the candidate leave your organization on good terms?")
    candidate_rehiring = fields.Boolean(
    "Would you re-hire the candidate for a similar position in your organization?")

    team_work_rating = fields.Selection([
    ('excellent', 'Excellent'),
    ('good', 'Good'),
    ('fair', 'Fair'),
    ('poor', 'Poor')], string="Teamwork and ability to work with and build relationships with others.")

    candidate_punctuality = fields.Selection([
    ('excellent', 'Excellent'),
    ('good', 'Good'),
    ('fair', 'Fair'),
    ('poor', 'Poor')], string="Punctuality, timeliness of work, and ability to meet deadlines.")

    work_quality = fields.Selection([
    ('excellent', 'Excellent'),
    ('good', 'Good'),
    ('fair', 'Fair'),
    ('poor', 'Poor')], string="Quality of work.")

    multi_tasking = fields.Selection([
    ('excellent', 'Excellent'),
    ('good', 'Good'),
    ('fair', 'Fair'),
    ('poor', 'Poor')], string="Multi-tasking and ability to effectively handle several assignments at once.")


    employee_self_sufficincies = fields.Selection([
    ('excellent', 'Excellent'),
    ('good', 'Good'),
    ('fair', 'Fair'),
    ('poor', 'Poor')], string="Self-sufficiency in seeing things through on project tasks or assignments.")


    other_skills = fields.Selection([
    ('excellent', 'Excellent'),
    ('good', 'Good'),
    ('fair', 'Fair'),
    ('poor', 'Poor')], string="•	How would you rate capabilities in Microsoft Excel, Microsoft Word, and database information entry and retrieval?")


    further_reservations = fields.Selection([
    ('no_reservation', 'No Reservation'),
    ('some_reservation', 'Some Reservation'),
    ('not_approperiate', 'Would Not Be Approperiate for that position')], string="If you were in a position to hire Miss. Maryam Farzami would you have any reservations about placing Name in this role?")


    comments_explanation = fields.Char(
    "Comments / Explanation")
 
    def get_random_string(self,length):
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str

    
    #authentication
    token = fields.Char("token")


    def send_email_to_reference(self):
        for record in self:
            self.mail_reference_check(record)


    def mail_reference_check(self,record):
        user = self.env['res.users']
        from_mail = user.browse(self._uid) and user.login or ''
        from_mail = from_mail.encode('utf-8')
        to_mail = (record.email).encode('utf-8')

        email_template = False
        message = ""

        token = self.get_random_string(12)
        
        record.update({
            'token': token,
            'state': 'sent'
        })

        if record.applicant_id:
            report_template_id = self.env.ref(
                'nl_recruitment.action_print_applicant_reference_check').with_context(model='hr.applicant')._render_qweb_pdf(record.id)
            data_record = base64.b64encode(report_template_id[0])
            ir_values = {
                    'name': "Reference Check",
                    'type': 'binary',
                    'datas': data_record,
                    'store_fname': data_record,
                    'mimetype': 'application/pdf',
                }
            data_id = self.env['ir.attachment'].create(ir_values)
            email_template = self.env.ref(
                    'nl_recruitment.email_applicant_reference_check')
        
            body_html = """
                        <![CDATA[<div style="font-family: 'Lucica Grande',
                        Ubuntu, Arial, Verdana, sans-serif; font-size: 14px;
                        color: rgb(34, 34, 34); background-color: #FFF; ">
                        <p>Dear """ + record.name + """,</p>
                        <br/>
                        <p>We are considering the application of <b>"""+record.applicant_id.name+"""</b> for the position of <b>""" + record.applicant_id.job_id.name + """</b> with <b>""" + record.applicant_id.company_id.name + """</b> who has given your detail as reference. We would be grateful if you could verify and answer the questions in the attached reference check form and send us the signed and stamped scanned copy at your earliest convenience. </p>

                        </br>

                        <p>Please be confident that any information you provide will be kept strictly confidential.
                        <br/>
                        <br/>
                        Thank you for your cooperation.
                        <br/>
                        <p>Human Resource Management<br/>
                        <br/>
                        <img src="/logo.png?company="""+str(self.env.user.company_id.id)+""" "  style="padding: 0px; margin: 0px; height: auto; width: 150px;" alt=" """+self.env.user.company_id.name+""" "/>
                        </p>
                    """
            if email_template:
                email_template.attachment_ids = [(6, 0, [data_id.id])]
                email_template.sudo().write({
                    'subject': 'Reference Check for ' + record.applicant_id.name,
                    'body_html': body_html,
                    'email_from': from_mail,
                    'email_to': to_mail
                })
                email_template.send_mail(record.applicant_id.id, force_send=True)
                email_template.attachment_ids = [(3, data_id.id)]

        if not record.applicant_id:
            report_template_id = self.env.ref(
                'nl_recruitment.action_print_applicant_reference_check').with_context(model='hr.employee')._render_qweb_pdf(record.id)
            data_record = base64.b64encode(report_template_id[0])
            ir_values = {
                    'name': "Reference Check",
                    'type': 'binary',
                    'datas': data_record,
                    'store_fname': data_record,
                    'mimetype': 'application/pdf',
                }
            data_id = self.env['ir.attachment'].create(ir_values)
            email_template = self.env.ref(
                    'nl_employee.reference_mail_check')
        
            body_html = """
                        <![CDATA[<div style="font-family: 'Lucica Grande',
                        Ubuntu, Arial, Verdana, sans-serif; font-size: 14px;
                        color: rgb(34, 34, 34); background-color: #FFF; ">
                        <p>Dear """ + record.name + """,</p>
                        <br/>
                        <p>We are considering the application of <b>"""+record.empl_id.name+"""</b> for the position of <b>""" + record.empl_id.job_id.name + """</b> with <b>""" + record.empl_id.company_id.name + """</b> who has given your detail as reference. We would be grateful if you could verify and answer the questions in the attached reference check form and send us the signed and stamped scanned copy at your earliest convenience. </p>

                        </br>

                        <p>Please be confident that any information you provide will be kept strictly confidential.
                        <br/>
                        <br/>
                        Thank you for your cooperation.
                        <br/>
                        <p>Human Resource Management<br/>
                        <br/>
                        <img src="/logo.png?company="""+str(self.env.user.company_id.id)+""" "  style="padding: 0px; margin: 0px; height: auto; width: 150px;" alt=" """+self.env.user.company_id.name+""" "/>
                        </p>
                    """
            if email_template:
                email_template.attachment_ids = [(6, 0, [data_id.id])]
                email_template.sudo().write({
                    'subject': 'Reference Check for ' + record.empl_id.name,
                    'body_html': body_html,
                    'email_from': from_mail,
                    'email_to': to_mail
                })
                email_template.send_mail(record.empl_id.id, force_send=True)
                email_template.attachment_ids = [(3, data_id.id)]
    

class CompletedPoliceClearance(models.Model):
    _name = 'completed.police.clearance'
    _description = 'Work Permit'

    name = fields.Binary(
        string='Document'
    )
    file_name = fields.Char(
        string='File name'
    )
    police_id = fields.Many2one(
        'hr.employee'
    )


class CompletedPikazClearance(models.Model):
    _name = 'completed.pikaz.clearance'
    _description = 'Medical Checkup'
    _rec_name = "type"

    type = fields.Text(string="Medical Type", required=True)

    name = fields.Binary(
        string='Document',
    )
    file_name = fields.Char(
        string='File name'
    )
    pikaz_id = fields.Many2one(
        'hr.employee'
    )
    checked = fields.Boolean(
        string="Checked"
    )
    applicant_id = fields.Many2one('hr.applicant')


    @api.constrains('checked')
    def track_checked_uncheck(self):
        for rec in self:
            context = dict(self._context) or {}
            if rec.create_date != rec.write_date:            
                old_string = "un-checked"
                new_string = "checked"
                if not rec.checked:
                    old_string = "checked"
                    new_string = "un-checked"
                
                if rec.applicant_id:
                    try: 
                        rec.applicant_id.message_post(
                                body=_('Medical: %s:  %s -> %s') % (rec.type, old_string, new_string),
                                subtype_xmlid="nl_employee.mt_applicant_medical")
                    except:
                        pass
                if rec.pikaz_id:

                    try: 
                        rec.pikaz_id.message_post(
                                body=_('Medical: %s:  %s -> %s') % (rec.type, old_string, new_string),
                                subtype_xmlid="nl_employee.mt_employee_medical")
                    except:
                        pass

class EmployeeDocument(models.Model):
    _name = 'employee.document'
    _description = 'Employee Document'

    name = fields.Binary(
        string='Document'
    )
    file_name = fields.Char(
        string='Document name'
    )
    emp_id = fields.Many2one(
        'hr.employee'
    )

class Province(models.Model):
    _name = 'province'
    
    name = fields.Char("Province Name")
    name_in_dari = fields.Char('نام ولایت')


class PayrollGroup(models.Model):
    _name = 'payroll.group'
    _description = 'Payroll Group'

    name = fields.Char(
        string='Name', required=True
    )
    office_id = fields.Many2one('office', string='Office', required=True, )


   

class Office(models.Model):
    _name = 'office'

    name = fields.Char('Office Name')
    name_in_dari = fields.Char('نام دفتر')
    code = fields.Char()
    active = fields.Boolean(default=True)
    

class Districts(models.Model):
    _name = 'district'

    name = fields.Char('Dsictrict Name')
    province_id = fields.Many2one('province')
    name_in_dari = fields.Char('نام ولسوالی')

class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    work_location = fields.Char('Work Location')
    job_id = fields.Many2one('hr.job', 'Designation', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")


    def write(self, values):
        if 'parent_id' in values:
            manager = self.env['hr.employee'].browse(values['parent_id']).user_id
            if manager:
                to_change = self.filtered(lambda e: e.leave_manager_id == e.parent_id.user_id or not e.leave_manager_id)
                to_change.write({'leave_manager_id': values.get('leave_manager_id', manager.id)})

        old_managers = self.env['res.users']
        # if 'leave_manager_id' in values:
        #     old_managers = self.mapped('leave_manager_id')
        #     if values['leave_manager_id']:
        #         old_managers -= self.env['res.users'].browse(values['leave_manager_id'])
        #         approver_group = self.env.ref('hr_holidays.group_hr_holidays_responsible', raise_if_not_found=False)
        #         if approver_group:
        #             approver_group.sudo().write({'users': [(4, values['leave_manager_id'])]})

        res = super(HrEmployeeBaseExtended, self).write(values)
        # remove users from the Responsible group if they are no longer leave managers
        old_managers._clean_leave_responsible_users()

        if 'parent_id' in values or 'department_id' in values:
            today_date = fields.Datetime.now()
            hr_vals = {}
            if values.get('parent_id') is not None:
                hr_vals['manager_id'] = values['parent_id']
            if values.get('department_id') is not None:
                hr_vals['department_id'] = values['department_id']
            holidays = self.env['hr.leave'].sudo().search(['|', ('state', 'in', ['draft', 'confirm']), ('date_from', '>', today_date), ('employee_id', 'in', self.ids)])
            holidays.write(hr_vals)
            allocations = self.env['hr.leave.allocation'].sudo().search([('state', 'in', ['draft', 'confirm']), ('employee_id', 'in', self.ids)])
            allocations.write(hr_vals)
        return res

HrEmployeeBaseExtended.write = HrEmployeeBase.write
    

class BankBank(models.Model):
    _name = 'bank.bank'
    _description = 'Bank'

    name = fields.Char('Bank Name')
    bank_address = fields.Char('Bank Address')
    bank_city = fields.Char('Province')

class EmployeeLeaveBalance(models.Model):
    _name = "employee.leave.balance"

    employee_id = fields.Many2one('hr.employee', 'Employee')
    emp_no = fields.Char(related="employee_id.idc_no", store=True)
    unit_id = fields.Many2one('hr.unit', string='Unit', related="employee_id.unit_id", store=True)
    department_id = fields.Many2one('hr.department', string='Department', related="employee_id.department_id", store=True)
    office_id = fields.Many2one('office',related='employee_id.office_id', string='Office',)
    job_id = fields.Many2one('hr.job', string='Job Position', related="employee_id.job_id", store=True)
    total_allocation = fields.Float('Allocation',)
    total_leave = fields.Float('Leaves Taken',)
    total_balance = fields.Float('Balance',)
    leave_type = fields.Many2one('hr.leave.type')
    util_percentage = fields.Float('Percentage', compute="_get_leave_utilization_percentage")

    
    def _get_leave_utilization_percentage(self):
        self.util_percentage = 0.0
        for item in self:
            percentage = 0.0
            if item.total_leave and item.total_allocation:
                percentage = item.total_leave / item.total_allocation
            item.util_percentage = percentage
            
    def update_dictionary_values_time_off(self,dictionary):
        num_dict = {}
        for t in dictionary:
            if t[0] in num_dict:
                num_dict[t[0]] = num_dict[t[0]]+t[1]
            else:
                num_dict[t[0]] = t[1]
        return num_dict

    @api.model
    def action_time_off_balance_extended(self):
        employee_id = self.env['hr.employee'].sudo().search([('id','=',self.env.context.get('active_id'))])
        employee_id.employee_leave_balance_ids.unlink()
        allocations = []
        leaves = []
        leave_allocation_ids = self.env['hr.leave.allocation'].sudo().search([('date_from','ilike',datetime.now().year),('employee_id','=',employee_id.id), ('state', '=', 'validate')])
        leave_ids = self.env['hr.leave'].sudo().search([('date_from','ilike',datetime.now().year),('employee_id','=',employee_id.id), ('state', '=', 'validate')])
        for item in leave_allocation_ids:
            allocations.append([item.holiday_status_id.id,item.number_of_days])
        allocations = self.update_dictionary_values_time_off(allocations)
        employee_leave_balance = self.env['employee.leave.balance']
        for key,value in allocations.items():
            if value > 0:
                line = employee_leave_balance.sudo().create({
                    'employee_id':self.env.context.get('active_id'),
                    'total_allocation':value,
                    'leave_type':key,
                    'total_balance': value
                })
        for item in leave_ids:
            leaves.append([item.holiday_status_id.id,item.number_of_days])
        leaves = self.update_dictionary_values_time_off(leaves)
        for key,value in leaves.items():
            if value > 0:
                for item in employee_leave_balance.sudo().search([('employee_id','=',employee_id.id)]):
                    if key == item.leave_type.id:
                        line = item.write({
                            'employee_id':employee_id.id,
                            'total_leave':value,
                            'leave_type':key,
                            'total_balance':item.total_allocation - value
                           
                        })
        if self.env.context.get('active_model') == 'hr.employee':
            return {
                'name': _('Time Off Balances'),
                'type': 'ir.actions.act_window',
                'res_model': 'employee.leave.balance',
                'view_id' : self.env.ref('nl_employee.hr_leave_balance_tree').id,
                'view_mode': 'tree',
                'domain':[('employee_id','=',self.env.context.get('active_id'))]
                
            }
        else:
            return {
                'name': _('Time Off Balances'),
                'type': 'ir.actions.act_window',
                'res_model': 'employee.leave.balance',
                'view_mode': 'tree',
                'context': {
                    'search_default_group_employee': True,
                }   
            }


    @api.model
    def action_time_off_balance_extended_all(self):
        context = dict(self._context) or {}

        self._cr.execute(""" 
            DELETE  FROM employee_leave_balance
         """)
        self._cr.commit()
        
        employee_ids = self.env['hr.employee'].sudo().search([('active','=',True)])

        for employee_id in employee_ids:
            
            
            allocations = []
            leaves = []
            if context.get("not_return_view", False):
                leave_allocation_ids = self.env['hr.leave.allocation'].sudo().search([('date_from','ilike',datetime.now().year-1),('employee_id','=',employee_id.id), ('state', '=', 'validate')])
                leave_ids = self.env['hr.leave'].sudo().search([('date_from','ilike',datetime.now().year-1),('employee_id','=',employee_id.id), ('state', '=', 'validate')])
            else:
                leave_allocation_ids = self.env['hr.leave.allocation'].sudo().search([('date_from','ilike',datetime.now().year),('employee_id','=',employee_id.id), ('state', '=', 'validate')])
                leave_ids = self.env['hr.leave'].sudo().search([('date_from','ilike',datetime.now().year),('employee_id','=',employee_id.id), ('state', '=', 'validate')])
            for item in leave_allocation_ids:
                allocations.append([item.holiday_status_id.id,item.number_of_days])
            allocations = self.update_dictionary_values_time_off(allocations)
            employee_leave_balance = self.env['employee.leave.balance']
            for key,value in allocations.items():
                if value > 0:
                    line = employee_leave_balance.sudo().create({
                        'employee_id':employee_id.id,
                        'total_allocation':value,
                        'leave_type':key,
                        'total_balance': value
                    })
            for item in leave_ids:
                leaves.append([item.holiday_status_id.id,item.number_of_days])
            leaves = self.update_dictionary_values_time_off(leaves)
            for key,value in leaves.items():
                if value > 0:
                    for item in employee_leave_balance.sudo().search([('employee_id','=',employee_id.id)]):
                        if key == item.leave_type.id:
                            line = item.write({
                                'employee_id':employee_id.id,
                                'total_leave':value,
                                'leave_type':key,
                                'total_balance':item.total_allocation - value
                            
                            })
        if context.get("not_return_view", False):
            return
            
        return {
            'name': _('Time Off Balances'),
            'type': 'ir.actions.act_window',
            'res_model': 'employee.leave.balance',
            'view_mode': 'tree',
            'context': {
                'search_default_group_employee': True,
            }
        }
