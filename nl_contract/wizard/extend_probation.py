from odoo import api, fields, models, _, tools

class ExtendProbation(models.TransientModel):
    _name = "extend.employee.probation"
    _description = 'Extend Employee Probation'

    probation_start_date = fields.Date('Probation Start Date')
    probation_end_date = fields.Date('Probation End Date')

    has_probation_period_date = fields.Boolean(compute="_check_probation_period_start")

    def _check_probation_period_start(self):
        print("+++++++++++++++++++")
        self.has_probation_period_date = False
        probation_period_start = self.env.context.get('probation_period_start')
        print("++++++++++++++++",probation_period_start)
        if probation_period_start:
            print("+++++++++++++++++++1")
            self.has_probation_period_date = False
        else:
            print("+++++++++++++++++++2")
            self.has_probation_period_date = True


    def extend_probation(self):
        employee_id = self.env.context.get('employee_id')
        employee = self.env['hr.contract'].search([('id','=',employee_id)])
        if employee.probation_period_start:
            employee.write({
                'probation_period_end':self.probation_end_date
            })
        else:
            employee.write({
                'probation_period_start':self.probation_start_date,
                'probation_period_end':self.probation_end_date
            })

