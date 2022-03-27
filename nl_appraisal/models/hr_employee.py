from odoo import fields, models, api, _
class HREmployee(models.Model):
    _inherit = 'hr.employee'

    appraisal_type = fields.Selection([
        ('none', 'N/A'),
        ('admin_staff', 'Annual Performance Review'),
        ('field_staff', 'Entry Level/Support Staff'),
        ], default="none", required=True)