# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Hendra Saputra <hendrasaputra0501@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

from odoo import models, fields, tools, api, _
from odoo.exceptions import UserError, ValidationError

class hr_attendance_type(models.Model):
    _inherit = 'hr.attendance.type'

    overtime_base_value = fields.Selection([('jam_kerja_biasa', 'Jam Kerja/Hari Biasa'), ('jam_kerja_libur', 'Jam Kerja/Hari Libur')])