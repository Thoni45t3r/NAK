# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Deby Wahyu Kurdian <deby.wahyu.kurdian@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError, except_orm, Warning, RedirectWarning, ValidationError

class PurchaseOrder(models.Model):
    _inherit      	= 'purchase.order'
    _description	= 'Purchase Order'

    @api.multi
    def print_purchase(self):
        return {
            'type'          : 'ir.actions.report.xml',
            'report_name'   : 'report_purchase_order',
            'datas'         : {
                    'model' : 'purchase.order',
                    'id'    : self.id,
                    'name'  : self.name or "^-^", },
            'nodestroy': False
        }