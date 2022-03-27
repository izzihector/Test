# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from datetime import date, datetime
from datetime import timedelta
from dateutil import relativedelta
from lxml import etree
from odoo.addons.nl_master.helpers import master_data
import calendar


class ResCompanyContracts(models.Model):
    _inherit = 'res.company'

    days_prior_to_contract_expiry = fields.Integer(
        string="Days Prior to Contract Expiry",
        required=True,
        default=45,
        help="Input the no. of days prior to contract expiry."
    )
    minimum_contract_days = fields.Integer(
        string="Avg Minimum Contract Days",
        required=True,
        default=90,
        help="Set the minimum number of days a contract can have."
    )
    contract_signatory = fields.Many2one(
        'hr.employee',
        string="Contract Signatory"
    )
    

    head_of_hr = fields.Many2one('hr.employee', string="Head of HR")
    
class Contract(models.Model):
    _name = 'hr.contract'
    _rec_name = 'contract_sequence'
    _inherit = ['hr.contract', 'mail.thread', 'mail.activity.mixin']


    renewal_type = fields.Selection([
        ('new', 'New'),
        ('extension', 'Extension'),
        ('for_shorterm', 'Foreshorten')], string="Renewal Type", default='new')
    wage = fields.Monetary('Gross Salary', required=False, tracking=True, help="Employee's monthly gross wage.", store=True)
    tax_free_amount = fields.Monetary('Non-Taxable Amount',default=5000)
    taxable_amount = fields.Monetary('Taxable Amount')
    tax_deduction = fields.Monetary('Tax Deduction')
    net_salary = fields.Monetary('Net Salary')
    allowance = fields.Monetary('Adjustment Allowance', tracking=True, help="Adujstment allowance", store=True)
    previous_salary = fields.Monetary("Previous Salary", tracking=True, store=True)

    transport_allowance = fields.Monetary('Transport', tracking=True, store=True)
    top_up_amount = fields.Monetary('Top Up Amount', tracking=True, store=True)
    transport_deduction = fields.Monetary('Transport Deduction', tracking=True, store=True)


    grade_and_step = fields.Char('Grade and Step', store=True)

    def _domain_contract_signatory(self):
        domain = [('id', 'in', self.env.context.get('contract_signatories'))]
        if self.env.context.get('active_model') == 'hr.contract':
            domain = [('id', 'in', self.env.context.get('contract_signatories'))]
        return domain
    contract_signatory = fields.Many2one(
        'res.users',
        string="Contract Signatory",
        domain = _domain_contract_signatory,tracking=True
        )

    department_id = fields.Many2one('hr.department', compute='_compute_employee_contract', store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", string="Department", tracking=True)
    job_id = fields.Many2one('hr.job', compute='_compute_employee_contract', store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", string='Job Position', tracking=True)
    contract_signatory_position = fields.Char(string="Signatory Position",related='contract_signatory.employee_id.job_id.name',tracking=True)

    is_contract_approver = fields.Boolean(compute="_check_contract_approver")

    next_numnber = fields.Integer()

    unit_id = fields.Many2one('hr.unit', related="employee_id.unit_id", store=True,tracking=True)

    probation_period_start = fields.Date('Probation Start Date',tracking=True)
    probation_period = fields.Selection([
        ('one_month','1 Month'),
        ('two_month','2 Month'),
        ('three_month','3 Month')
    ],string="Probation Period",tracking=True)
    probation_period_end = fields.Date('Probation End Date',tracking=True)
    increment_salary = fields.Float("Increment Salary")   
    previous_contract_id = fields.Many2one('hr.contract',string="Previous Contract ID")
    is_extended = fields.Boolean(string="Is Extended")
    leave_allocation_ids = fields.One2many('contract.leave.allocation', 'contract_id')

    duration_of_contract = fields.Char('Duration of contract(months/days/weeks)')
    teaching_experience = fields.Char(string="Teaching Experience")
    calculate_contract_duration = fields.Char(compute="Compute_contract_duration",string="Duration of contract(months)")
    contract_sequence = fields.Char(string='Contract Sequence', readonly=True,
                       default=lambda self: _('New'))
    father_name = fields.Char(string="Father Name", related="employee_id.father_name")
    name = fields.Char('Contract Reference', required=False)
    contract_change_date = fields.Date(string="Contract Change Date",default=fields.Date.today)
    is_first_contract = fields.Boolean(compute="compute_first_contract")
    foreshorten_cancellation_date = fields.Date(string="Foreshorten Date",readonly=True)
    separation_date = fields.Date(string="Separation Date",readonly=True)
    is_valid_contract = fields.Boolean(compute="_compute_minimum_contract_days")
    has_probation_appraisal = fields.Boolean(compute="_compute_has_probation_appraisal")


    def _compute_has_probation_appraisal(self):
        self.ensure_one()
        self.has_probation_appraisal = self.get_employee_probation_appraisal() and True or False

    def create_probation_appraisal(self):
        self.ensure_one()
        if self.get_employee_probation_appraisal():
            raise ValidationError("A probation appraisal record already exists for current employee.")

        if not (self.probation_period_start and self.probation_period_end):
            raise ValidationError("Please set probation period start date and end date.")

        self.env['probation.appraisal'].create({
            'employee_id': self.employee_id.id,
            'start_date': self.probation_period_start,
            'end_date': self.probation_period_end
        })
        self.env['bus.bus'].sendone(
            (self._cr.dbname, 'res.partner', self.env.user.partner_id.id),
            {'type': 'simple_notification','sticky': False, 'warning': True, 'title': _('Probation Appraisal'), 'message': _('Probation appraisal record created successfully.')}
        )
    
    def action_view_probation_appraisal(self):
        self.ensure_one()
        emp = self.get_employee_probation_appraisal()
        if emp:
            return {
                'name': _('Employee Probation Appraisal'),
                'type': 'ir.actions.act_window',
                'res_model': 'probation.appraisal',
                'view_id' : self.env.ref('nl_appraisal.view_employee_probation_appraisal_form').id,
                'view_mode': 'form',
                'res_id': emp.get('id')
            }

    def get_employee_probation_appraisal(self):
        self.ensure_one()
        self._cr.execute("""
                    SELECT
                        id
                    FROM
                        probation_appraisal
                    WHERE
                        employee_id = %s
                    AND
                        active = 't'
                    AND
                        state != 'cancel'
                    ORDER BY
                        id desc
                    LIMIT 1""", (self.employee_id.id,))
        return self._cr.dictfetchone()

    def difference_between_two_dates_in_months(self,date_1,date_2):
        return (date_2.year - date_1.year) * 12 + (date_2.month - date_1.month)

    def get_contraction_probation_info(self, payroll_start_date):
        """" This function return infomration about contract propration period.

        Args:
            payroll_date: The date to which the probation is compared.
        Return: Dictionary
            if propbation is expired then it returns with status False else True
        """
        for contract in self:
            if contract.probation_period_end and payroll_start_date:
                if payroll_start_date >= contract.probation_period_end:
                    duration = self.difference_between_two_dates_in_months(contract.probation_period_start,contract.probation_period_end)
                    return {'probation_status': 'Probation Ended','duration':duration}
                else:
                    return {'probation_status': 'Probation On Going'}
            else:
                return {'probation_status': 'Probation Not Set'}

    def _compute_minimum_contract_days(self):
        for rec in self:
            rec.is_valid_contract = False
            if rec.date_start and rec.date_end:
                if (rec.date_end - rec.date_start).days <= self.env.user.company_id.minimum_contract_days:
                    rec.is_valid_contract = True

    
        
    @api.onchange('contract_change_date')
    def set_contract_start_date(self):
        if self.contract_change_date:
            self.date_start = self.contract_change_date

    @api.model
    def update_step_grade(self):
        kmo_employees = self.env['hr.employee'].search([('office_id', '=', 1)]).mapped('id')
        running_contracts = self.search([('state', 'in', ['open']), ('employee_id', 'in',  kmo_employees)])
        for contract in running_contracts:
            employee = contract.employee_id
            if contract.grade_and_step and (employee.employee_salary != contract.wage or contract.allowance != 0):
                try:
                    contract_grade = contract.grade_and_step.split('-')[0].strip()
                    contract_step = contract.grade_and_step.split('-')[1].strip()
                    grade = self.env['salary.grade'].search([('contract', '=', contract.employment_type), ('name', '=', contract_grade)], limit=1)
                    step = self.env['salary.step'].search([('grade_id', '=', grade.id), ('name', '=', contract_step)], limit=1)
                    contract.write({'salary_grade': grade.id, 'salary_step': step.id})
                    employee.write({
                        "previous_salary": employee.employee_salary, 
                        "previous_grade": employee.employee_grade,
                        "previous_step": employee.employee_step,
                        "employee_salary": contract.wage, 
                        "contract_id": contract.id,
                        "employee_grade": contract_grade, 
                        "employee_step": contract_step,
                        "last_promotion_date": "2021-12-31"
                        })
                except Exception as e:
                    pass
                    
                
    @api.model
    def contract_probation_expiration_notification(self):
        running_contracts = self.env['hr.contract'].search([('state','=','open')])
        for contract in running_contracts:
            if contract.probation_period_end:
                if (contract.probation_period_end - fields.Date.today()).days <= 7:
                    contract.contract_probation_expiration(contract.employee_id.name,contract.date_end,contract.message_follower_ids)
    
    @api.model
    def update_contract_terms_and_conditions(self):
        """
        populate general terms and conditions of every contract in 'running' stage based on contract type.
        """
        running_contracts = self.search([])

        for contract in running_contracts:
            if not contract.general_term_ids:
                if contract.salary_grade and contract.salary_step and contract.employment_type:
                    contract.set_domain_to_salary_grade()
                    contract.update_non_fps_contract_terms_conditions()
                else:
                    contract.set_domain_to_salary_grade()
                    contract.update_fps_contract_terms_conditions()

    @api.model
    def set_probation_period_in_terms_conditions(self):
        contracts = self.search([])
        for contract in contracts:
            if contract.general_term_ids and contract.salary_grade and contract.salary_step and contract.probation_period_start and contract.probation_period_end:
                contract.update_probation_period_in_terms_conditions()
    
    @api.model
    def update_contract_tax_information(self):
        """
            this function is an schedualer to update the tax information of contracts.
        """
        contracts = self.search([])
        for contract in contracts:
            contract.calculate_tax()


    
    def update_non_fps_contract_terms_conditions(self):
        for item in self.general_term_ids:
            if 'The employment contract is' in item.name:
                item.update({
                    'name':f"The employment contract is {self.salary_grade.name + ' - ' + self.salary_step.name} ({dict(self._fields['employment_type'].selection).get(self.employment_type)}) and the first three months is probation period."
                })

    def update_fps_contract_terms_conditions(self):
        for item in self.general_term_ids:
            if 'Your basic salary per month is' in item.name and self.employment_type in ['fps1_2','fps1']:
                    item.update({
                        'name':f"Your basic salary per month is {self.wage} AFNs. The salary is according to the approved SCA salary scale/Ministry guidelines. You are liable for paying Income Tax and SCA will facilitate monthly tax deductions directly to govt."
                    })
            
    @api.model
    def create(self, vals):

        sequence_id = self.env['ir.sequence'].sudo().search([('code','=','hr.contract')])
        employee = self.env['hr.employee'].search([('id','=',vals['employee_id'])])
        if employee.office_id.code:
            sequence_id.write({
                'prefix':employee.office_id.code +'/'+fields.Date.today().strftime('%y')+'/'
            })
        if not employee.office_id.code:
            sequence_id.sudo().write({
                'prefix':fields.Date.today().strftime('%Y')+'/'
            })
        sequence = self.env['ir.sequence'].sudo().next_by_code('hr.contract')
        vals['contract_sequence'] = sequence or _('New')
        vals['name'] = sequence or _('New')
        contract = super(Contract, self).create(vals)
        employee.write({
            'join_date':contract.first_contract_date
        })


        leave_types = self.env['hr.leave.type'].search([('default_allocation', '=', True)]) # Put some conditions here
        current_leave_type_allocations = [c_a.leave_type_id.id for c_a in contract.leave_allocation_ids]
        for leave_type in leave_types:
            if leave_type.id not in current_leave_type_allocations:
                self.env['contract.leave.allocation'].create({
                    "leave_type_id": leave_type.id,
                    "no_of_days": leave_type.default_allocation_days,
                    "allocation_type": leave_type.default_allocation_type,
                    "is_allocated": False,
                    "contract_id": contract.id
                    })
        return contract

    def get_difference_between_two_dates_in_months(self, start_date, end_date):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        return (end_date - start_date).days / 30

    @api.depends('date_end')
    def Compute_contract_duration(self):
        for item in self:
            if item.date_end and item.date_start:
                difference_in_months = item.difference_between_two_dates_in_months(item.date_start,item.date_end)
        self.calculate_contract_duration = str(difference_in_months + 1)
        

    @api.onchange('increment_salary')
    def update_wage_after_increment(self):
        self.previous_salary = self.wage
        self.wage = self.wage + self.increment_salary


    @api.onchange('probation_period')
    def onchange_probation_period(self):
        self.ensure_one()
        
        if self.probation_period == 'one_month':
            start_date = datetime.strptime(self.probation_period_start.strftime("%m/%d/%y"), "%m/%d/%y")
            self.probation_period_end = start_date + timedelta(days=30)
        if self.probation_period == 'two_month':
            start_date = datetime.strptime(self.probation_period_start.strftime("%m/%d/%y"), "%m/%d/%y")
            self.probation_period_end = start_date + timedelta(days=60)
        if self.probation_period == 'three_month':
            start_date = datetime.strptime(self.probation_period_start.strftime("%m/%d/%y"), "%m/%d/%y")
            self.probation_period_end = start_date + timedelta(days=90)

    
    province_id = fields.Many2one('province', related="employee_id.province_id", string="Province")

    project_contract_id = fields.Many2one("contract.project", string="Project", related="employee_id.project_id",tracking=True)

    pension_amount = fields.Monetary('Pension',compute='calculate_pension',store=True )
    cal_pension = fields.Boolean(string="Calculate Pension")

    def _check_contract_approver(self):
        for item in self:
            if item.contract_approver_user == self.env.user:
                item.is_contract_approver = True
            else:
                item.is_contract_approver = False

    @api.onchange('wage')
    def calculate_pension(self):
        for item in self:
            if item.employment_type == 'open_ended' or item.cal_pension:
                item.pension_amount = (item.wage * 8.4 ) / 100
                
    @api.onchange('wage')
    def calculate_tax(self):
        for item in self:
            if item.wage >= 5001 and item.wage <= 12500:
                item.taxable_amount = item.wage - item.tax_free_amount
                item.tax_deduction = (item.taxable_amount * 2) / 100
                item.net_salary = item.wage - item.tax_deduction
            elif item.wage >= 12501 and item.wage <= 100000:
                item.taxable_amount = item.wage - item.tax_free_amount
                item.tax_deduction = 150 + (item.taxable_amount * 10) / 100
                item.net_salary = item.wage - item.tax_deduction
            elif item.wage >= 100001:
                item.taxable_amount = item.wage - item.tax_free_amount
                item.tax_deduction = 8900 + (item.taxable_amount * 20) / 100
                item.net_salary = item.wage - item.tax_deduction
            else:
                item.taxable_amount = 0.0
                item.tax_deduction = 0.0
                item.net_salary = item.wage - item.tax_deduction



    @api.onchange('cal_pension')
    def onchange_cal_pension(self):
        for item in self:
            if item.cal_pension:
                item.pension_amount = (item.wage * 8.4 ) / 100
            else:
                item.pension_amount = 0.0
    
    state = fields.Selection([
        ('draft', 'New'),
        ('to_approve', 'To Approve'),
        ('open', 'Running'),
        ('foreshorten', 'Foreshorten'),
        ('close', 'Expired'),
        ('in_separation', 'Separated'),
        ('cancel', 'Cancelled'),
        ('rejected', 'Rejected')
    ], string='Status', group_expand='_expand_states', copy=False,
        tracking=True, help='Status of the contract', default='draft')

    is_expiring_soon = fields.Boolean(
        string="Is Expiring Soon"
    )

    in_separation = fields.Boolean(
        string="In Separation"
    )

    contract_approval_user = fields.Selection([
        ('ceo', 'Head Office'),
        ('coo', 'Project Manager' ),
        ('porgram_dicrector', 'Program Director' ),
        ('coutry_director', 'Country Director' ),

    ], string="Contract Approver", copy=False,
        tracking=True, help='Status of the contract', default='ceo', required=True)

    contract_approver_user = fields.Many2one('res.users','Contract Approver User', required=True, tracking=True)
    

    salary_grade = fields.Many2one('salary.grade',string="Grade", tracking=True)


    salary_step = fields.Many2one('salary.step',string="Step", tracking=True)

    @api.onchange('employee_id')
    def return_contract_approvers(self):
        print("hellll")
        contract_approvers = []
        contract_signatories = []
        contract_approver_ids = self.env['hr.contract.approver'].sudo().search([('office_id','=',self.employee_id.office_id.id)])
        for user in contract_approver_ids.user_ids:
            contract_approvers.append(user.id)
        for signatory in contract_approver_ids.signatory_user_ids:
           
            contract_signatories.append(signatory.id)
            print(contract_signatories)
        if self.previous_contract_id:
            if self.previous_contract_id.state == 'foreshorten':
                self.renewal_type = 'for_shorterm'
            if self.previous_contract_id.state == 'close':
                self.renewal_type = 'extension'
        return {'domain': {'contract_approver_user': [('id', 'in', contract_approvers)],'contract_signatory': [('id', 'in', contract_signatories)]}}



    @api.onchange('salary_step',) 
    def update_wage_and_contract_terms(self):
        for item in self.general_term_ids:
            if 'The employment contract is' in item.name:
                item._origin.update({
                    'name':f"The employment contract is {self.salary_grade.name + ' - ' + self.salary_step.name} ({dict(self._fields['employment_type'].selection).get(self.employment_type)}) and the first three months is probation period."
                })

        if  self.salary_grade and self.salary_step and self.employment_type not in ['fps1_2','fps1']:
            self.wage = self.salary_step.value
            self.grade_and_step = self.salary_grade.name + " - " + self.salary_step.name
        else:
            self.wage = self.wage

    @api.onchange('probation_period_end')
    def update_probation_period_in_terms_conditions(self):
        for item in self.general_term_ids:
            if 'probation period' in item.name:
                if self.employment_type not in ['fps1_2','fps1']:
                    item._origin.update({
                        'name':f"The employment contract is {self.salary_grade.name + ' - ' + self.salary_step.name} ({dict(self._fields['employment_type'].selection).get(self.employment_type)}) and the first three months is probation period; starting from {self.probation_period_start.strftime('%d-%B-%Y')} till {self.probation_period_end.strftime('%d-%B-%Y')}."
                    }) 
                if self.employment_type == 'fps1_2':
                    item._origin.update({
                        'name':f"You are employed on category 1 of Project Field staff. The first one (1) month will be probation period; starting from {self.probation_period_start.strftime('%d-%B-%Y')} till {self.probation_period_end.strftime('%d-%B-%Y')}."
                    })  
                if self.employment_type == 'fps1':
                    item._origin.update({
                        'name':f"You are employed on category 2 of Project Field staff. The first one (1) month will be probation period; starting from {self.probation_period_start.strftime('%d-%B-%Y')} till {self.probation_period_end.strftime('%d-%B-%Y')}."
                    })   


    
    @api.onchange('employment_type')
    def set_domain_to_salary_grade(self):
        for item in self.general_term_ids:
            item.write({'contract_id':False})
           
        config_id = self.env['contract.general.terms.config'].sudo().search([('contract_type','=',self.employment_type)])
        for item in config_id.term_ids:
            self.env['contract.general.terms'].sudo().create({
                'name':item.name,
                'contract_id':self.id,
                'sub_point':item.sub_point,
                
            })
        
            
        if self.employment_type:
            if self.employment_type != 'other':
                return {'domain':{'salary_grade':[('contract','=',self.employment_type)]}}


    @api.onchange('wage')
    def update_wage_in_contract_terms(self):
        for item in self.general_term_ids:
           if 'Your basic salary per month is' in item.name and self.employment_type in ['fps1_2','fps1']:
                item._origin.update({
                    'name':f"Your basic salary per month is {self.wage} AFNs. The salary is according to the approved SCA salary scale/Ministry guidelines. You are liable for paying Income Tax and SCA will facilitate monthly tax deductions directly to govt."
                }) 

            
    @api.onchange('salary_grade')
    def set_domain_to_salary_step(self):
        if self.salary_grade:
            
            return {'domain':{'salary_step':[('grade_id','=',self.salary_grade.id)]}}
            

    employment_type = fields.Selection(master_data.EMPLOYEMENT_TYPE,tracking=True)
    other_contract_term = fields.Char(string="Specify Contract Term")

    task_ids = fields.One2many('contract.tasks', 'contract_id', string='Main Tasks')
    general_term_ids = fields.One2many('contract.general.terms', 'contract_id', string='General Terms', ondelete='cascade')
    
    def who_shall_approve(self):
      
        if self.contract_approval_user == 'ceo':
            self.activity_update()
            print(self.contract_approval_user)
           
        else:
            self.activity_update_cco()
            print(self.contract_approval_user)
    
    def extend_contract(self):
        contract_id = self.create({

            'employee_id':self.employee_id.id,
            'contract_approver_user':self.contract_approver_user.id,
            'project_contract_id':self.project_contract_id.id,
            'contract_signatory':self.contract_signatory.id,
            'previous_contract_id':self.id,
            'renewal_type':'for_shorterm',
            'structure_type_id':self.structure_type_id.id,
            'department_id':self.department_id.id,
            'job_id':self.job_id.id,
            'wage':self.wage,
        })
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.contract',
                'target': 'current',
                'res_id': contract_id.id,
            } 

    def compute_first_contract(self):
        self.ensure_one()
        self.is_first_contract = True

        contracts = self.employee_id.sudo().contract_ids.filtered(lambda c: c.state not in ['cancel','draft','to_approve','rejected'] and c.date_start < self.date_start)
        if contracts:
            self.is_first_contract = False
        else:
            self.is_first_contract = True

    @api.onchange('employee_id')
    def _fetch_previous_contract_details(self):
        # renewal_type = self.env.context.get('default_renewal_type')
        previous_wage = self.env.context.get('default_wage')
        previous_contract_id = self.env.context.get('default_contract_id')
        # self.renewal_type = renewal_type
         
        self.wage = previous_wage
        self.previous_contract_id = previous_contract_id

        contracts = self.employee_id.sudo().contract_ids.filtered(lambda c: c.state not in ['cancel','draft','to_approve','rejected'])
        perious_contract_date_start = ''
        previous_contract_id = None
        if contracts:
            self.is_first_contract = False
            # set previous contract id
            for contract in contracts:
                if contract.id != self._origin.id  and contract.date_start.strftime('%Y-%m-%d') > perious_contract_date_start:
                    perious_contract_date_start = contract.date_start.strftime('%Y-%m-%d')
                    previous_contract_id = contract.id
            if previous_contract_id:
                self.previous_contract_id = previous_contract_id
        else:
            self.is_first_contract = True


    def who_shall_deny(self):
        if self.contract_approval_user == 'ceo':
            self.activity_unlink('nl_contract.mail_ceo_contract_approval')
        else:
            self.activity_unlink('nl_contract.mail_coo_contract_approval')
    
    def activity_update(self):
        note = _('New %s Contract created by %s that needs your approval.') % (
            self.employee_id.name, self.create_uid.name)
        self.activity_schedule(
                'nl_contract.mail_ceo_contract_approval',
                note=note,
                user_id=self.contract_approver_user.id or self.env.user.id)

    def _unlink_activity(self,user):
        activity = self.env.ref('nl_contract.mail_ceo_contract_approval').id
        activities = self.env['mail.activity'].search([('user_id','=',user.id),('activity_type_id','=',activity)])
        for activity in activities:
            activity.unlink()
    

    def activity_update_cco(self):
        note = _('New %s Request created by %s') % (
            self.employee_id.name, self.create_uid.name)
        groups = []
        user = self.env['res.users']
        groups.extend(user.search([]).filtered(
            lambda x: x.has_group("nl_contract.group_coo")).ids)
        users = list(set(groups))
        for login in users:
            ceo = user.browse(login)
            self.activity_schedule(
                'nl_contract.mail_coo_contract_approval',
                note=note,
                user_id=ceo.id or self.env.user.id)

    def contract_probation_expiration(self,employee,end_date,followers):
        note = _('Please be advised that the probationary period of Employee: %s will end in one week on %s .') % (
                employee, end_date)
        for follower in followers:
            user = self.env['res.users'].search([('partner_id','=',follower.partner_id.id)])
            self.activity_schedule(
                    'nl_contract.mail_contract_probation_expiration',
                    note=note,
                    user_id=user.id)


    def send_to_approval(self):
        self.state = "to_approve"
        self.activity_update()
        if self.wage == 0:
            raise UserError(_("You can submit this contract without providing a value for wage"))

    def cancel(self):
        self.is_expiring_soon = False
        self.state = "cancel"
        self.foreshorten_cancellation_date = fields.Date.today()
        self.update_resume_lines()

    def manager_approve(self):
        self.who_shall_approve()
        self.state = "ceo_approval"
        
        # self.activity_update()

    def reject(self):
        self.state = "rejected"

    def ceo_reject(self):
        self.state = "rejected"
        self.who_shall_deny()
       

    def reset_to_draft(self):
        self.state = "draft"

    def ceo_approve(self):
        emp_update_values = {
            'previous_grade':self.employee_id.employee_grade,
            'previous_step':self.employee_id.employee_step,
            'previous_salary':self.employee_id.employee_salary,
            'last_promotion_date':fields.Date.today(),

            'employee_salary': self.wage,
            'employee_grade': self.salary_grade.name,
            'employee_step': self.salary_step.name,
            'job_id':self.job_id.id,
            'project_id':self.project_contract_id.id,
            'unit_id':self.unit_id.id,
            'department_id':self.department_id.id,
        }

        if self.employment_type and \
            self.employment_type in ['open_ended', 'casual_contract', 'fixed_term', 'project_based'] \
                and self.employee_id.employee_type != 'regular':
            emp_update_values.update({
                'employee_type': 'regular'
            })
        if self.employment_type and \
            self.employment_type in ['fps1_2', 'fps1'] \
                and self.employee_id.employee_type != 'field':
            emp_update_values.update({
                'employee_type': 'field'
            })
        if self.department_id and self.department_id != self.employee_id.project_id:
            emp_update_values.update({
                'department_id': self.department_id.id
            })
        if self.unit_id and self.unit_id != self.employee_id.unit_id:
            emp_update_values.update({
                'unit_id': self.unit_id.id
            })
        if self.project_contract_id and self.project_contract_id != self.employee_id.project_id:
            emp_update_values.update({
                'project_id': self.project_contract_id.id
            })
        if self.job_id and self.job_id != self.employee_id.job_id:
            emp_update_values.update({
                'job_id': self.job_id.id
            })

        self.state = "open"
        self.allocate_leave_balance()
        # self.who_shall_deny()
        self._unlink_activity(user=self.env.user)

        self.previous_contract_id.update({
            'is_extended':True
        })
        self.employee_id.update(emp_update_values)
        self.update_resume_lines()


    def foreshorten(self):
        self.is_expiring_soon = False
        self.state = "foreshorten"
        self.foreshorten_cancellation_date = fields.Date.today()


        contract_approvers = []
        contract_signatories = []
        contract_approver_ids = self.env['hr.contract.approver'].sudo().search([('office_id','=',self.employee_id.office_id.id)])
        for user in contract_approver_ids.user_ids:
            contract_approvers.append(user.id)
        for signatory in contract_approver_ids.signatory_user_ids:
            contract_signatories.append(signatory.id)

        contract_id = self.create({
            'employee_id':self.employee_id.id,
            'contract_approver_user':self.contract_approver_user.id,
            'project_contract_id':self.project_contract_id.id,
            'contract_signatory':self.contract_signatory.id,
            'previous_contract_id':self.id,
            'renewal_type':'for_shorterm',
            'structure_type_id':self.structure_type_id.id,
            'department_id':self.department_id.id,
            'job_id':self.job_id.id,
            'wage':self.wage,
        })

        return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'hr.contract',
                'target': 'current',
                'res_id': contract_id.id,
                'context': {
                    'contract_signatories': contract_signatories,
            },
            } 


    def print_contract(self):
        return self.env.ref(
            'nl_contract.action_print_contracts').report_action(self)


    def allocate_leave_balance(self):
        for item in self.leave_allocation_ids:
            if not item.is_allocated:
                if item.allocation_type == 'regular':
                    allocation = self.env['hr.leave.allocation'].sudo().create({
                        'employee_id':item.contract_id.employee_id.id,
                        'holiday_status_id':item.leave_type_id.id,
                        'name':item.leave_type_id.name + " Allocation for " + item.contract_id.employee_id.name,
                        'holiday_type':'employee',
                        'allocation_type':'regular',
                        'number_of_days':item.no_of_days
                    })
                    item.is_allocated = True
                    allocation.action_approve()
                    if allocation.state != 'validate':
                        allocation.write({'state': 'validate'})

                if item.allocation_type == 'accrual':
                    default_number_of_days = item.leave_type_id.default_allocation_days
                    if default_number_of_days < 1:
                        raise ValidationError(_("Default allocation days for the %s should be greather than zero"% (item.leave_type_id.name)))
                    number_of_days = 0.0
                    current_date = date.today()
                    last_day_of_current_month = calendar.monthrange(date.today().year, date.today().month)[1]
                    if item.contract_id.date_start.month == current_date.month:
                        if item.contract_id.date_start >= current_date:
                            number_of_days = last_day_of_current_month - item.contract_id.date_start.day
                            number_of_days = (default_number_of_days / 12 / last_day_of_current_month) * number_of_days
                        if item.contract_id.date_start < current_date:
                            if item.contract_id.date_start.day == 1:
                                number_of_days = default_number_of_days / 12
                            else:
                                number_of_days = last_day_of_current_month - current_date.day
                                number_of_days = (default_number_of_days / 12 / last_day_of_current_month) * number_of_days

                    if item.contract_id.date_start.month < current_date.month:
                        diff = current_date.month - item.contract_id.date_start.month
                        number_of_days =  ((item.contract_id.date_start.day - last_day_of_current_month) * diff * -1) + diff
                        
                        number_of_days = (default_number_of_days / 12 ) +  ((default_number_of_days / 12 / last_day_of_current_month) *  number_of_days)
                    
                    allocation = self.env['hr.leave.allocation'].sudo().create({
                        'employee_id':item.contract_id.employee_id.id,
                        'holiday_status_id':item.leave_type_id.id,
                        'name':item.leave_type_id.name + " Allocation for " + item.contract_id.employee_id.name,
                        'holiday_type':'employee',
                        'allocation_type':'accrual',
                        'number_per_interval':default_number_of_days / 12,
                        'date_from':self.return_the_first_day_of_next_month(),
                        'date_to':date(date.today().year, 12, 31),
                        'interval_number':1,
                        'number_of_days_display':number_of_days,
                        'interval_unit':'months',
                        'unit_per_interval':'days',
                        'number_of_days':number_of_days
                    })

                    allocation.action_approve()
                    allocation.with_context(bypass_rules=True).action_validate()

                     
    
    def difference_between_contract_start_date_and_current_date(self):
        return (self.date_start - date.today()).days


    

    def return_the_number_of_last_day_of_the_current_month(self):
        return calendar.monthrange(date.today().year, date.today().month)[1]
        
    # return the first day of next month.
    def return_the_first_day_of_next_month(self):
        if date.today().month == 12:
            return date(date.today().year, date.today().month, 1)
        else:
            return date(date.today().year, date.today().month + 1, 1)
        

    @api.constrains('employee_id', 'state', 'kanban_state', 'date_start', 'date_end')
    def _check_current_contract(self):
        """ Two contracts in state [incoming | open | close] cannot overlap """
        for contract in self.filtered(lambda c: c.state not in ['draft', 'cancel'] or c.state == 'draft' and c.kanban_state == 'done'):
            domain = [
                ('id', '!=', contract.id),
                ('employee_id', '=', contract.employee_id.id),
                '|',
                    ('state', 'in', ['open']), # 'close' Removed for netlinks
                    '&',
                        ('state', '=', 'draft'),
                        ('kanban_state', '=', 'done') # replaces incoming
            ]

            if not contract.date_end:
                start_domain = []
                end_domain = ['|', ('date_end', '>=', contract.date_start), ('date_end', '=', False)]
            else:
                start_domain = [('date_start', '<=', contract.date_end)]
                end_domain = ['|', ('date_end', '>', contract.date_start), ('date_end', '=', False)]

            domain = expression.AND([domain, start_domain, end_domain])
            if self.search_count(domain):
                raise ValidationError(_('An employee can only have one contract at the same time. (Excluding Draft and Cancelled contracts)'))


    @api.model
    def update_state(self):
        """ Behaviour is stoped for Netlinks. Follow contract_expiry()"""
        return True

    @api.model
    def contract_expiry(self):
        company = self.env.user.company_id
        current_date = fields.Date.context_today(self)
        contract_open_ids = self.search([
            ('state', '=', 'open')
        ])
        for running in contract_open_ids:
            if running.date_end:
                output = running.date_end - current_date
                if company.days_prior_to_contract_expiry >= output.days:
                    running.is_expiring_soon = True
                    # self.contract_expiry_notify(running)

                if running.date_end < current_date:
                    running.is_expiring_soon = False
                    running.write({'state': 'close'})
        return True

    def contract_expiry_notify(self, running):
        user = self.env['res.users']
        from_mail = user.browse(self._uid) and user.login or ''
        from_mail = from_mail.encode('utf-8')

        # groups = []

        # groups.extend(user.search([]).filtered(
        #     lambda x: x.has_group("hr_contract.group_hr_contract_manager")).ids)
        # users = list(set(groups))
        users = self.message_follower_ids

        for login in users:
            manager = user.browse(login)
            if manager.work_email:
                to_mail = (manager.work_email).encode('utf-8')

                father_name = ""
                job = ""
                department = ""
                if running.employee_id.father_name:
                    father_name = running.employee_id.father_name

                if running.job_id:
                    job = running.job_id.name

                if running.department_id:
                    department = running.department_id.name

                email_template = self.env.ref(
                    'nl_contract.email_contract_renew')

                body_html = """
                    <![CDATA[<div style="font-family: 'Lucica Grande',
                    Ubuntu, Arial, Verdana, sans-serif; font-size: 14px;
                    color: rgb(34, 34, 34); background-color: #FFF; ">
                    <p>Dear """ + manager.name + """,</p>
                    <p>Contract for the following will expire soon and requires renewal.
                    <br/>
                    <ul>
                        <li>Name: """ + running.employee_id.name + """</li>
                        <li>Father Name: """ + father_name + """</li>
                        <li>Position: """ + job + """</li>
                        <li>Department: """ + department + """</li>
                    </ul>
                    <br/>
                    <p>Thank you._<br/>
                    </p>
                """
                if email_template:
                    email_template.sudo().write({
                        'body_html': body_html,
                        'email_from': from_mail,
                        'email_to': to_mail
                    })
                    email_template.send_mail(running.id, force_send=True)

    def unlink(self):
        if self.state != 'draft':
            raise UserError(
                _("You can not delete!"))
        return super(Contract, self).unlink()

    def print_end_of_contract(self):
        return self.env.ref(
            'nl_contract.action_end_of_contracts').report_action(self)

    def print_extension_of_contract(self):
        return self.env.ref(
            'nl_contract.action_extension_of_contracts').report_action(self)

    def print_sehatmandi_contract(self):
        return self.env.ref(
            'nl_contract.action_print_contracts').report_action(self)

    def print_general_grant_contract(self):
        return self.env.ref(
            'nl_contract.action_print_contracts_v2').report_action(self)
    
    # def send_contract_to_hr(self):
    #     for contract in self:
    #         if contract.state == 'draft':
    #             contract.write({
    #                 'state':'manager_approval'
    #             })
    #         else:
    #             raise UserError(_("Only Contracts in draft state can be sent to HR Approval."))

    # def send_contract_to_ceo(self):
    #     for contract in self:
    #         if self.env.user.has_group('hr_contract.group_hr_contract_manager'):
    #             if contract.state == 'manager_approval':
    #                 contract.write({
    #                     'state':'ceo_approval'
    #                 })
    #             else:
    #                 raise UserError(_("Contract must be in Manager Approval state to be sent to CEO Approval"))
    #         else:
    #             raise UserError(_("This action is only authorized to HR manager of the Organization"))
        

    def ceo_confirm_contract(self):
        for contract in self:
            if self.env.user.has_group('nl_contract.group_ceo'):
                if contract.state == 'ceo_approval':
                    contract.ceo_approve()
                else:
                    raise UserError(_("Send the Contract for CEO to get approved"))
            else:
                raise UserError(_("This action is only authorized to CEO/Director of the Organization"))

    # update employee resume lines based on contract status
    def update_resume_lines(self):
        self.ensure_one()
        resume_lines = []
        resume_line_type = self.env['hr.resume.line.type'].search([('name','=','Experience')])
        hr_resume_line = self.env['hr.resume.line'].search([('employee_id','=',self.employee_id.id),('name','=',self.job_id.name),('date_start','=',self.date_start),('line_type_id','=',resume_line_type.id)])
        previous_hr_resume_line = self.env['hr.resume.line'].search([('employee_id','=',self.employee_id.id),('date_end','=',False)])
        today = fields.Date.today()
        if self.state == 'open':
            if hr_resume_line:
                hr_resume_line.write({
                    'date_end':today,
                })
            if previous_hr_resume_line:
                for rec in previous_hr_resume_line:
                    rec.write({
                        'date_end':today,
                    })
            if not hr_resume_line:
                resume_lines.append((0,0,{
                    'name':self.job_id.name or '',
                    'display_type':'classic',
                    'date_start':self.date_start,
                    'line_type_id':resume_line_type.id,
                }))
        if self.state == 'cancel':
            hr_resume_line.write({
                'date_end':self.date_end,
            })
        self.employee_id.write({
            'resume_line_ids':resume_lines
        })

    def extend_probation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("nl_contract.action_extend_probation_wizard")
        action.update({
            'context': {'employee_id':self.id,'probation_period_start':self.probation_period_start}
        })
        return action

    def update_contract(self):
        action = self.env['ir.actions.actions']._for_xml_id("nl_contract.action_update_contract_wizard")
        action.update({
            'context':{
                'default_contract_id':self.id,
            }
        })
        return action

    def print_contract_name(self):
        """
        This function returns contract template name. 
        It is called from employment_contract_v1.xml
        """
        self.ensure_one()
        employment_type = {'open_ended':'Open Ended','casual_contract':'Casual and Service',
        'fixed_term':'Fixed Term One Year','project_based':'Project Based','fps1_2':'FPS Category 1/2 Normal',
        'fps1':'FPS Category 2 Education','other':'Other'
        }
        return employment_type[self.employment_type] + ' ' + self.name

