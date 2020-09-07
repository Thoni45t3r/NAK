# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Deby Wahyu Kurdian <deby.wahyu.kurdian@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

import logging
import time
import datetime
import calendar
from odoo.tools.translate import _
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.addons import decimal_precision as dp
from odoo import models, fields, tools, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
import base64
import xlrd

############################################### Transaction Nota Angkut Buah ################################################
class lhm_transaction_line(models.Model):
    _inherit = 'lhm.transaction'

    @api.multi
    def recalculate_plantation(self):
        all_plantation_ids  = self.env['lhm.transaction'].search([('account_period_id', '=', self.account_period_id.id)])
        for plantation in all_plantation_ids:
            for line in plantation.lhm_line_ids:
                if line.attendance_id and line.employee_id and line.min_wage_id:
                    if line.attendance_id:
                        line.valid      = True
                    if line.overtime_hour and line.overtime_hour > 0:
                        holiday         = False
                        overtime_data   = self.env['hr.overtime'].search([('hours', '=', line.overtime_hour)], limit=1)
                        holiday_data    = self.env['hr.holidays.public.line'].search([('date', '=', line.date)])
                        if holiday_data:
                            holiday     = True
                        if overtime_data and line.employee_id.type_id and line.employee_id.type_id.overtime_calc:
                            if holiday and overtime_data and line.min_wage_id.umr_month != 0.00:
                                line.overtime_value = round((line.min_wage_id.umr_month / 173) * overtime_data.holiday, -1)
                            elif not holiday and overtime_data and line.min_wage_id.umr_month != 0.00:
                                # check_holiday = plantation.lhm_line_ids.filtered(lambda x: x.attendance_id.code=='PH' and x.non_work_day>0.0)
                                # if check_holiday or line.attendance_id.type=='na':
                                if line.attendance_id.overtime_base_value=='jam_kerja_libur':
                                    line.overtime_value = round((line.min_wage_id.umr_month / 173) * overtime_data.holiday, -1)
                                else:
                                    line.overtime_value = round((line.min_wage_id.umr_month / 173) * overtime_data.normal_day, -1)
                            else:
                                line.overtime_value = 0
                        if overtime_data and line.employee_id.type_id and not line.employee_id.type_id.overtime_calc:
                            if holiday and overtime_data and line.min_wage_id.umr_month != 0.00:
                                line.overtime_value = (line.min_wage_id.umr_month / 25) * float(float(3) / float(20)) * overtime_data.holiday
                            elif not holiday and overtime_data and line.min_wage_id.umr_month != 0.00:
                                # check_holiday = plantation.lhm_line_ids.filtered(lambda x: x.attendance_id.code=='PH' and x.non_work_day>0.0)
                                # if check_holiday or line.attendance_id.type=='na':
                                if line.attendance_id.overtime_base_value=='jam_kerja_libur':
                                    line.overtime_value = round((line.min_wage_id.umr_month / 25) * float(float(3) / float(20)) * overtime_data.holiday, -1)
                                else:
                                    line.overtime_value = round((line.min_wage_id.umr_month / 25) * float(float(3) / float(20)) * overtime_data.normal_day, -01)
                            else:
                                line.overtime_value = 0

class lhm_transaction_line(models.Model):
    _inherit = 'lhm.transaction.line'

    @api.onchange('overtime_hour')
    def _onchange_overtime_hour(self):
        if self.overtime_hour:
            holiday         = False
            overtime_data   = self.env['hr.overtime'].search([('hours','=',self.overtime_hour)], limit=1)
            holiday_data    = self.env['hr.holidays.public.line'].search([('date', '=', self.date)])
            if holiday_data:
                holiday = True
            if overtime_data and self.employee_id.type_id and self.employee_id.type_id.overtime_calc:
                if holiday and overtime_data and self.min_wage_id.umr_month != 0.00:
                    self.overtime_value = round((self.min_wage_id.umr_month / 173) * overtime_data.holiday, -1)
                elif not holiday and overtime_data and self.min_wage_id.umr_month != 0.00:
                    # check_holiday = self.search([('lhm_id.date','=',self.lhm_id.date),('attendance_id.code','=','PH'),('non_work_day','>',0)])
                    # if check_holiday or (self.attendance_id.type=='na'):
                    if self.attendance_id.overtime_base_value=='jam_kerja_libur':
                        self.overtime_value = round((self.min_wage_id.umr_month / 173) * overtime_data.holiday, -1)
                    else:
                        self.overtime_value = round((self.min_wage_id.umr_month / 173) * overtime_data.normal_day, -1)
                else:
                    self.overtime_value = 0
            if overtime_data and self.employee_id.type_id and not self.employee_id.type_id.overtime_calc:
                if holiday and overtime_data and self.min_wage_id.umr_month != 0.00:
                    self.overtime_value = round((self.min_wage_id.umr_month / 25) * float(float(3)/float(20)) * overtime_data.holiday, -1)
                elif not holiday and overtime_data and self.min_wage_id.umr_month != 0.00:
                    # check_holiday = self.search([('lhm_id.date','=',self.lhm_id.date),('attendance_id.code','=','PH'),('non_work_day','>',0)])
                    # if check_holiday or (self.attendance_id.type=='na'):
                    if self.attendance_id.overtime_base_value=='jam_kerja_libur':
                        self.overtime_value = round((self.min_wage_id.umr_month / 25) * float(float(3)/float(20)) * overtime_data.holiday, -1)
                    else:
                        self.overtime_value = round((self.min_wage_id.umr_month / 25) * float(float(3)/float(20)) * overtime_data.normal_day, -1)
                else:
                    self.overtime_value = 0
        elif self.overtime_hour <= 0 :
            self.overtime_value = 0
