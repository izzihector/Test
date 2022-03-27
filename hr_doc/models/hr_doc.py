# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HrAppContentLine(models.Model):
    _name = 'hr.app.content.line'
    _description = 'HR Content Line'

    sequence = fields.Integer(
        string='Sequence'
    )
    title = fields.Char(
        string='Title'
    )
    text = fields.Html(
        string='Text',
        help='To get field values dynamically: ${object.field_name}'
    )
    hr_app_id = fields.Many2one(
        'hr.app.doc',
        string='Appointment'
    )


class HrAppDoc(models.Model):
    _name = 'hr.app.doc'
    _description = 'Hr App Doc'

    name = fields.Char(
        string='Name'
    )
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True
    )
    subject = fields.Char(
        string="Subject"
    )
    content_ids = fields.One2many(
        'hr.app.content.line',
        'hr_app_id',
        string='Content Line'
    )
    model_id = fields.Many2one(
        'ir.model',
        string='Object'
    )
    ref_ir_act_window_id = fields.Many2one(
        'ir.actions.act_window',
        string='Sidebar action',
        readonly=True,
        help="""Sidebar action to make "
                "this template available on "
                "records of the related "
                "document model."""
    )
    ref_ir_value_id = fields.Many2one(
        'ir.default',
        string='Sidebar button',
        readonly=True,
        help="Sidebar button to open "
             "the sidebar action."
    )

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=50):
        return super(HrAppDoc, self).name_search(
            name=name, args=args, operator=operator, limit=limit)

    def create_action(self):
        action_obj = self.env['ir.actions.act_window']
        for doc in self:
            vals = {}
            src_obj = doc.model_id.model
            button_name = _('Documents')
            vals['ref_ir_act_window_id'] = action_obj.create({
                'name': button_name,
                'type': 'ir.actions.act_window',
                'res_model': 'hr.doc.wiz',
                'src_model': src_obj,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'auto_refresh': 1,
                'binding_model_id': doc.model_id.id,
            }).id
            doc.write({'ref_ir_act_window': vals['ref_ir_act_window_id']})
            doc.write(vals)
            return True

    def unlink_action(self):
        for doc in self:
            try:
                if doc.ref_ir_act_window_id:
                    doc.ref_ir_act_window_id.unlink()
                if doc.ref_ir_value_id:
                    doc.ref_ir_value_id.unlink()
            except:
                raise UserError(_("Deletion of the action record failed."))
        return True

    def unlink(self):
        self.unlink_action()
        return super(HrAppDoc, self).unlink()
