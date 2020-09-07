from odoo import models, fields, api, _

class AccountPayment(models.Model):
    _inherit    = 'account.payment'

    @api.multi
    def create_report_ho(self):
        return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'report_voucher_payment_ho',
                'datas'         : {
                    'model'         : 'account.payment',
                    'id'            : self._context.get('active_ids') and self._context.get('active_ids')[0] or self.id,
                    'ids'           : self._context.get('active_ids') and self._context.get('active_ids') or [],
                    'name'          : (self.journal_report_type.capitalize() + " - " + self.name)or "---",
                    },
                'nodestroy'     : False
        }