class SalaryGrade(models.Model):
    _name = 'salary.grade'
    _rec_name = 'name'
    _description = 'Salary Grade'

    name = fields.Char('Grade')
    contract = fields.Selection([
        ('open_ended','Open Ended'),
        ('casual_contract','Casual and Service'),
        ('fixed_term','Fixed Term'),
        ('project_based','Project Based'),
        ('fps1_2','FPS Category 1/2 Normal'),
        ('fps1','FPS Category 2 Education'),
        ('other','Other'),
    ])
    step_ids = fields.One2many('salary.step','grade_id',string="Step")


class SalaryStep(models.Model):
    _name = 'salary.step'
    _rec_name = 'name'
    _description = 'Salary Steps'

    name = fields.Char('Step')
    value = fields.Float('Value')
    grade_id = fields.Many2one('salary.grade',string="Grade")
     
        

class HrJob(models.Model):
    _inherit = 'hr.job'

    requires_travel = fields.Boolean(
        string="Requires  Travel"
    )
class ContractApprovers(models.Model):
    _name = 'hr.contract.approver'
    _description = "Contract Approvers"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    office_id = fields.Many2one('office', string='Office')
    user_ids = fields.Many2many('res.users', string="Contract Approvers")
    signatory_user_ids = fields.Many2many(comodel_name='res.users',
        relation='hr_contract_signatories_res_users_rel', string="Contract Signatories")
    infraction_approver_ids = fields.Many2many(
        comodel_name='res.users',
        relation='hr_contract_approver_infraction_res_users_rel',
        string="Office HR Responsible",
        domain=lambda self: [("groups_id", "=", self.env.ref("hr.group_hr_user").id)]
        )
    leave_approver_id = fields.Many2one(
        comodel_name='res.users',
        relation='hr_contract_approver_infraction_res_users_rel',
        string="Time Of Responsible",
        )
    payroll_responsible_finance = fields.Many2many(
        comodel_name='res.users',
        relation='payroll_responsible_finance_res_users_rel',
        string="Payroll Responsible (Finance)",
        domain=lambda self: [("groups_id", "=", self.env.ref("nl_payroll.group_payroll_finance").id)]
        )
    appraisal_responsible = fields.Many2one(
        comodel_name='res.users',
        string="Appraisal Responsible",
        required=True
        )
    
    @api.constrains("office_id")
    def check_office_unique(self):
        for rec in self:
            if rec.office_id and self.search([('office_id', '=', rec.office_id.id), ('id', '!=', rec.id)]):
                raise UserError (_("One HR Contract Approver Record Already Exists For the Current Office, %s"% (rec.office_id.name, )))

