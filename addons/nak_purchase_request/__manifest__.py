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
    'name'      : "Purchase Request Module for Agri Sentra Lestari",
    'category'  : 'Plantation',
    'version'   : '1.0.0.1',
    'author'    : "Konsaltén Indonesia (Consult10 Indonesia)",
    'website'   : "www.consult10indonesia.com",
    'license'   : 'AGPL-3',
    'depends'   : ['base', 'purchase', 'c10i_base', 'c10i_purchase_request','c10i_purchase', 'c10i_lhm'],
    'summary'   : """
                        NAK Purchase Request Module - C10i
                    """,
    'description'   : """
                        Customize Modul Purchase Request NAK.
                    """,
    'data'      : [
            'data/report_data.xml',
            'views/res_config_views.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
}
