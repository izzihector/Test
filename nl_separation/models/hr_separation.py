# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
import random
import string

import re

class HrSeparation(models.Model):
    _name = 'hr.separation'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']
    _description = 'HR Separation'
    _rec_name = 'employee_id'

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    def copy(self, default=None):
        for rec in self:
            raise UserError(_('You can not duplicate a Separation Request!'))
        return super(HrSeparation, self).copy(default=default)

    @api.onchange('notice_period')
    def _cal_resign_date(self):
        # This method calculates the last date based on the notice period.
        for sep_rec in self:
            if sep_rec.resign_date:
                r_date = sep_rec.resign_date
                l_date = r_date + relativedelta(days=sep_rec.notice_period)
                sep_rec.relieve_date = l_date.strftime(
                    DEFAULT_SERVER_DATE_FORMAT)
                sep_rec.notice_period = sep_rec.notice_period
            if sep_rec.notice_period < 0:
                raise ValidationError(_("The employment end date shall not be earlier than the notice "))

    @api.onchange('relieve_date')
    def _cal_relieve_date(self):
        for rel_rec in self:
            if rel_rec.relieve_date and rel_rec.resign_date:
                rel_date = rel_rec.relieve_date
                r_date = rel_rec.resign_date
                total_notice_period = relativedelta(rel_date, r_date)

                if total_notice_period:
                    rel_rec.notice_period = total_notice_period.days

    name = fields.Char(
        string='Name',
        readonly=True
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        help="A employee information"
    )

    father_name = fields.Char(
        string="Father Name",
        related='employee_id.father_name',
    )
    job_id = fields.Many2one(
        'hr.job',
        string='Designation',
        related='employee_id.job_id',
        help="This would be display job information for employee"
    )
    gender = fields.Selection(
        string='Gender',
        related='employee_id.gender',
        help="A employee information"
    )
    unit_id = fields.Many2one(
        'hr.unit',
        string='Unit',
        related='employee_id.unit_id',
        help="A employee Unit"
    )
    project_id = fields.Many2one(
        'contract.project',
        related='employee_id.project_id',
        string='Project',
        help="A employee Unit"
    )
    
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        help="A employee department details",
        store=True
    )
    office_id = fields.Many2one(
        'office',
        string='Office',
        related='employee_id.office_id',
        store = True,
        help="A employee Office details"
    )
    join_date = fields.Date(
        string='Employment Start Date',
        related='employee_id.join_date',
        help="A join date of employee"
    )
    relieve_date = fields.Date(
        string='Employment End Date',
        help="A relive date of employee"
    )
    # separation_type = fields.Selection([
    #     ('resignation', 'Resignation'),
    #     ('redundant', 'Redundant'),
    #     ('retirement', 'Retirement'),
    #     ('end_of_contract', 'End of Contract'),
    #     ('termination', 'Dismissal'),
    #     ('death', 'Death'),
    #     ('foreshorten', 'Contract Foreshorten'),
        
    # ])
    employment_separation_type = fields.Many2one('hr.separation.type',string="Separation Type")
    manager_id = fields.Many2one(
        'hr.employee',
        string='Manager',
        related='employee_id.parent_id',
        help="A manager would be configure as per employee"
    )
    resign_date = fields.Date(
        string='Notice Date',
        help="A employee resign date"
    )
    notice_period = fields.Integer(
        string='Notice Period (Days)',
        help="A notice period of employee",
        
    )
    reason = fields.Text(
        string='Reason',
        help="A reason of employee separation"
    )
    
    payslip_paid = fields.Boolean(
        string='Payslip Paid',
        help="A payslip paid or not"
    )
    state = fields.Selection([
        ('draft', 'New'),
        ('in_progress', 'In Progress'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', group_expand='_expand_states', copy=False)

    unit_head_comments = fields.Text()
   
    office_keys = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Office Keys")
    book_files_reference = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Book, Files and Reference")
    signature_of_supervisor = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Signature of Supervisor/HoD ensuring departmental clearance")
    office_key_returned = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Office Key Returned")
    mobile_phone_and_sim_card_returned = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Mobile Phone and Sim Card Returned")
    mobile_returned = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Mobile Phone Returned")
    local_advance_cleared = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Telephone and Bill Cleared")
    telephone_and_bill_cleared = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Telephone and Bill Cleared")
    other_equipment = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Other Equipment")
    training_cost = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Local Advance Cleared")
    personal_telephone_bills_cleared = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Personal Telephone Bills Cleared")
    guest_house_accommodation_bills_cleared = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Guest House Accommodation Bills Cleared")
    any_other_entitlement_withheld = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Any Other Entitlement Withheld")
    payroll_entitlement_paid = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Payroll Entitlement Paid")

    email_revoked = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Email Revoked?")

    all_code_revoked = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="All Code Revoked")
    domain_user_disabled_renamed_ip_phone_data_backup_complete = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Domain User Disabled / Renamed IP Phone, Data Backup Complete")
    access_suspension_from_doors_and_laptop_returned = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Access Suspension from Doors and Laptop Returned")
    training_cost = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Final Entitlements Including Salary")
    fee = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Attendance and Leave Certified")
    id_card_returned = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="ID Card Returned")
    leave_balance = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Final Evaluation")
    exit_interview_form_filled = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Exit Interview Form Filled")
    payroll_related_actions_if_any = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Payroll Related Actions If Any")
    
    blacklisted = fields.Boolean(
        string="‘Blacklisted’"
    )
    project_unit_remark = fields.Text(
        string="Project unit Remark"
    )
    administrative_remark = fields.Text(
        string="Administrative Remark"
    )
    finance_remark = fields.Text(
        string="Finance Remark"
    )
    it_unit_remark = fields.Text(
        string="It Unit Remark"
    )
    procurement_supply = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Procurement and Supply")
    procurement_remark = fields.Text(
        string="Procurement Remark"
    )
    inventory_incharge = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Inventory In Charge")
    inventory_remark = fields.Text(
        string="Inventory Remark"
    )
    library_clearance = fields.Selection([
        ('cleared', "Cleared"),
        ('na', "N/A")
    ], string="Library")
    library_remark = fields.Text(
        string="Library Remark"
    )
    hr_remark = fields.Text(
        string="Hr Remark"
    )



    clearance_done = fields.Boolean("clearance done", compute="_check_if_clearance_is_done")

    is_calculated_in_payslip = fields.Boolean("", default=False)

    finance_clearance = fields.Boolean("finance clearance")
    administrative_clearance = fields.Boolean("administrative clearence")
    it_clearance = fields.Boolean("it clearence")
    project_unit_clearnce = fields.Boolean("project unit clearnce")
    hr_clearance = fields.Boolean("hr clearance")
    supervisor_clearance = fields.Boolean("Supervisor/Unit clearance")
    procurement_clearance = fields.Boolean("Procurement clearance")
    hr_inventory_clearance = fields.Boolean("Inventory clearance")
    hr_library_clearance = fields.Boolean("Library clearance")
    is_separated = fields.Boolean(string="Is Separated")


    exit_interview_form_id = fields.Many2one('exit.interview.form', string="Exit Interview")

    @api.constrains('employee_id', 'state')
    def _check_current_contract(self):
        """ Two Separation in state [draft | in progress] cannot overlap """
        for separation in self.filtered(lambda c: c.state in ['draft', 'in_progress'] or c.state == 'draft'):
            domain = [
                ('id', '!=', separation.id),
                ('employee_id', '=', separation.employee_id.id),
                    ('state', 'in', ['draft', 'in_progress']),
            ]

            domain = expression.AND([domain])
            if self.search_count(domain):
                raise ValidationError(_('An employee can have only one separation at draft and in progress states.'))



    @api.onchange('finance_clearance','administrative_clearance','it_clearance','hr_clearance','supervisor_clearance','procurement_clearance','hr_inventory_clearance','hr_library_clearance')
    def _check_if_clearance_is_done(self):
        self.clearance_done = False
        for item in self:
            if item.finance_clearance and item.administrative_clearance and item.it_clearance and item.hr_clearance and item.supervisor_clearance and item.procurement_clearance and item.hr_inventory_clearance and item.hr_library_clearance:
                item.clearance_done = True


    def action_cancel(self):
        self.update({'state':'cancel'})

    def unlink(self):
        if self.state == 'draft':
            return super(HrSeparation, self).unlink()
        else:
             raise UserError(_('Only Draft separation record can be deleted.'))
            
    
    def _check_supervisor_confirm_clearance(self):

        self._check_if_clearance_is_done()
        self.supervisor_clearance = True
        self._check_if_clearance_is_done()

    def _check_library_confirm_clearance(self):
        info = []
        
        if not self.library_clearance:
            info.append("Library")
        if not self.library_clearance:
            raise UserError(_("The following items haven't been processed %s") % info)
        else:
            self.hr_library_clearance = True
            self._check_if_clearance_is_done()

    def _check_inventory_confirm_clearance(self):
        info = []
        
        if not self.inventory_incharge:
            info.append("Inventory In Charge")
        if not self.inventory_incharge:
            raise UserError(_("The following items haven't been processed %s") % info)
        else:
            self.hr_inventory_clearance = True
            self._check_if_clearance_is_done()

    def _check_procurement_confirm_clearance(self):
        info = []
        
        if not self.procurement_supply:
            info.append("Procurement and Supply")
        if not self.procurement_supply:
            raise UserError(_("The following items haven't been processed %s") % info)
        else:
            self.procurement_clearance = True
            self._check_if_clearance_is_done()

    def _check_hr_confirm_clearance(self):
        info = []
        
        if not self.training_cost:
            info.append("Training Cost")
        if not self.fee:
            info.append("Fee")
        if not self.id_card_returned:
            info.append("ID Card Returned")
        if not self.leave_balance:
            info.append("Leave Balance")
        if not self.exit_interview_form_filled:
            info.append("Exit Interview Form Filled")
        if not self.payroll_related_actions_if_any:
            info.append("Payroll Related Actions If Any")
        if not self.training_cost\
                or not self.fee\
                or not self.id_card_returned\
                or not self.leave_balance\
                or not self.exit_interview_form_filled\
                or not self.payroll_related_actions_if_any:
            raise UserError(_("The following items haven't been processed %s") % info)
        else:
            self.hr_clearance = True
            self._check_if_clearance_is_done()

    
    
    def _check_administrative_confirm_clearance(self):
        
        info = []
        self._check_if_clearance_is_done()
        if not self.office_key_returned:
            info.append("Office Key Returned")
        if not self.mobile_phone_and_sim_card_returned:
            info.append("Sim Card")
        if not self.mobile_returned:
            info.append("Mobile")
        if not self.telephone_and_bill_cleared:
            info.append("VHF")
        if not self.other_equipment:
            info.append("Thuraya")
        if not self.office_key_returned\
                or not self.mobile_phone_and_sim_card_returned\
                or not self.mobile_returned\
                or not self.telephone_and_bill_cleared\
                or not self.other_equipment:
                
            raise UserError(_("The following items haven't been processed %s ") % info)
        else:
            self.administrative_clearance = True
            self._check_if_clearance_is_done()


    def _check_it_confirm_clearance(self):
        
        info = []
        self._check_if_clearance_is_done()
        if not self.email_revoked:
            info.append("Laptop")
        if not self.all_code_revoked:
            info.append("Hard Disk(s) / Flash")
        if not self.domain_user_disabled_renamed_ip_phone_data_backup_complete:
            info.append("Camera")
        if not self.access_suspension_from_doors_and_laptop_returned:
            info.append("Email and Electronic Data")
        
        if not self.email_revoked\
                or not self.all_code_revoked\
                or not self.domain_user_disabled_renamed_ip_phone_data_backup_complete\
                or not self.access_suspension_from_doors_and_laptop_returned:
            raise UserError(_("The following items haven't been processed %s") % info)
        else:
            self.it_clearance = True
            self._check_if_clearance_is_done()

    def _check_finance_clearnce(self):
        info = []

        self._check_if_clearance_is_done()

        if not self.local_advance_cleared:
            info.append("Last Salary")
        if not self.personal_telephone_bills_cleared:
            info.append("Last Pension")
        if not self.guest_house_accommodation_bills_cleared:
            info.append("Loan ")
        if not self.any_other_entitlement_withheld:
            info.append("Any Other Entitlement Withheld")
        if not self.payroll_entitlement_paid:
            info.append("Impress Amount")
        if not self.local_advance_cleared\
                or not self.personal_telephone_bills_cleared\
                or not self.guest_house_accommodation_bills_cleared\
                or not self.any_other_entitlement_withheld\
                or not self.payroll_entitlement_paid:
            raise UserError(_("The following items haven't been processed %s") % info)
        else:
            self.finance_clearance = True
            self._check_if_clearance_is_done()


    def _check_selection(self):
        info = []
        
        if not self.office_key_returned:
            info.append("Office Key Returned")
        if not self.mobile_phone_and_sim_card_returned:
            info.append("Sim Card")
        if not self.mobile_returned:
            info.append("Mobile")
        if not self.telephone_and_bill_cleared:
            info.append("VHF")
        if not self.other_equipment:
            info.append("Thuraya")
        if not self.local_advance_cleared:
            info.append("Local Advance Cleared")
        if not self.personal_telephone_bills_cleared:
            info.append("Personal Telephone Bills Cleared")
        if not self.guest_house_accommodation_bills_cleared:
            info.append("Guest House Accommodation Bills ")
        if not self.any_other_entitlement_withheld:
            info.append("Any Other Entitlement Withheld")
        if not self.payroll_entitlement_paid:
            info.append("Payroll Entitlement Paid")
        if not self.email_revoked:
            info.append("Email Revoked?")
        if not self.all_code_revoked:
            info.append("All Code Revoked")
        if not self.domain_user_disabled_renamed_ip_phone_data_backup_complete:
            info.append("Domain User Disabled / Renamed IP Phone, Data Backup Complete")
        if not self.access_suspension_from_doors_and_laptop_returned:
            info.append("Access Suspension from Doors and Laptop Returned")
        if not self.training_cost:
            info.append("Training Cost")
        if not self.fee:
            info.append("Attendance and Leave Certified")
        if not self.id_card_returned:
            info.append("ID Card Returned")
        if not self.leave_balance:
            info.append("Leave Balance")
        if not self.exit_interview_form_filled:
            info.append("Exit Interview Form Filled")
        if not self.payroll_related_actions_if_any:
            info.append("Payroll Related Actions If Any")
        if not self.office_key_returned\
                or not self.mobile_phone_and_sim_card_returned\
                or not self.mobile_returned\
                or not self.telephone_and_bill_cleared\
                or not self.other_equipment\
                or not self.local_advance_cleared\
                or not self.personal_telephone_bills_cleared\
                or not self.guest_house_accommodation_bills_cleared\
                or not self.any_other_entitlement_withheld\
                or not self.payroll_entitlement_paid\
                or not self.email_revoked\
                or not self.all_code_revoked\
                or not self.domain_user_disabled_renamed_ip_phone_data_backup_complete\
                or not self.access_suspension_from_doors_and_laptop_returned\
                or not self.training_cost\
                or not self.fee\
                or not self.id_card_returned\
                or not self.leave_balance\
                or not self.exit_interview_form_filled\
                or not self.payroll_related_actions_if_any:
            raise UserError(_("The following items haven't been processed %s") % info)
    

    def action_relieve_letter(self):
        context = self.env.context
        if context is None:
            context = {}
        data = {
            'ids': self.ids,
            'model': self._context.get('active_model'),
            'form': self.read([])[0]
        }
        return self.env.ref("hr_doc.report_app").report_action(self, data=data)

    def action_experience_letter(self):
        context = self.env.context
        if context is None:
            context = {}
        data = {
            'ids': self.ids,
            'model': self._context.get('active_model'),
            'form': self.read([])[0]
        }
        return self.env.ref("hr_doc.report_app").report_action(self, data=data)

    @api.model
    def create(self, values):
        onsite_comp_obj = self.env['ir.sequence']
        separation_seq_val = onsite_comp_obj.next_by_code('hr.separation')
        values['name'] = separation_seq_val
        
        

        return super(HrSeparation, self).create(values)

    def return_current_user(self):
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        return user

    
    supervisor_user = fields.Many2one("res.users")
    def supervisor_confirm_clearance(self):
        self._check_supervisor_confirm_clearance()
        self.create_activity("All clearance items relating to the Supervisor have been cleared.")
        self.supervisor_user = self.return_current_user()

    library_user = fields.Many2one("res.users")
    def library_confirm_clearance(self):
        self._check_library_confirm_clearance()
        self.create_activity("All clearance items relating to the Library have been cleared.")
        self.library_user = self.return_current_user()

    procurement_user = fields.Many2one("res.users")
    def procurement_confirm_clearance(self):
        self._check_procurement_confirm_clearance()
        self.create_activity("All clearance items relating to the Procurement have been cleared.")
        self.procurement_user = self.return_current_user()

    inventory_user = fields.Many2one("res.users")
    def inventory_confirm_clearance(self):
        self._check_inventory_confirm_clearance()
        self.create_activity("All clearance items relating to the Inventory have been cleared.")
        self.inventory_user = self.return_current_user()

    hr_user = fields.Many2one("res.users")
    def hr_confirm_clearnce(self):
        self._check_hr_confirm_clearance()
        self.create_activity("All clearance items relating to the HR Department have been cleared.")
        
        self.hr_user = self.return_current_user()
        
    project_user = fields.Many2one("res.users")
    def project_unit_confirm_clearnce(self):
        self._check_project_unit_confirm_clearance()
        self.create_activity("All clearance items relating to the Project Unit have been cleared.")
       
        self.project_user = self.return_current_user()

    finance_user = fields.Many2one("res.users")
    def finance_confirm_clearance(self):
        self._check_finance_clearnce()
        self.create_activity("All clearance items relating to the Finance Department have been cleared.")
        self.finance_user = self.return_current_user()

    it_user = fields.Many2one("res.users")
    def it_confirm_clearance(self):
        self._check_it_confirm_clearance()
        self.create_activity("All clearance items relating to the IT Unit  have been cleared.")
        self.it_user = self.return_current_user()

    admin_user = fields.Many2one("res.users")
    def administrative_confirm_clearance(self):
        self._check_administrative_confirm_clearance()
        self.create_activity("All clearance items relating to the the Operations/Admin Department have been cleared.")
        self.admin_user = self.return_current_user()
  
    def create_activity(self, message):
        
        self.message_post(body=message, message_type='comment', subtype_xmlid='mt_comment')
    
    def check_employee_info(self):
        missing_info = []
        for rec in self:
            if rec.employee_id.employee_type == 'regular':
                if not rec.employee_id.department_id:
                    missing_info.append("Department")
                if not rec.employee_id.job_id:
                    missing_info.append("Job Position")
                if not rec.employee_id.parent_id:
                    missing_info.append("Manager")
                if not rec.employee_id.personal_email:
                    missing_info.append("Personal Email")
                if missing_info:
                    raise UserError(_("You cannot start clearance for this employee due to below missing field(s):\n %s") %missing_info) 
            if rec.employee_id.employee_type == 'field':
                if not rec.employee_id.department_id:
                    missing_info.append('Department')
                if not rec.employee_id.job_id:
                    missing_info.append("Job Position")
                if not rec.employee_id.parent_id:
                    missing_info.append("Manager")
                if missing_info:
                    raise UserError(_("You cannot start clearance for this employee due to below missing field(s):\n %s") %missing_info)

    def start_clearance(self):
        """
        This method is used to change the state
        to In Progress of the Hr Separation
        --------------------------------------------
        @param self : object pointer
        """
        
        for on in self:
            if on.employee_id.employee_type == 'regular':
                self.check_employee_info()
                on.clearance_mail()
                token = self.get_random_string(12)
                self.create_online_interview_form(token,self.employee_id.id)
            if on.employee_id.employee_type == 'field':
                self.check_employee_info()
            on.state = 'in_progress'

    def create_online_interview_form(self,token,employee_id):
        created_interview_form = self.env['exit.interview.form'].create({
            'employee_id': employee_id,
            'token':token
        })
        if created_interview_form:
            self.exit_interview_form_id = created_interview_form.id
            self.mail_exit_interview_form(self.employee_id,token)




    def mail_exit_interview_form(self,record,token):
        user = self.env['res.users']
        from_mail = user.browse(self._uid) and user.login or ''
        from_mail = from_mail.encode('utf-8')
        to_mail = (record.personal_email).encode('utf-8')

        email_template = False
        message = ""
        
        email_template = self.env.ref(
                'nl_separation.online_interview_exit_form')
        
        body_html = """
                    <![CDATA[<div style="font-family: 'Lucica Grande',
                    Ubuntu, Arial, Verdana, sans-serif; font-size: 14px;
                    color: rgb(34, 34, 34); background-color: #FFF; ">
                    <p>Dear """ + record.name + """,</p>
                    <br/>
                    <p>We are requesting your feedback regarding your employment with the SCA. Please be as open and honest as possible. By providing this information, you are helping to guide us in continuously improving our working environment. 
                    The information you provide will be confidential and will not be discussed in connection with your name. Your response will not affect your rehire status.</p>

                    </br>

                    <p>Thank you for taking the time to complete this survey. The HRM unit wishes you the best in your future endeavors. 
                    <br/>
                    
                    <p class="text-center"><a class="oe_stat_button btn btn-primary text-center" href="/interview?id=""" + str(record.id) + """&token=""" + token + """ ">Fill in the form</a></p>
                    <br/>
                    <br/>
                    <p>Head of HR.<br/>
                    <p>Kabul Management Office.<br/>
                    <p>Kabul, Afghanistan<br/>
                    </p>
                """
        if email_template:
            email_template.sudo().write({
                'subject': 'Online Exit Interview Form ' + record.name,
                'body_html': body_html,
                'email_from': from_mail,
                'email_to': to_mail
            })
            email_template.send_mail(self.id, force_send=True)


    def get_random_string(self,length):
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str

    


    def confirm(self):
        """
        This method is used to change the state
        to confirm of the Hr Separation
        and sets the approver who approves it
        --------------------------------------------
        @param self : object pointer
        """
        for rel_cal in self:
            rel_cal._check_selection()
            if not rel_cal.join_date or not rel_cal.relieve_date:
                raise UserError(_('Please make sure you have entered Employee Joining Date and Employement End Date'))
                
            user = self.env['res.users'].search([
                ('id', '=', rel_cal.employee_id.user_id.id)
                ])
            contracts = self.env['hr.contract'].search([
                ('employee_id', '=', rel_cal.employee_id.id),
                ('state', '=', 'open')
                ])
            vals_emp = {
                'resign_date': rel_cal.resign_date,
                'last_date': rel_cal.relieve_date,
                'blacklisted': rel_cal.blacklisted,
                }

            if rel_cal.relieve_date  == fields.Date.today():
                vals_emp.update({'active':False})
                user.sudo().write({'active': False})

            rel_cal.employee_id.write(vals_emp)
            history_vals = {
                'separation_id':rel_cal.id,
                'date': rel_cal.resign_date,
                'employment_separation_type': rel_cal.employment_separation_type.id,
                'blacklisted': rel_cal.blacklisted,
                'emp_h_id': rel_cal.employee_id.id
                }
            self.env['employment.history'].create(history_vals)
            for contract in contracts:
                contract.write({'state': 'in_separation'})
            rel_cal.state = 'confirmed'
            # rel_cal.approver_id = self._uid

    def confirm_separation(self):
        """
        This method is used to change the state
        to confirm of the Hr Separation
        and it is visible in Progress stage
        --------------------------------------------
        @param self : object pointer
        """
        for rel_cal in self:
            if not rel_cal.join_date or not rel_cal.relieve_date:
                raise UserError(_('Please make sure you have entered Employee Joining Date and Employement End Date'))

            user = self.env['res.users'].search([
                ('id', '=', rel_cal.employee_id.user_id.id)
                ])
            contracts = self.env['hr.contract'].search([
                ('employee_id', '=', rel_cal.employee_id.id),
                ('state', '=', 'open')
                ])
            vals_emp = {
                'resign_date': rel_cal.resign_date,
                'last_date': rel_cal.relieve_date,
                'blacklisted': rel_cal.blacklisted,
                }
            contract_vals = {
                'in_separation': True
            }
            if rel_cal.relieve_date  <= fields.Date.today():
                vals_emp.update({'active':False})
                user.sudo().write({'active': False})
                contract_vals.update({'state':'in_separation','separation_date':fields.Date.today()})
                rel_cal.is_separated = True

            rel_cal.employee_id.write(vals_emp)
            rel_cal.employee_id.message_post(body="Separated Employee")
            history_vals = {
                'separation_id':rel_cal.id,
                'date': rel_cal.resign_date,
                'employment_separation_type': rel_cal.employment_separation_type.id,
                'blacklisted': rel_cal.blacklisted,
                'emp_h_id': rel_cal.employee_id.id
                }
            self.env['employment.history'].create(history_vals)
            for contract in contracts:
                contract.write(contract_vals)
            rel_cal.state = 'confirmed'

    def clearance_mail(self):
        user = self.env['res.users']
        from_mail = user.browse(self._uid) and user.login or ''
        from_mail = from_mail.encode('utf-8')

        # groups = []
        
        # groups.append(self.manager_id.user_id.id)


        # groups.extend(user.search([]).filtered(
        #     lambda x: x.has_group("nl_separation.group_purchase_manager") and x.has_group("nl_separation.group_separation")).ids)
        # groups.extend(user.search([]).filtered(
        #     lambda x: x.has_group("nl_separation.group_account_manager") and x.has_group("nl_separation.group_separation")).ids)
        # groups.extend(user.search([]).filtered(
        #     lambda x: x.has_group("nl_separation.group_it_unit") and x.has_group("nl_separation.group_separation")).ids)
        # groups.extend(user.search([]).filtered(
        #     lambda x: x.has_group("hr.group_hr_manager") and x.has_group("nl_separation.group_separation")).ids)
        # users = list(set(groups))
        separation_notification_users = self.env['hr.separation.notification'].search([])

        users = []
        for rec in separation_notification_users:
            users.extend([rec.supervisor,rec.administartive_unit,rec.it_unit,rec.provurement_supply,rec.finance,rec.inventory_in_charge,rec.library,rec.hr_unit])

        for login in users:
            clearance = user.browse(login.id)
            if clearance.work_email:
                to_mail = (clearance.work_email).encode('utf-8')

                email_template = self.env.ref(
                    'nl_separation.email_separation_clearance_process')
                body_html = """
                    <![CDATA[<div style="font-family: 'Lucica Grande',
                    Ubuntu, Arial, Verdana, sans-serif; font-size: 14px;
                    color: rgb(34, 34, 34); background-color: #FFF; ">
                    <p>Dear """ + clearance.name + """,</p>
                    <br/>
                    <p>Kindly access the clearance form for """ + self.employee_id.name + """ to process all clearance items related to your department.</p>
                    
                    <ul>
                        <li>Name: """ + self.employee_id.name + """</li>
                        <li>Department: """ + self.employee_id.department_id.name + """</li>
                        <li>Position: """ + self.employee_id.job_id.name + """</li>
                        <li>Resign Date: """ + str(self.resign_date) + """</li>
                    </ul>
                    
                    <br/>
                    <br/>
                    <p>Head of HR.<br/>
                    <p>Kabul Management Office.<br/>
                    <p>Kabul, Afghanistan<br/>
                    </p>


                """
                if email_template:
                    email_template.sudo().write({
                        'body_html': body_html,
                        'email_from': from_mail,
                        'email_to': to_mail
                    })
                    email_template.send_mail(self.id, force_send=True)



    # def print_employment_certificate(self):
    #     return self.env.ref(
    #         'nl_separation.employee_certificate').report_action(self)
    
    def print_seperation_report(self):
        return self.env.ref(
            'nl_separation.employee_separation_report').report_action(self)

    def print_termination_report(self):
        return self.env.ref(
            'nl_separation.employee_separation_report').report_action(self)

    def print_termination_letter(self):
        if not self.employment_separation_type.name == 'termination':
            raise UserError(_("This type of report shall be printed only for a terminated employee."))
        else:
            return '%s' % (self.name)

    # cron job to cancel separated employee's contracts
    def _cancel_separated_employee_contract(self):
        today = fields.Date.today()
        for separation in self.search([('relieve_date','<=',today),('state','=','confirmed'),('is_separated','=',False)]):
            contract = self.env['hr.contract'].search([('employee_id','=',separation.employee_id.id),('state','=','open')])
            if len(contract):
                contract.write({
                    'state':'in_separation',
                    'in_separation':False,
                    'separation_date':fields.Date.today()
                })
                contract.update_resume_lines()
                contract.employee_id.user_id.write({'active': False})
                contract.employee_id.write({
                'active':False
                })
            separation.is_separated = True
            
    def _set_contract_separation_date(self):
        for separation in self.search([('state','=','confirmed')]):
            if separation.employee_id.contract_id.state == 'in_separation':
                separation.employee_id.contract_id.separation_date = separation.relieve_date

    def _update_employee_history(self):
        for separation in self.search([('state','=','confirmed')]):
            for rec in separation.employee_id.employee_history_ids:
                rec.date = separation.relieve_date

class SeparationType(models.Model):
    _name = 'hr.separation.type'
    _description = "Separation Type"

    name = fields.Char('Name')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.depends('employee_history_ids')
    def _employee_history(self):
        self.employee_history = any(x for x in self.employee_history_ids)

    employee_history = fields.Boolean(
        string="Employee History",
        compute=_employee_history
    )
    employee_history_ids = fields.One2many(
        'employment.history',
        'emp_h_id',
        string="Employees History"
    )


class EmploymentHistory(models.Model):
    _name = 'employment.history'
    _description = 'Employment History'

    date = fields.Date(
        string="Separation Date"
    )
    separation_id = fields.Many2one('hr.separation',string="Separation Reference Number")
    # separation_type = fields.Selection([
    #     ('resignation', 'Resignation'),
    #     ('redundant', 'Redundant'),
    #     ('retirement', 'Retirement'),
    #     ('end_of_contract', 'End of Contract'),
    #     ('termination', 'Dismissal'),
    #     ('death', 'Death'),
    #     ('foreshorten', 'Contract Foreshorten'),
    # ])

    employment_separation_type = fields.Many2one('hr.separation.type',string="Separation Type")

    blacklisted = fields.Boolean(
        string="Blacklisted?"
    )
    emp_h_id = fields.Many2one(
        'hr.employee'
    )
    employment_date = fields.Date(related='emp_h_id.join_date')

class ExitInterviewForm(models.Model):
    _name = 'exit.interview.form'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    name = fields.Char("Name", related="employee_id.name")
    job_title = fields.Many2one('hr.job', string="Job Title")

    better_employement_elsewhere = fields.Boolean("Better employment elsewhere", default= False)
    diffucilt_with_work = fields.Boolean("Difficulty with work &amp; family balance", default= False)
    limited_career = fields.Boolean("Limited career advancement opportunities", default= False)
    pay_compensation = fields.Boolean("Pay/Compensation issues", default= False)
    benefits = fields.Boolean("Benefits/entitlements issues", default= False)
    dissatisfied_job = fields.Boolean("Dissatisfied with job duties", default= False)
    dissatisfied_working_condition = fields.Boolean("Dissatisfied with working conditions", default= False)
    supervision_issues = fields.Boolean("Supervision issues", default= False)
    own_security = fields.Boolean("Concerned about own security.", default= False)
    higher_education = fields.Boolean("Continuation of higher education", default= False)
    

    place_of_work = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="How would you rate SCA as a place of work")

    working_condition = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="Working conditions, office, transportation, guesthouse, and other physical facilities were")

    supervisor_relationship = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="Your relationship with your supervisor was")

    understand_job = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="Your understanding of your Job description (duties, responsibilities, and performance standards) was")

    goals_and_objectives = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="The level of involvement in setting your work goals and objectives with your supervisor was")

    ahead_of_time = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="The extent to which you are informed ahead of time regarding changes to your work was")

    well_done_recognition = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="When you did a job well, the recognition you received was")

    constructive_feedback = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="The extent to which constructive feedback was given to help you grow and improve your performance was")

    problem_solving = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="Your supervisor’s willingness to listen to your problems and help you when you had questions and challenges was")

    respect = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="The respect and confidence you had in your supervisor was")

    staff_concern = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="Management willingness to address staff concerns was")

    effort_keep = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="The effort expended to keep you as an employee was ")

    level_of_concern = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="The level of concern for employees here in __________/SCA is")

    compare = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="Compared to other international organizations in Afghanistan, the benefit package wa    ")

    pay = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="The pay you received was    ")

    increment = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="You regarded your chances for promotion and increased pay as       ")

    development = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="To what extent were the training and development opportunities offered by SCA relevant and appropriate to your work ")

    culture = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="The culture of SCA as a Learning and progressive organization is ")

    cooperation = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="The level of cooperation among employees in your section/unit was")

    guidance_hr = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="The guidance and instruction you received from the HRM Unit was ")

    guidance_finance = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="The guidance and instruction you received from the Finance Unit was   ")

    guidance_admin = fields.Selection([
        ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="The guidance and instruction you received from the Admin Unit was   ")

    guidance_procurement = fields.Selection([
       ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="The guidance and instruction you received from the Procurement &amp; Supply Unit was")

    guidance_tr = fields.Selection([
       ('1','Poor'),
        ('2','Disappointing'),
        ('3','Fair'),
        ('4','Good'),
        ('5','Very Good')
    ],string="The cooperation and advice you received from the TR &amp; ER Unit was ")

    

    specific_expereinces = fields.Text('Please write any specific experiences that stood out (positive or negative) in relation to table above.  ')
    conditions = fields.Text("Under what conditions would you have stayed?")
    one_thing = fields.Text("What one thing would you have changed in SCA?")
    lose_employee = fields.Text("How can SCA avoid losing good employees in the future?")
    reconsider_working = fields.Text("Would you consider working with SCA in future?")
    other_comments = fields.Text("Any other Comments:  ")
    

    token = fields.Char()
    



class SeparationNotification(models.Model):
    _name = 'hr.separation.notification'
    _description = "Separation Notification"

    supervisor = fields.Many2one('res.users',string="Supervisor/Unit Head")
    administartive_unit = fields.Many2one('res.users',string="Administrative Unit")
    it_unit = fields.Many2one('res.users',string="IT Unit")
    provurement_supply = fields.Many2one('res.users',string="Procurement and Supply")
    finance = fields.Many2one('res.users',string="Finance")
    inventory_in_charge = fields.Many2one('res.users',string="Inventory In Charge")
    library = fields.Many2one('res.users',string="Library")
    hr_unit = fields.Many2one('res.users',string="HR")
