from odoo import api, fields, models, _, tools
from odoo.addons.nl_master.helpers import master_data

class UpdateContract(models.TransientModel):
    _name = "update.hr.contract.wiz"
    _description = 'Update Contract Wizard'

    contract_id = fields.Many2one('hr.contract')
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    job_position = fields.Many2one('hr.job')
    employment_type = fields.Selection(master_data.EMPLOYEMENT_TYPE)
    contract_approver = fields.Many2one('res.users')
    department_id = fields.Many2one('hr.department',string="Department")
    project_id = fields.Many2one('contract.project',string="Project")
    unit_id = fields.Many2one('hr.unit',string="Unit")
    salary_grade = fields.Many2one('salary.grade',string="Grade")
    salary_step = fields.Many2one('salary.step',string="Step")
    contract_signatory1 = fields.Many2one('res.users', string="Contract Signatory")
    wage = fields.Float('Wage', required=False, help="Employee's monthly gross wage.")

    @api.onchange('salary_grade')
    def set_domain_to_salary_step(self):
        if self.salary_grade:
            return {'domain':{'salary_step':[('grade_id','=',self.salary_grade.id)]}}

    def update_contract(self):
        contract = self.env['hr.contract'].search([('id','=',self.contract_id.id)])
        employee = self.env['hr.employee'].search([('id','=',contract.employee_id.id)])
        contract.write({
            'date_start':self.date_start or contract.date_start,
            'date_end':self.date_end or contract.date_end,
            'job_id':self.job_position.id or contract.job_id.id,
            'employment_type':self.employment_type or contract.employment_type,
            'contract_approver_user':self.contract_approver.id or contract.contract_approver_user.id,
            'department_id':self.department_id.id or contract.department_id.id,
            'unit_id':self.unit_id.id or contract.unit_id.id,
            'salary_grade':self.salary_grade.id or contract.salary_grade.id,
            'salary_step':self.salary_step.id or contract.salary_step.id,
            'contract_signatory':self.contract_signatory1.id or contract.contract_signatory.id,
            'wage':self.wage or contract.wage,
        })
        employee.write({
            'join_date':self.date_start or contract.date_start,
            'job_id':self.job_position.id or contract.job_id.id,
            'employment_type':self.employment_type or contract.employment_type,
            'department_id':self.department_id.id or contract.department_id.id,
            'project_id':self.project_id.id or contract.project_contract_id.id,
            'unit_id':self.unit_id.id or contract.unit_id.id,
        })
        if self.salary_grade or self.salary_step:
            contract.update_wage_in_contract_terms()
            contract.update_wage_and_contract_terms()
            employee.write({
                'employee_salary': self.wage,
                'employee_grade': self.salary_grade.name,
                'employee_step': self.salary_step.name,
            })
        contract.write({
            'wage':self.wage or contract.wage
        })
        employee.write({
                'employee_salary': contract.wage,
            })
        contract.calculate_pension()
        contract.calculate_tax()