class ContractTasks(models.Model):
    _name = 'contract.tasks'
    _description = "Contract Tasks"

    name = fields.Char('Task')

    contract_id = fields.Many2one('hr.contract')

class ContractGeneralTerms(models.Model):
    _name = 'contract.general.terms'
    _description = "Terms and Conditions"
    _rec_name = 'name'

    name = fields.Char('Term')
    sub_point = fields.Boolean(string="Sub-Point")

    contract_id = fields.Many2one('hr.contract')

class ContractGeneralTermsConfig(models.Model):
    _name = 'contract.general.terms.config'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Contract Terms and Conditions"
    _rec_name = 'contract_type'

    contract_type = fields.Selection([
        ('open_ended','Open Ended'),
        ('casual_contract','Casual and Service'),
        ('fixed_term','Fixed Term One Year'),
        ('project_based','Project Based'),
        ('fps1_2','FPS Category 1/2 Normal'),
        ('fps1','FPS Category 2 Education'),
        ('other','Other'),
    ])

    term_ids = fields.One2many('contract.term', 'config_id', string='Terms')


    

class ContractTerms(models.Model):
    _name = 'contract.term'
    _description = "Contract Terms"
    _rec_name = 'name'

    name = fields.Char('Term & Condittion')
    sub_point = fields.Boolean(string="Sub-Point")
    config_id = fields.Many2one('contract.general.terms.config')

