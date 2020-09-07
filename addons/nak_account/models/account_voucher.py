from odoo import models, fields, api, _

class AccountVoucher(models.Model):
    _inherit    = 'account.voucher'

    @api.multi
    def create_report_ho(self):
        return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'report_voucher_ho',
                'datas'         : {
                    'model'         : 'account.voucher',
                    'id'            : self._context.get('active_ids') and self._context.get('active_ids')[0] or self.id,
                    'ids'           : self._context.get('active_ids') and self._context.get('active_ids') or [],
                    'name'          : (self.journal_report_type.capitalize() + " - " + self.name)or "---",
                    },
                'nodestroy'     : False
        }
