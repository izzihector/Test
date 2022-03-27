# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrDocWizard(models.TransientModel):
    _name = "hr.doc.wiz"
    _description = 'HR Doc Wizard'

    app_doc_id = fields.Many2one(
        'hr.app.doc',
        string='Documents'
    )

    @api.onchange('app_doc_id')
    def onchange_app_doc_id(self):
        rec_ids = self.env['hr.app.doc'].search([
            ('model_id', '=', self._context.get('active_model', False))])
        res = {}
        res.update({'domain': {'app_doc_id': [('id', 'in', rec_ids.ids)]}})
        return res
