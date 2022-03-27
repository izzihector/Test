# -*- coding: utf-8 -*-

import base64
import json
from odoo import http
from odoo.tools.translate import _
from odoo.http import request
from odoo.http import content_disposition


class CustomDownloadFile(http.Controller):
    ''' Download file '''
    @http.route('/web/binary/custom_download_file', type='http', auth='public')
    def custom_download_file(self, req, data, token):
        jdata = json.loads(data)
        model = jdata['model']
        field = jdata['field']
        data = jdata['data']
        jdata_id = jdata.get('id', None)
        filename_field = jdata.get('filename_field', None)
        context = jdata.get('context', {})

        Model = request.env[model]
        fields = [field]
        if filename_field:
            fields.append(filename_field)
        if data:
            res = {field: data}
        elif jdata_id:
            res = Model.read([int(jdata_id)], fields, context)[0]
        else:
            res = Model.default_get(fields, context)
        filecontent = base64.b64decode(res.get(field, ''))
        if not filecontent:
            raise ValueError(_("No content found for field '%s' on '%s:%s'"
                               ) % (field, model, jdata_id))
        filename = '%s_%s' % (model.replace('.', '_'), jdata_id)
        if filename_field:
            filename = filename_field or filename
        return req.make_response(filecontent, headers=[('Content-Type', 'application/octet-stream'),
                                                       ('Content-Disposition', content_disposition(filename))], cookies={'fileToken': token})
