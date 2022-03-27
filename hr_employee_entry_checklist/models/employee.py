# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class HREntryChecklist(models.Model):
    _name = 'hr.entry.checklist'
    _description = 'Employee Checklist'

    name = fields.Char(required="True")
    description = fields.Text()
    category = fields.Selection([
        ('ict','Information & Communication Technology (ICT)'),
        ('su','Security Unit (SU)'),
        ('ssu','Service Support Unit (SSU)'),
        ('logistic','Logistic'),
        ('hr','Human Resources (HR)'),
        ('other','Other Items'),
    ])
    prent_id = fields.Many2one('hr.entry.checklist',string="Parent Category")
    is_parent = fields.Boolean(string="Is Main Category")
class HRPersonalChecklist(models.Model):
    _name = 'hr.personal.checklist'
    _description = 'Personal Checklist'

    name = fields.Char(required="True")
    description = fields.Text()
    prent_id = fields.Many2one('hr.entry.checklist',string="Parent Category")
    category = fields.Selection([
        ('personal_profile','Personal Profile'),
        ('learning_development','Learning and Development'),
        ('recruitment','Recruitment & Selection'),
        ('disciplinary','Disciplinary'),
        ('hr_administration','HR Administration'),
        ('exits_and_separation','Exits and Separation'),
    ])
    is_parent = fields.Boolean(string="Is Main Category")


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    entry_checklist = fields.Many2many('hr.entry.checklist', 'employee_checklist_rel', 'checklist_id', 'employee_id', 'Entry Checklist', default=0.0)
    security_checklist = fields.Many2many('hr.entry.checklist', 'security_checklist_rel', 'checklist_id', 'security_id', 'Security Checklist', default=0.0)
    service_support_checklist = fields.Many2many('hr.entry.checklist', 'service_checklist_rel', 'checklist_id', 'service_id', 'Security Checklist', default=0.0)
    logistic_checklist = fields.Many2many('hr.entry.checklist', 'logistic_checklist_rel', 'checklist_id', 'logistic_id', 'Security Checklist', default=0.0)
    hr_checklist = fields.Many2many('hr.entry.checklist', 'hr_checklist_rel', 'checklist_id', 'hr_id', 'Security Checklist', default=0.0)
    check_marked = fields.Float('Entry Progress', compute='_compute_check_marked',store=True)
    max_value = fields.Float(default=100.0)

    personal_file_checklist = fields.Many2many('hr.personal.checklist', 'personal_file_checklist_rel', 'checklist_id', 'employee_id', 'Personal File Checklist', default=0.0)
    learning_checklist = fields.Many2many('hr.personal.checklist', 'learning_checklist_rel', 'checklist_id', 'employee_id', 'Learning and Development Checklist', default=0.0)
    recruitment_checklist = fields.Many2many('hr.personal.checklist', 'recruitment_checklist_rel', 'checklist_id', 'employee_id', 'Recruitment Checklist', default=0.0)
    diciplinary_checklist = fields.Many2many('hr.personal.checklist', 'diciplinary_checklist_rel', 'checklist_id', 'employee_id', 'Diciplinary Checklist', default=0.0)
    hr_administration_checklist = fields.Many2many('hr.personal.checklist', 'hr_administration_checklist_rel', 'checklist_id', 'employee_id', 'HR Administration Checklist', default=0.0)
    exits_and_separation_checklist = fields.Many2many('hr.personal.checklist', 'exits_and_separation_checklist_rel', 'checklist_id', 'employee_id', 'Exits and Separation Checklist', default=0.0)
    personal_checklist_check_marked = fields.Float('Entry Progress', compute='_compute_personal_checklist_check_marked',store=True)
    personal_checklist_max_value = fields.Float(default=100.0)

    @api.depends('entry_checklist','security_checklist','service_support_checklist','logistic_checklist','hr_checklist')
    def _compute_check_marked(self):
        all_checklist = self.env['hr.entry.checklist'].search([])
        if len(all_checklist) >=1 : 
            for rec in self:
                rec.check_marked = ((len(rec.entry_checklist) + len(rec.security_checklist) + len(rec.service_support_checklist) + len(rec.logistic_checklist) + len(rec.hr_checklist))* 100)/len(all_checklist)

    @api.depends('personal_file_checklist','learning_checklist','recruitment_checklist','diciplinary_checklist')
    def _compute_personal_checklist_check_marked(self):
        all_personal_checklist = self.env['hr.personal.checklist'].search([])
        if len(all_personal_checklist) >=1 : 
            for rec in self:
                rec.personal_checklist_check_marked = ((len(rec.personal_file_checklist) + len(rec.learning_checklist) + len(rec.recruitment_checklist) + len(rec.diciplinary_checklist))* 100)/len(all_personal_checklist)