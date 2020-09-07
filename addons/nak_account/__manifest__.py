# -*- coding: utf-8 -*-
######################################################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2018  Konsaltén Indonesia (Consult10 Indonesia) <www.consult10indonesia.com>
#   @author Deby Wahyu Kurdian <deby.wahyu.kurdian@gmail.com>
#   For more details, check COPYRIGHT and LICENSE files
#
######################################################################################################

{
    'name'      : "Accounting Module for Agri Sentra Lestari",
    'category'  : 'Plantation',
    'version'   : '1.0.0.1',
    'author'    : "Konsaltén Indonesia (Consult10 Indonesia)",
    'website'   : "www.consult10indonesia.com",
    'license'   : 'AGPL-3',
    'depends'   : ['base', 'c10i_base', 'c10i_account' ,'c10i_lhm', 'account_operating_unit', 'nak_base'],
    'summary'   : """
                        NAK Accounting Module - C10i
                    """,
    'description'   : """
                        Customize Modul Accounting NAK.
                    """,
    'data'      : [
            'security/head_office_security.xml',
            'wizard/wizard_general_ledger_account_view.xml',
            'views/res_partner_views.xml',
            'views/account_views.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
}
