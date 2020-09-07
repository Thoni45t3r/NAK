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

class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    user_warehouse_pr   = fields.Many2one('res.users', string='PJ Gudang', related='company_id.user_warehouse_pr',)
    user_qc_pr          = fields.Many2one('res.users', string='KTU', related='company_id.user_qc_pr',)
    user_director_pr    = fields.Many2one('res.users', string='Direktur', related='company_id.user_director_pr',)
