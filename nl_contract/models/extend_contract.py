from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

class HrPayrollIndexExtended(models.TransientModel):

    _inherit = "hr.payroll.index"

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    type_of_increament = fields.Selection([
        ('amount','Amount'),
        ('percentage','Percentage'),
    ])
    amount = fields.Float(string="Amount")

    def create_new_contract_with_salary_increment_in_percentage(self):
        new_contracts = self.env['hr.contract']
        for contract in self.contract_ids:
            projects = []
            for project in contract.project_ids:
                projects.append((0,0,{
                    'project_id':project.project_id.id,
                    'percentage':project.percentage,
                    'allocated_amount':contract.wage + (contract.wage * self.percentage) / 100 ,
                }))
                project._calculate_project_allocation()
            new_contracts.create({
                'employee_id':contract.employee_id.id,
                'date_start':self.start_date,
                'date_end':self.end_date,
                'increment_salary':(contract.wage * self.percentage) / 100 ,
                'previous_salary':contract.wage,
                'state':'draft',
                'name':contract.name,
                'wage':contract.wage + (contract.wage * self.percentage) / 100 ,
                'renewal_type':'extension',
                'project_ids':projects,
                'previous_contract_id': contract.id,
                'legal_leave':contract.legal_leave,
                'sick_leave':contract.sick_leave,
                'contract_type':contract.contract_type,
                'department_id':contract.department_id.id,
                'job_id':contract.job_id.id,
                'apply_nta':contract.apply_nta,
                'structure_type_id':contract.structure_type_id.id,
                
                'budget_line_id':contract.budget_line_id.id,
                'activity_id':contract.activity_id.id,
                'hr_responsible_id':contract.hr_responsible_id.id,
            })
    
    def create_new_contract_with_salary_increment_in_amount(self):
        new_contracts = self.env['hr.contract']
        for contract in self.contract_ids:
            projects = []
            for project in contract.project_ids:
                projects.append((0,0,{
                    'project_id':project.project_id.id,
                    'percentage':project.percentage,
                    'allocated_amount':contract.wage + self.amount ,
                }))
                project._calculate_project_allocation()
            new_contracts.create({
                'employee_id':contract.employee_id.id,
                'date_start':self.start_date,
                'date_end':self.end_date,
                'increment_salary':self.amount ,
                'previous_salary':contract.wage,
                'state':'draft',
                'name':contract.name,
                'wage':contract.wage + self.amount ,
                'renewal_type':'extension',
                'project_ids':projects,
                'previous_contract_id': contract.id,
                'legal_leave':contract.legal_leave,
                'sick_leave':contract.sick_leave,
                'contract_type':contract.contract_type,
                'department_id':contract.department_id.id,
                'job_id':contract.job_id.id,
                'apply_nta':contract.apply_nta,
                'structure_type_id':contract.structure_type_id.id,
                
                'budget_line_id':contract.budget_line_id.id,
                'activity_id':contract.activity_id.id,
                'hr_responsible_id':contract.hr_responsible_id.id,
            })

    def action_confirm(self):
        if self.amount:
            self.create_new_contract_with_salary_increment_in_amount()
        if self.percentage:
            self.create_new_contract_with_salary_increment_in_percentage()
