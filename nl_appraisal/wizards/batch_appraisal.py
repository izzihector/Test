from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class BatchAppraisal(models.TransientModel):
    _name = "employee.batch.appraisal"
    _description = 'Employee Batch Appraisal'

    name = fields.Char(required=False)
    office_ids = fields.Many2many('office', string="Offices")
    unit_ids = fields.Many2many('hr.unit', string="Units")
    review_period_start_date = fields.Date(string="From", required=True)
    review_period_end_date = fields.Date(string="To", required=True)
    appraisal_type = fields.Selection([
        ('none', 'N/A'),
        ('admin_staff', 'Annual Performance Review'),
        ('field_staff', 'Entry Level/Support Staff'),
        ])
    
    @api.constrains('review_period_start_date', 'review_period_end_date')
    def validate_appraisal_date(self):
        for rec in self:
            if rec.review_period_start_date and rec.review_period_end_date and rec.review_period_start_date >= rec.review_period_end_date:
                raise ValidationError(_("Appraisal Review start date should be less than end date."))
    
    def create_appraisals(self):
        for rec in self:
            domain = [('appraisal_type', '!=', 'none')]
            if rec.office_ids:
                domain.append(('office_id', 'in', rec.office_ids.mapped('id')))
            if rec.unit_ids:
                domain.append(('unit_id', 'in', rec.unit_ids.mapped('id')))
            if rec.appraisal_type:
                domain.append(('appraisal_type', '=', rec.appraisal_type))
            employees = self.env['hr.employee'].search(domain).mapped('id')
            if not employees:
                raise ValidationError(_("No emloyees found with this creteria."))
            for emp_id in employees:
                tmp_appraisal = self.env['employee.appraisal'].new({
                    "employee_id": emp_id,
                    "review_period_start_date": rec.review_period_start_date,
                    "review_period_end_date": rec.review_period_end_date,
                    })
                tmp_appraisal.onchange_employee_id()
                values  = tmp_appraisal._convert_to_write(tmp_appraisal._cache)
                appraisal = self.env['employee.appraisal'].create(values)
                if appraisal.appraisal_type == 'field_staff':
                    appraisal.with_context(delay_appraisals_send_emails=True).move_to_supervisor_review_field()
                else:
                    appraisal.with_context(delay_appraisals_send_emails=True).move_to_objective_settings()
        return self.open_appraisal_view()

    @api.model
    def default_get(self, d_fields):
        vals = super(BatchAppraisal, self).default_get(d_fields)
        current_year_start = fields.Date.today().replace(day=1, month=3)
        current_year_end = fields.Date.today().replace(current_year_start.year+1, day=28, month=2)
        vals['review_period_start_date'] = current_year_start
        vals['review_period_end_date'] = current_year_end
        
        return vals


    def open_appraisal_view(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("nl_appraisal.employee_appraisal_action")
        return action