class lhm_nab(models.Model):
    _inherit        = 'lhm.nab'
    _description    = 'Nota Angkut Buah'

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'vdata_panen_nab_naf')
        self._cr.execute("""
            CREATE OR REPLACE VIEW "public"."vdata_panen_nab_naf" AS 
             SELECT 'panen'::text AS grp,
                lrb.tgl_panen,
                lpb.afdeling_id,
                lpb.id AS block_id,
                lrb.tgl_panen AS tgl_trans,
                sum(lrb.value) AS jjg_qty
               FROM (lhm_restan_balance lrb
                 LEFT JOIN lhm_plant_block lpb ON ((lpb.id = lrb.block_id)))
              GROUP BY lrb.tgl_panen, lpb.afdeling_id, lpb.id
            UNION ALL
             SELECT 'panen'::text AS grp,
                ltpl.date AS tgl_panen,
                lpb.afdeling_id,
                lpb.id AS block_id,
                ltpl.date AS tgl_trans,
                sum(ltpl.nilai) AS jjg_qty
               FROM (((lhm_transaction lt
                 LEFT JOIN lhm_transaction_process_line ltpl ON ((lt.id = ltpl.lhm_id)))
                 LEFT JOIN lhm_activity la ON ((la.id = ltpl.activity_id)))
                 LEFT JOIN lhm_plant_block lpb ON ((lpb.location_id = ltpl.location_id)))
              WHERE ((la.is_panen IS TRUE) AND ((lt.state)::text = ANY (ARRAY[('done'::character varying)::text, ('close'::character varying)::text])))
              GROUP BY ltpl.date, lpb.afdeling_id, lpb.id
            UNION ALL
             SELECT 'panen'::text AS grp,
                lcl.date AS tgl_panen,
                lpb.afdeling_id,
                lpb.id AS block_id,
                lcl.date AS tgl_trans,
                sum(lcl.nilai) AS jjg_qty
               FROM (((lhm_contractor lc
                 LEFT JOIN lhm_contractor_line lcl ON ((lc.id = lcl.contractor_id)))
                 LEFT JOIN lhm_activity la ON ((la.id = lcl.activity_id)))
                 LEFT JOIN lhm_plant_block lpb ON ((lpb.location_id = lcl.location_id)))
              WHERE (la.is_panen IS TRUE)
              GROUP BY lcl.date, lpb.afdeling_id, lpb.id
            UNION ALL
             SELECT 'nab'::text AS grp,
                lnl.tgl_panen,
                lpb.afdeling_id,
                lnl.block_id,
                ln.date_pks AS tgl_trans,
                (- sum(lnl.qty_nab)) AS jjg_qty
               FROM ((lhm_nab ln
                 LEFT JOIN lhm_nab_line lnl ON ((lnl.lhm_nab_id = ln.id)))
                 LEFT JOIN lhm_plant_block lpb ON ((lpb.id = lnl.block_id)))
              WHERE (((ln.state)::text = ANY (ARRAY[('confirmed'::character varying)::text, ('done'::character varying)::text])) AND (lnl.block_id IS NOT NULL))
              GROUP BY lnl.tgl_panen, lpb.afdeling_id, lnl.block_id, ln.date_pks
            UNION ALL
             SELECT 'naf'::text AS grp,
                lnal.tgl_panen,
                lpb.afdeling_id,
                lnal.block_id,
                lna.date_naf AS tgl_trans,
                (- sum(lnal.qty)) AS jjg_qty
               FROM ((lhm_nab_afkir lna
                 LEFT JOIN lhm_nab_afkir_line lnal ON ((lnal.lhm_nab_afkir_id = lna.id)))
                 LEFT JOIN lhm_plant_block lpb ON ((lpb.id = lnal.block_id)))
              WHERE (((lna.state)::text = ANY (ARRAY[('confirmed'::character varying)::text, ('done'::character varying)::text])) AND (lnal.block_id IS NOT NULL))
              GROUP BY lnal.tgl_panen, lpb.afdeling_id, lnal.block_id, lna.date_naf;
            """)