class ProjectAllocation(models.Model):
    _name = "project.allocation"

    contract_id = fields.Many2one("hr.contract")
    project_id = fields.Many2one("project")
    percentage = fields.Float("Percentage")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id)
    allocated_amount = fields.Float(string="Allocated Amount")
    
    


    @api.onchange("percentage")
    def _calculate_project_allocation(self):
        for item in self:
            item.allocated_amount = ((item.contract_id.wage / 100) * item.percentage ) * 100
        


    @api.onchange('project_id')
    def return_not_selected_project_ids(self):
        project_ids = []
        for project in self.contract_id.project_ids.project_id:
            project_ids.append(project.id)
        return {'domain': {'project_id': [('id', 'not in', project_ids)]}}   
                          
       
class ContractBudgetLine(models.Model):
    _name = 'budget.line'
    
    name = fields.Char("Budget Line")

    
class ContractProject(models.Model):
    _name = 'contract.project'
    
    name = fields.Char("Project Name", required=True)
    contract_id = fields.Many2one('hr.contract')



class ContractLeaveAllocation(models.Model):
    _name = 'contract.leave.allocation'

    leave_type_id = fields.Many2one('hr.leave.type', string="Leave Type")
    no_of_days = fields.Float(string="Number of Days")
    allocation_type = fields.Selection([('regular','Regular'),('accrual','Accrual')], string="Allocation Type")
    is_allocated = fields.Boolean()
    contract_id = fields.Many2one('hr.contract')


