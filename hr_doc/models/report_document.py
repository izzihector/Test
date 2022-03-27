# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import copy
import logging
import datetime
from urllib.parse import urlencode, quote as quote
from odoo import _, api, models
from odoo import tools
from odoo.exceptions import UserError
from functools import reduce


import dateutil.relativedelta as relativedelta


_logger = logging.getLogger(__name__)


try:
    # We use a jinja2 sandboxed environment to render mako templates.
    # Note that the rendering does not cover all the mako syntax, in particular
    # arbitrary Python statements are not accepted, and not all expressions are
    # allowed: only "public" attributes (not starting with '_') of objects may
    # be accessed.
    # This is done on purpose: it prevents incidental or malicious execution of
    # Python code that may break the security of the server.
    from jinja2.sandbox import SandboxedEnvironment
    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,  # do not output newline after blocks
        autoescape=True,  # XML/HTML automatic escaping
    )
    mako_template_env.globals.update({
        'str': str,
        'quote': quote,
        'urlencode': urlencode,
        'datetime': datetime,
        'len': len,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'filter': filter,
        'reduce': reduce,
        'map': map,
        'round': round,
        # 'cmp': cmp,

        # dateutil.relativedelta is an old-style class and cannot be directly
        # instanciated wihtin a jinja2 expression, so a lambda "proxy" is
        # is needed, apparently.
        'relativedelta': lambda *a, **kw: relativedelta.relativedelta(*a, **kw)
    })
    mako_safe_template_env = copy.copy(mako_template_env)
    mako_safe_template_env.autoescape = False
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")


class DocumentReport(models.AbstractModel):
    _name = 'report.hr_doc.report_document'
    _description = 'HR Doc Report'

    @api.model
    def generate_dynamic_data(self, template_txt, record):
        # try to load the letter content
        try:
            mako_env = mako_safe_template_env if self.env.context.get(
                'safe') else mako_template_env
            template = mako_env.from_string(tools.ustr(template_txt))
        except Exception:
            _logger.info("Failed to load template %r",
                         template_txt, exc_info=True)

        variables = {'object': record}

        try:
            render_result = template.render(variables)
        except Exception:
            _logger.info("Failed to render template %r using values %r"
                         % (template, variables), exc_info=True)
            raise UserError(_("Failed to render template %r using values %r")
                            % (template, variables))
        if render_result == u"False":
            render_result = u""
        return render_result

    def _convert_text(self, data, act_rec):
        """
        This method will be call from report template
        for getting dynamic value of field passed
        in format ${field_name} .
        """
        if act_rec and data:
            generated_field_values = self.generate_dynamic_data(
                data, act_rec)
            return generated_field_values
        else:
            return data

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data if data is not None else {}
        active_model = self._context.get('active_model')
        docs = self.env[active_model].browse(self._context.get('active_id'))
        if self._context.get('relieve'):
            app_letter = self.env['hr.app.doc'].search([
                ('name', 'ilike', 'Relieve Agreement Letter')])
            return {
                'doc_ids': self.ids,
                'docs': docs,
                'app_doc_id': app_letter,
                'convert_text': self._convert_text
            }
        elif self._context.get('experience'):
            app_letter = self.env['hr.app.doc'].search([
                ('name', 'ilike', 'Experience Letter')])
            return {
                'doc_ids': self.ids,
                'docs': docs,
                'app_doc_id': app_letter,
                'convert_text': self._convert_text
            }
        else:
            app_letter = self.env['hr.app.doc'].browse(
                (data['form'].get('app_doc_id')[0]))
            return {
                'doc_ids': docids,
                'docs': docs,
                'data': data,
                'app_doc_id': app_letter,
                'convert_text': self._convert_text
            }
