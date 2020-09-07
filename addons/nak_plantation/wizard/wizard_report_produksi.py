from odoo import models, fields, tools, api, _
from datetime import datetime
import time
import datetime

class WizardReportProduksi(models.TransientModel):
    _inherit            = "wizard.report.produksi"
    _description        = "Laporan Produksi"

    @api.multi
    def create_report(self):
        # Laporan Panen
        if self.panen_ids:
            for data in self.panen_ids:
                data.unlink()
        
        str_sql1 = """
            select
            hf.code AS name  
            ,ltpl.date
            ,ltpl.location_id
            ,ltpl.uom_id
            ,ltpl.nilai
            ,ltpl.uom2_id
            ,ltpl.nilai2
            ,ltpl.realization
            ,ltpl.work_day
            ,lpb.afdeling_id
            FROM lhm_transaction lt
            LEFT JOIN lhm_transaction_process_line ltpl ON lt.id=ltpl.lhm_id
            LEFT JOIN hr_foreman hf on hf.id=lt.kemandoran_id
            LEFT JOIN lhm_activity la on la.id=ltpl.activity_id
            LEFT JOIN lhm_plant_block lpb on lpb.location_id=ltpl.location_id
            where la.is_panen is True and ltpl.date between %s and %s and state in('done','close')            
        """

        str_sql2 = """
            SELECT 
            rp.name AS name
            ,lcl.date
            ,lcl.location_id
            ,lcl.uom_id
            ,lcl.nilai
            ,lcl.uom2_id
            ,lcl.nilai2
            ,lcl.total
            ,(0) work_day
            ,lpb.afdeling_id
            FROM lhm_contractor lc
            LEFT JOIN lhm_contractor_line lcl ON lc.id=lcl.contractor_id
            LEFT JOIN res_partner rp on rp.id=lc.supplier_id
            LEFT JOIN lhm_activity la on la.id=lcl.activity_id
            LEFT JOIN lhm_plant_block lpb on lpb.location_id=lcl.location_id
            where la.is_panen is True and lcl.date between %s and %s 
        """

        str_sql3 = ''
        if self.afdeling_ids:
            str_afdeling_id = ''
            for data in self.afdeling_ids:
                str_afdeling_id += str(data.id)+","
            str_sql3 = ' and lpb.afdeling_id in ('+str_afdeling_id[:-1]+')'

        str_sql = str_sql1 + str_sql3+' union all' + str_sql2 + str_sql3 + ' order by 2 , 1 '
        self.env.cr.execute(str_sql, (self.date_start, self.date_end, self.date_start, self.date_end))

        for report in self.env.cr.fetchall():
            new_lines = {
                'name'          : report[0],
                'date'          : report[1],
                'location_id'   : report[2],
                'uom_id'        : report[3],
                'nilai'         : report[4],
                'uom_id2'       : report[5],
                'nilai2'        : report[6],
                'total'         : report[7],
                'hk'            : report[8],
                'afdeling_id'   : report[9],
                'produksi_id': self.id,
            }
            if new_lines:
                self.env['wizard.report.produksi.panen'].create(new_lines)

        #Laporan NAB Detail
        if self.nab_detail_ids:
            for data in self.nab_detail_ids:
                data.unlink()

        str_sql = """
            SELECT
            date_nab,
            no_nab,
            ln.afdeling_id,
            lnl.block_id,
            lnl.qty_nab,
            tgl_panen,
            ((lnl.qty_nab*lb.value)/(sum(lnl.qty_nab*lb.value) over (partition by ln.id))*ln.timbang_tara_kbn) as kbn_kg,
            ((lnl.qty_nab*lb.value)/(sum(lnl.qty_nab*lb.value) over (partition by ln.id))*timbang_tara_kbn)/lnl.qty_nab as kbn_bjr,
            date_pks,
            ((lnl.qty_nab*lb.value)/(sum(lnl.qty_nab*lb.value) over (partition by ln.id))*timbang_tara_pks) as pks_kg,
            ((lnl.qty_nab*lb.value)/(sum(lnl.qty_nab*lb.value) over (partition by ln.id))*grading) as pks_grading,
            ((lnl.qty_nab*lb.value)/(sum(lnl.qty_nab*lb.value) over (partition by ln.id))*netto) as netto,
            ((lnl.qty_nab*lb.value)/(sum(lnl.qty_nab*lb.value) over (partition by ln.id))*netto /lnl.qty_nab) as pks_bjr,
            ln.id as nab_id
            from lhm_nab ln
            LEFT JOIN lhm_nab_line lnl ON lnl.lhm_nab_id=ln."id"
            LEFT JOIN lhm_bjr lb ON lb.block_id=lnl.block_id
            where date_pks between %s and %s and state in('confirmed','done') and lnl.block_id is not null
        """
        str_sql2 = ''
        if self.afdeling_ids:
            str_afdeling_id = ''
            for data in self.afdeling_ids:
                str_afdeling_id += str(data.id)+","
            str_sql2 = ' and afdeling_id in ('+str_afdeling_id[:-1]+')'

        str_sql = str_sql + str_sql2 + ' order by ln.id,lnl.id '
        self.env.cr.execute(str_sql, (self.date_start, self.date_end))

        for report in self.env.cr.fetchall():
            new_lines = {
                'tgl_nab'       : report[0] ,
                'no_nab'        : report[1],
                'afdeling_id'   : report[2],
                'block_id'      : report[3],
                'kbn_qty_jjg'   : report[4],
                'tgl_panen'     : report[5],
                'kbn_qty_kg'    : report[6],
                'kbn_bjr'       : report[7],
                'pks_tgl'       : report[8],
                'pks_bruto'     : report[9],
                'pks_grading'   : report[10],
                'pks_netto'     : report[11],
                'pks_bjr'       : report[12],
                'nab_id'        : report[13],
                'produksi_id'     : self.id,
            }
            if new_lines:
                self.env['wizard.report.produksi.nab.detail'].create(new_lines)

        # Laporan NAB Rekap
        if self.nab_rekap_ids:
            for data in self.nab_rekap_ids:
                data.unlink()

        str_sql = """
            SELECT
            date_nab as tgl_nab,
            no_nab,
            afdeling_id,
            vehicle_id,
            driver,
            ownership,
            date_nab as tgl_nab2,
            janjang_jml as kbn_qty_jjg,
            timbang_tara_kbn as kbn_qty_kg,
            pks_id,
            date_pks as pks_tgl,
            timbang_tara_pks as pks_bruto,
            grading as pks_grading,
            netto as pks_netto,
            id as nab_id
            from lhm_nab
            where date_pks between %s and %s and state in('confirmed','done')
        """

        str_sql2 = ''
        if self.afdeling_ids:
            str_afdeling_id = ''
            for data in self.afdeling_ids:
                str_afdeling_id += str(data.id) + ","
            str_sql2 = ' and afdeling_id in (' + str_afdeling_id[:-1] + ')'

        str_sql = str_sql + str_sql2 + ' order by date_pks,no_nab '
        self.env.cr.execute(str_sql, (self.date_start, self.date_end))

        for report in self.env.cr.fetchall():
            new_lines = {
                'tgl_nab'       : report[0],
                'no_nab'        : report[1],
                'afdeling_id'   : report[2],
                'vehicle_id'    : report[3],
                'driver'        : report[4],
                'ownership'     : report[5],
                'tgl_nab2'      : report[6],
                'kbn_qty_jjg'   : report[7],
                'kbn_qty_kg'    : report[8],
                'pks_id'        : report[9],
                'pks_tgl'       : report[10],
                'pks_bruto'     : report[11],
                'pks_grading'   : report[12],
                'pks_netto'     : report[13],
                'nab_id'        : report[14],
                'produksi_id'   : self.id,
            }
            if new_lines:
                self.env['wizard.report.produksi.nab.rekap'].create(new_lines)

        # Laporan NAB PerBlock
        if self.nab_perblock_ids:
            for data in self.nab_perblock_ids:
                data.unlink()

        str_sql = """
                select lpb.afdeling_id,
                wrpnd.block_id,
                sum(case when pks_tgl = wrp.date_end then kbn_qty_kg else 0 end) kbn_hi_kg,
                sum(case when pks_tgl between wrp.date_start and wrp.date_end then kbn_qty_kg else 0 end) kbn_shi_kg,
                sum(case when pks_tgl = wrp.date_end then kbn_qty_jjg else 0 end) kbn_hi_jjg,
                sum(case when pks_tgl between wrp.date_start and wrp.date_end then kbn_qty_jjg else 0 end) kbn_shi_jjg,
                sum(case when pks_tgl = wrp.date_end then pks_bruto else 0 end) pks_hi_bruto,
                sum(case when pks_tgl between wrp.date_start and wrp.date_end then pks_bruto else 0 end) pks_shi_bruto,
                sum(case when pks_tgl = wrp.date_end then pks_grading else 0 end) pks_hi_grading,
                sum(case when pks_tgl between wrp.date_start and wrp.date_end then pks_grading else 0 end) pks_shi_grading,
                sum(case when pks_tgl = wrp.date_end then pks_netto else 0 end) pks_hi_netto,
                sum(case when pks_tgl between wrp.date_start and wrp.date_end then pks_netto else 0 end) pks_shi_netto
                from wizard_report_produksi_nab_detail wrpnd
                left join wizard_report_produksi wrp on wrp.id=wrpnd.produksi_id
                left join lhm_plant_block lpb on lpb.id=wrpnd.block_id
                left join res_afdeling ra on ra.id=lpb.afdeling_id
                where produksi_id=%s
                group by lpb.afdeling_id, wrpnd.block_id, ra.code, lpb.code
                order by  ra.code, lpb.code
            """

        self.env.cr.execute(str_sql, (self.id,))

        kbn_hi_bjr = 0
        kbn_shi_bjr = 0
        pks_hi_bjr = 0
        pks_shi_bjr = 0
        for report in self.env.cr.fetchall():
            if report[4]:
                kbn_hi_bjr = report[2]/report[4]
            if report[5]:
                kbn_shi_bjr = report[3]/report[5]
            if report[4]:
                pks_hi_bjr = report[10]/report[4]
            if report[5]:
                pks_shi_bjr = report[11]/report[5]

            new_lines = {
                'afdeling_id'   : report[0],
                'block_id'      : report[1],
                'kbn_hi_kg'     : report[2],
                'kbn_shi_kg'    : report[3],
                'kbn_hi_jjg'    : report[4],
                'kbn_shi_jjg'   : report[5],
                'kbn_hi_bjr'    : kbn_hi_bjr,
                'kbn_shi_bjr'   : kbn_shi_bjr,
                'pks_hi_bruto'  : report[6],
                'pks_shi_bruto' : report[7],
                'pks_hi_grading': report[8],
                'pks_shi_grading':report[9],
                'pks_hi_netto'  : report[10],
                'pks_shi_netto' : report[11],
                'pks_hi_bjr'    : pks_hi_bjr,
                'pks_shi_bjr'   : pks_shi_bjr,
                'produksi_id'   : self.id,
            }
            if new_lines:
                self.env['wizard.report.produksi.nab.perblock'].create(new_lines)

        #Laporan Restan
        if self.restan_ids:
            for data in self.restan_ids:
                data.unlink()

        str_sql = """
            select header.tgl_panen
            ,header.block_id
            ,header.qty_saw
            ,header.qty_panen
            ,header.qty_nab
            ,header.qty_naf
            ,header.qty_restan
            ,case when header.qty_restan = 0 then 0 else header.umur_restan end as umur_restan
            ,detail.tgl_trans
            ,detail.qty_nab2
            ,detail.qty_naf2
            from
            (select tgl_panen,block_id,sum(qty_saw) as qty_saw,sum(qty_panen)qty_panen,sum(qty_nab)qty_nab,sum(qty_naf)qty_naf,
            sum(qty_saw+qty_panen-qty_nab-qty_naf)qty_restan,
            date_part('day',%s::timestamp - tgl_panen::timestamp) umur_restan
            from
            (select tgl_panen,block_id,sum(jjg_qty) as qty_saw,(0)qty_panen,(0)qty_nab,(0)qty_naf
            from vdata_panen_nab_naf vpnn
            where tgl_trans < %s and jjg_qty <>0
            group by tgl_panen,block_id
            having sum(jjg_qty)<>0
            union all
            select tgl_panen,block_id,(0)qty_saw
            ,sum(case when grp='panen' and tgl_trans between %s and %s then jjg_qty else 0 end) as qty_panen
            ,sum(case when grp='nab' and tgl_trans between %s and %s then -jjg_qty else 0 end) as qty_nab
            ,sum(case when grp='naf' and tgl_trans between %s and %s then -jjg_qty else 0 end) as qty_naf
            from vdata_panen_nab_naf vpnn
            where tgl_trans between %s and %s and jjg_qty <>0
            group by tgl_panen,block_id
            having sum(jjg_qty)<>0) dat_saw_trans
            group by tgl_panen,block_id) header
            left join
            (select tgl_panen,block_id,tgl_trans
            ,sum(case when grp='nab' and tgl_trans between %s and %s then -jjg_qty else 0 end) as qty_nab2
            ,sum(case when grp='naf' and tgl_trans between %s and %s then -jjg_qty else 0 end) as qty_naf2
            from vdata_panen_nab_naf
            where grp<>'panen' and tgl_trans between %s and %s and jjg_qty <>0
            group by tgl_panen,block_id,tgl_trans,grp) detail
            on header.tgl_panen=detail.tgl_panen and header.block_id=detail.block_id
            order by header.tgl_panen,header.block_id,detail.tgl_trans
        """

        self.env.cr.execute(str_sql, (self.date_end,self.date_start,
              self.date_start, self.date_end,
              self.date_start, self.date_end,
              self.date_start, self.date_end,
              self.date_start, self.date_end,
              self.date_start, self.date_end,
              self.date_start, self.date_end,
              self.date_start, self.date_end,))

        no_urut = 0
        xtgl_panen = False
        xblock_id = False

        for report in self.env.cr.fetchall():
            if (xtgl_panen == report[0] and xblock_id == report[1]):
                no_urut = no_urut
            else:
                no_urut += 1

            xtgl_panen = report[0]
            xblock_id = report[1]

            new_lines = {
                'tgl_panen'     : xtgl_panen or False,
                'block_id'      : xblock_id or False,
                'qty_saw'       : report[2] or False,
                'qty_panen'     : report[3] or False,
                'qty_nab'       : report[4] or False,
                'qty_naf'       : report[5] or False,
                'qty_restan'    : report[6] or False,
                'umur_restan'   : report[7] or False,
                'tgl_trans'     : report[8] or False,
                'qty_nab2'      : report[9] or False,
                'qty_naf2'      : report[10] or False,
                'no_urut'       : no_urut,
                'produksi_id'   : self.id,
            }
            if new_lines:
                new_values_restan = self.env['wizard.report.produksi.restan'].create(new_lines)

        #Laporan Rotasi
        if self.rotasi_ids:
            for data in self.rotasi_ids:
                data.unlink()

        year_now = datetime.datetime.strptime(self.date_end, '%Y-%m-%d').year
        n_day = datetime.datetime.strptime(self.date_end, '%Y-%m-%d').day

        period_id = self.env['account.period'].search([('date_start', '<', self.date_start), ('special', '=', False)], order='date_stop desc', limit=1)

        rotasi_hd = self.env['lhm.rotasi.panen.balance'].search([('period_id', '=', period_id.id)])

        data_block = self.env['lhm.plant.block'].search([('planted', '>', 0.0)], order='code')
        if data_block:
            for block in data_block:
                status = ''
                umur_tbs = year_now - block.year
                if umur_tbs == 0.0:
                    status = 'TBM-0'
                elif umur_tbs == 1:
                    status = 'TBM-1'
                elif umur_tbs == 2:
                    status = 'TBM-2'
                elif umur_tbs == 3:
                    status = 'TBM-3'
                elif umur_tbs == 4:
                    status = 'TM-1'
                elif umur_tbs == 5:
                    status = 'TM-2'
                elif umur_tbs == 6:
                    status = 'TM-3'
                elif umur_tbs == 7:
                    status = 'TM-4'
                elif umur_tbs == 8:
                    status = 'TM-5'
                else:
                    status = ''

                rotasi_dt = self.env['lhm.rotasi.panen.balance.nomor'].search([('block_id', '=', block.id),
                                                                               ('nomor_id', '=', rotasi_hd.id)])

                new_lines = {
                    'afdeling_id' : block.afdeling_id.id,
                    'section'     : block.section,
                    'block_id'    : block.id,
                    'luas'        : block.planted,
                    'pokok'       : block.total_plant,
                    'sph'         : block.total_plant/block.planted,
                    'status'      : status,
                    't00'         : rotasi_dt.value or False,
                    'produksi_id' : self.id,
                }

                if new_lines:
                    self.env['wizard.report.produksi.rotasi.panen'].create(new_lines)


        #Flag Panen dari LHM range tgl
        str_sql = """
            select
            ltpl.date as tgl_panen
            ,lpb.id as block_id
            FROM lhm_transaction lt
            LEFT JOIN lhm_transaction_process_line ltpl ON lt.id=ltpl.lhm_id
            left join lhm_plant_block lpb on lpb.location_id=ltpl.location_id
            LEFT JOIN lhm_activity la on la.id=ltpl.activity_id
            where la.is_panen is True and ltpl.date between %s and %s and state in ('done','close')
            group by ltpl.date,lpb.id
            order by lpb.id,ltpl.date
        """
        self.env.cr.execute(str_sql, (self.date_start, self.date_end))

        old_grp_block = 0
        old_tgl_panen = False
        val_panen = 0
        sel_tgl = 0
        for flag_panen in self.env.cr.fetchall():
            if flag_panen:
                if flag_panen[1] != old_grp_block:
                    val_panen = 1
                    old_tgl_panen = flag_panen[0]
                else:
                    sel_tgl = abs((datetime.datetime.strptime(flag_panen[0], '%Y-%m-%d') - datetime.datetime.strptime(
                        old_tgl_panen, '%Y-%m-%d')).days)

                    if sel_tgl < 4:
                        val_panen = 2
                    else:
                        val_panen = 3
                        old_tgl_panen = flag_panen[0]

                old_grp_block = flag_panen[1]
                str_tgl = datetime.datetime.strptime(flag_panen[0], '%Y-%m-%d').strftime('%d')
                str_sql = """
                    update wizard_report_produksi_rotasi_panen set t""" + str_tgl + """= %s where block_id = %s and produksi_id = %s;
                    update wizard_report_produksi_rotasi_panen set z""" + str_tgl + """= %s where block_id = %s and produksi_id = %s;
                """
                self.env.cr.execute(str_sql, (val_panen, old_grp_block, self.id, val_panen, old_grp_block, self.id))

        data_rotasi = self.env['wizard.report.produksi.rotasi.panen'].search([('produksi_id', '=', self.id)],)

        col_names = ['z01','z02', 'z03','z04','z05','z06','z07','z08','z09','z10','z11','z12','z13','z14','z15',
                     'z16','z17','z18','z19','z20','z21','z22','z23','z24','z25','z26','z27','z28','z29','z30','z31']

        z_col_names = col_names[:n_day]

        for block in data_rotasi:
            flag_merah = block.t00
            for col in sorted(z_col_names):
                flag_merah += 1
                if eval('block.%s' % col) in (1, 2, 3):
                    flag_merah = 0

                if flag_merah > 10:
                    str_sql = """
                        update wizard_report_produksi_rotasi_panen set """ + col + """ = 4 where block_id = %s and produksi_id = %s;
                    """
                    self.env.cr.execute(str_sql, (block.block_id.id, self.id))


        col_names = ['t01','t02', 't03','t04','t05','t06','t07','t08','t09','t10','t11','t12','t13','t14','t15',
                     't16','t17','t18','t19','t20','t21','t22','t23','t24','t25','t26','t27','t28','t29','t30','t31']

        z_col_names = col_names[:n_day]

        data_block = {}
        for block in data_rotasi:
            if block.block_id.id not in data_block.keys():
                data_block.update({block.block_id.id: dict(map(lambda x: (x, 0), col_names))})
                op = block.t00
                for col in sorted(z_col_names):
                    try:
                        op += 1
                        if eval('block.%s'%col) in (1, 3):
                            data_block[block.block_id.id][col] = 1
                            op = 1
                        else:
                            data_block[block.block_id.id][col] = op
                    except:
                        continue

                block.write(data_block[block.block_id.id])

class WizardReportProduksiPanen(models.TransientModel):
    _inherit        = 'wizard.report.produksi.panen'
    _description    = 'Laporan Panen'

    name            = fields.Char(string="Kemandoran/Kontraktor", readonly=True)
    afdeling_id     = fields.Many2one(comodel_name="res.afdeling", string="Afdeling", ondelete="restrict", readonly=True)