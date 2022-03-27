# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResumeLineExtended(models.Model):
    _inherit = 'hr.resume.line'

    specialization = fields.Char(
        string="Specialization"
    )
    domain = fields.Char(
        string="Domain"
    )
    active = fields.Boolean(
        string="Active",
        default=True
    )
    education_level = fields.Selection([
        ('1','Primary'),
        ('2','Grade 12'),
        ('3','Grade 14'),
        ('4','Bachelor'),
        ('5','Master'),
        ('6','Doctorate'),
    ])
    date_start = fields.Date(required=False)
    is_highest = fields.Boolean(string="Is Highest Education")
    line_type_id = fields.Many2one('hr.resume.line.type', string="Type", required=True)

    @api.model
    def create(self, vals):
        education = super(ResumeLineExtended, self).create(vals)
        if education.is_highest:
            education.update_employee_education(education.employee_id.id)
        return education

    def update_employee_education(self,employee_id):
        employee = self.env['hr.employee'].search([('id','=',employee_id)])
        edu_level = {'1':'Primary','2':'Grade 12','3':'Grade 14','4':'Bachelor','5':'Master','6':'Doctorate'}
        employee.write({
            'education_name': self.name,
            'education_start_date': self.date_start,
            'education_end_date': self.date_end,
            'education_institution': self.description,
            'education_level': self.education_level,
            'edu_level':edu_level[self.education_level],
            'is_illiterate':False
        })


    @api.onchange('line_type_id')
    def _onchange_line_type_id(self):
        self.domain = None
        if self.line_type_id:
            self.domain = self.line_type_id.name


class EmployeeSkill(models.Model):
    _inherit = 'hr.employee.skill'

    skill_level_id = fields.Many2one('hr.skill.level', required=True)

    @api.model
    def create(self, vals):
        skill = super(EmployeeSkill, self).create(vals)
        if skill.skill_type_id.name == 'Languages':
            skill.update_employee_language()
        return skill

    def update_employee_language(self):
        if self.employee_id.employee_language:
            self.employee_id.write({
                    'employee_language': str(self.employee_id.employee_language) + ", " + str(self.skill_id.name)
                })
        else:
            self.employee_id.write({
                    'employee_language':str(self.skill_id.name)
                })
