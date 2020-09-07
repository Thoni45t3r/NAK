# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Hendra Saputra <hendrasaputra0501@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import float_compare, float_is_zero


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    writeoff_sale_account_asset_id = fields.Many2one('account.account', 'Write-off Sale Account')

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    date_accrue = fields.Date('Date Accrue')
    account_depreciation_expense_id = fields.Many2one('account.account', 'Depreciation Expense Acccount', help='If you fill this, then this Asset will use this account as Expense Depreciation')
    prev_accumulated_depr = fields.Float(string='Prev. Accumulated Depreciation', digits=0, readonly=True, states={'draft': [('readonly', False)]},
        help="It is the acculumated depreciation amount of the Opening Asset Entry.")
    disposal_reason = fields.Text(string='Disposal Reason', readonly=True)
    disposal_method = fields.Selection(selection=[('asset_sale', 'Sold'), ('asset_dispose', 'Disposed')], string='Disposal Method', readonly=True)
    disposal_move_id = fields.Many2one('account.move', 'Disposal Entry', readonly=True)
    disposal_invoice_id = fields.Many2one('account.invoice', 'Sales Invoice Asset', readonly=True)
    disposal_move_line_ids = fields.One2many('account.move.line', related='disposal_move_id.line_ids', string='Disposal Asset', readonly=True)

    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'disposal_reason': '',
            'disposal_method': False,
            'disposal_move_id': False,
            'disposal_invoice_id': False,
        })
        return super(AccountAssetAsset, self).copy(default)
    
    @api.multi
    def validate(self):
        self.write({'state': 'open'})
        fields = [
            'method',
            'method_number',
            'method_period',
            'method_end',
            'method_progress_factor',
            'method_time',
            'salvage_value',
            'prev_accumulated_depr',
            'invoice_id',
        ]
        ref_tracked_fields = self.env['account.asset.asset'].fields_get(fields)
        for asset in self:
            tracked_fields = ref_tracked_fields.copy()
            if asset.method == 'linear':
                del(tracked_fields['method_progress_factor'])
            if asset.method_time != 'end':
                del(tracked_fields['method_end'])
            else:
                del(tracked_fields['method_number'])
            dummy, tracking_value_ids = asset._message_track(tracked_fields, dict.fromkeys(fields))
            asset.message_post(subject=_('Asset created'), tracking_value_ids=tracking_value_ids)

    @api.one
    @api.depends('value', 'prev_accumulated_depr', 'salvage_value', 'depreciation_line_ids.move_check', 'depreciation_line_ids.amount', 'disposal_move_id.state')
    def _amount_residual(self):
        total_amount = 0.0
        for line in self.depreciation_line_ids:
            if line.move_check:
                total_amount += line.amount
        if self.disposal_move_id and self.disposal_move_id.state=='posted':
            self.value_residual = 0.0
        else:
            self.value_residual = self.value - total_amount - (self.prev_accumulated_depr + self.salvage_value)

class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    disposal_method = fields.Selection([('asset_sale', 'Sold'), ('asset_dispose', 'Disposed')], string='Disposal Method')
    disposal_reason = fields.Text(string='Disposal Reason')

    @api.model
    def _cron_depreciate(self):
        to_depreciate = self.search([('depreciation_date','<=',fields.Date.context_today(self)), ('asset_id.state','=','open'), ('move_id','=',False)])
        to_depreciate.create_move(datetime.today())

    @api.multi
    def create_move(self, post_move=True):
        created_moves = self.env['account.move']
        prec = self.env['decimal.precision'].precision_get('Account')
        for line in self:
            if line.move_id:
                raise UserError(_('This depreciation is already linked to a journal entry! Please post or delete it.'))
            category_id = line.asset_id.category_id
            depreciation_date = self.env.context.get(
                'depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
            company_currency = line.asset_id.company_id.currency_id
            current_currency = line.asset_id.currency_id
            amount = current_currency.with_context(date=depreciation_date).compute(line.amount, company_currency)
            asset_name = line.asset_id.name + ' (%s/%s)' % (line.sequence, len(line.asset_id.depreciation_line_ids))
            move_line_1 = {
                'name': asset_name,
                'account_id': category_id.account_depreciation_id.id,
                'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id,
                'partner_id': line.asset_id.partner_id.id,
                'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'sale' else False,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
            }
            move_line_2 = {
                'name': asset_name,
                'account_id': line.asset_id.account_depreciation_expense_id and line.asset_id.account_depreciation_expense_id.id or category_id.account_depreciation_expense_id.id,
                'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id,
                'partner_id': line.asset_id.partner_id.id,
                'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'purchase' else False,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and line.amount or 0.0,
            }
            move_vals = {
                'ref': line.asset_id.code,
                'date': depreciation_date or False,
                'journal_id': category_id.journal_id.id,
                'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
            }
            move = self.env['account.move'].create(move_vals)
            line.write({'move_id': move.id, 'move_check': True})
            created_moves |= move

        if post_move and created_moves:
            created_moves.filtered(
                lambda m: any(m.asset_depreciation_ids.mapped('asset_id.category_id.open_asset'))).post()
        return [x.id for x in created_moves]