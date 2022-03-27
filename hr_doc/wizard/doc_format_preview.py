# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class DocFormatPreview(models.TransientModel):
    _inherit = "hr.app.doc"
    _name = "doc.format.preview"
    _description = "Doc Format Preview"

    @api.model
    def _get_records(self):
        """Return Records of particular Email Template's Model."""
        format_id = self._context.get('format_id')
        default_res_id = self._context.get('default_res_id')
        if not format_id:
            return []
        template = self.env['hr.app.doc'].browse(int(format_id))
        records = self.env[template.model_id.model].search([], limit=10)
        records |= records.browse(default_res_id)
        return records.name_get()

    @api.model
    def default_get(self, fields):
        result = super(DocFormatPreview, self).default_get(fields)

        if 'res_id' in fields and not result.get('res_id'):
            records = self._get_records()
            result['res_id'] = records and records[0][
                0] or False  # select first record as a Default
        if self._context.get('template_id') and \
                'model_id' in fields and not result.get('model_id'):
            result['model_id'] = self.env['hr.app.doc'].browse(
                self._context['format_id']).model_id.id
        return result
    res_id = fields.Selection(_get_records, 'Sample Document')

    @api.onchange('res_id')
    def on_change_res_id(self):
        values = {}
        if self.res_id and self._context.get('format_id'):
            template = self.env['hr.app.doc'].browse(
                self._context['format_id'])
            val = self.env['report.hr_doc.report_document']. \
                browse(self._context['format_id'])
            self.name = template.name
            for rec in template:
                for line_rec in rec.content_ids:
                    values = self.env['report.hr_doc.report_document']. \
                        generate_dynamic_data(line_rec.text, self.res_id)
