# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Deby Wahyu Kurdian <deby.wahyu.kurdian@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

from odoo import models, fields, api, _
class ResPartner(models.Model):
    _inherit    = ['res.partner']

    partner_code    = fields.Char('Partner Code')

class AccountInvoice(models.Model):
    _inherit    = ['account.invoice']

    @api.multi
    def _write(self, vals):
        for invoice in self:
            new_number  = False
            if invoice.partner_id and invoice.partner_id.partner_code != '' and vals.get('number', False):
                if vals.get('number', False)[(vals.get('number', False).find('/custom_name/')+13):28] == '01':
                    month_name = str('I')
                elif vals.get('number', False)[(vals.get('number', False).find('/custom_name/')+13):28] == '02':
                    month_name = str('II')
                elif vals.get('number', False)[(vals.get('number', False).find('/custom_name/')+13):28] == '03':
                    month_name = str('III')
                elif vals.get('number', False)[(vals.get('number', False).find('/custom_name/')+13):28] == '04':
                    month_name = str('IV')
                elif vals.get('number', False)[(vals.get('number', False).find('/custom_name/')+13):28] == '05':
                    month_name = str('V')
                elif vals.get('number', False)[(vals.get('number', False).find('/custom_name/')+13):28] == '06':
                    month_name = str('VI')
                elif vals.get('number', False)[(vals.get('number', False).find('/custom_name/')+13):28] == '07':
                    month_name = str('VII')
                elif vals.get('number', False)[(vals.get('number', False).find('/custom_name/')+13):28] == '08':
                    month_name = str('VIII')
                elif vals.get('number', False)[(vals.get('number', False).find('/custom_name/')+13):28] == '09':
                    month_name = str('IX')
                elif vals.get('number', False)[(vals.get('number', False).find('/custom_name/')+13):28] == '10':
                    month_name = str('X')
                elif vals.get('number', False)[(vals.get('number', False).find('/custom_name/')+13):28] == '11':
                    month_name = str('XI')
                elif vals.get('number', False)[(vals.get('number', False).find('/custom_name/')+13):28] == '12':
                    month_name = str('XII')
                else:
                    month_name = str('')
                if vals.get('number', False).find('/custom_name/') > 0:
                    partner_code    = str(invoice.partner_id.partner_code) if str(invoice.partner_id.partner_code) != 'False' else "TBS"
                    new_number      = vals.get('number', False).replace(vals.get('number', False)[(vals.get('number', False).find('/custom_name/')):28], str("/") + str(partner_code) + "/" + month_name)
                    if vals.get('number', False):
                        vals.update({'number'       : new_number,
                                     'move_name'    : new_number})
            if invoice.move_id.name != new_number and new_number:
                invoice.move_id.write({'name' : new_number})
        res = super(AccountInvoice, self)._write(vals)
        return res