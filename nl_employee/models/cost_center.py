# -*- coding: utf-8 -*-


from odoo import models, fields, api,_

class CostCenter(models.Model):
    _name = 'cost.center'
    _description = 'Cost Center'
    
    name = fields.Char(string="Cost Center", required=True)
    
class CostCenter(models.Model):
    _name = 'donor.code'
    _description = 'Donor Code'
    
    name = fields.Char(string="Donor Code", required=True)