# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2010-2012 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import netsvc
import pooler, tools
from datetime import datetime
from openerp.osv import orm, fields,osv

class stock_picking_carriage_condition(orm.Model):
    """
    Carriage condition
    """
    _name = "stock.picking.carriage_condition"
    _description = "Carriage Condition"
    _columns = {
        'name':fields.char('Carriage Condition', size=64, required=True, readonly=False),
        'note': fields.text('Note'),
    }

class stock_picking_goods_description(orm.Model):
    """
    Description of Goods
    """
    _name = 'stock.picking.goods_description'
    _description = "Description of Goods"

    _columns = {
        'name':fields.char('Description of Goods', size=64, required=True, readonly=False),
        'note': fields.text('Note'),#tenere na
    }

class stock_picking_reason(orm.Model):
    """
    Reason for Transportation
    """
    _name = 'stock.picking.transportation_reason'
    _description = 'Reason for transportation'
    
    _columns = {
        'name':fields.char('Reason For Transportation', size=64, required=True, readonly=False),
        'note': fields.text('Note'),#da togliere classe
    }

class stock_picking_out(orm.Model):
    _inherit = "stock.picking.out"
    _columns =  {
        'carriage_condition_id': fields.many2one('stock.picking.carriage_condition', 'Carriage condition'),
        'goods_description_id': fields.many2one('stock.picking.goods_description', 'Description of goods'),
        'transportation_reason_id': fields.many2one('stock.picking.transportation_reason', 'Reason for transportation'),
        'ddt_number':  fields.char('DDT', size=64),
        'ddt_date':  fields.date('DDT date'),
        'volume': fields.char('Volume',size=64),
        'note_ddt':fields.text('Note'),
        'invoice_id':fields.many2one('account.invoice','numberDDT',readonly=1),
        'actual_date': fields.date('Data'),
#         'eureka_state':fields.selection((
#                                         ('INVIATO', 'Inviato'),
#                                         ('CONFERMATO', 'Confermato'),
#                                         ),
#                                         'Stato DDT'),
        'ddt_reason':fields.selection((
                                        ('MITTENTE', 'Mittente'),
                                        ('DESTINATARIO', 'Destinatario'),
                                        ('VETTORE', 'Vettore'),
                                        ),
                                        'Trasporto a Cura di'),
    
        'delivery_address':  fields.many2one('res.partner',string="Indirizzo di spedizione secondario"),
    }
    def action_invoice_create(self, cursor, user, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        res = super(stock_picking, self).action_invoice_create(cursor, user, ids, journal_id,
            group, type, context)
   #     for picking in self.browse(cursor, user, ids, context=context):
   #         self.pool.get('account.invoice').write(cursor, user, res[picking.id], {
   #             'carriage_condition_id': picking.carriage_condition_id.id,
    #            'goods_description_id': picking.goods_description_id.id,
    #            'transportation_reason_id': picking.transportation_reason_id.id,
    #            })
        return res

    #-----------------------------------------------------------------------------
    # EVITARE LA COPIA DI 'NUMERO DDT'
    #-----------------------------------------------------------------------------
    def copy(self, cr, uid, ids, default={}, context=None):
        default.update({'ddt_number': ''})
        return super(stock_picking_out, self).copy(cr, uid, ids, default, context)
    
    def getLastDDtDate(self,cr,uid):
        """
            get last ddt date from all ddt
        """
        
        sql="""SELECT ddt_number,ddt_date FROM STOCK_PICKING WHERE DDT_NUMBER IS NOT NULL ORDER BY DDT_DATE DESC;""" 
        cr.execute(sql)
        results=cr.dictfetchall()
        for result in results:
            return datetime.strptime(result.get('ddt_date','2000-01-01'),'%Y-%m-%d')
        return datetime.strptime('2000-01-01','%Y-%m-%d')
        
    def button_ddt_number(self,cr, uid, ids, vals,context=None):
        lastDDtDate=self.getLastDDtDate(cr,uid)
        for brwsPick in self.browse(cr,uid,ids,context=context):
            if brwsPick.ddt_date==False:
                dateTest=datetime.now()
                self.write(cr, uid, [brwsPick.id], {'ddt_date': str(dateTest.strftime('%Y-%m-%d'))})
            else:
                dateTest=datetime.strptime(brwsPick.ddt_date,'%Y-%m-%d')
            if brwsPick.ddt_number==False or len(str(brwsPick.ddt_number))==0:
                if lastDDtDate>dateTest:
                    raise osv.except_osv(('Error'),("Impossibile staccare il ddt data antecedente all'ultimo ddt"))
                number= self.pool.get('ir.sequence').get(cr, uid, 'stock.ddt')
                self.write(cr, uid, [brwsPick.id], {'ddt_number':number})
        return True

# Redefinition of the new fields in order to update the model stock.picking in the orm
# FIXME: this is a temporary workaround because of a framework bug (ref: lp996816).
# It should be removed as soon as
# the bug is fixed

class stock_picking(orm.Model):
    _inherit = 'stock.picking'
    _columns =  {
        'carriage_condition_id': fields.many2one('stock.picking.carriage_condition', 'Carriage condition'),
        'goods_description_id': fields.many2one('stock.picking.goods_description', 'Description of goods'),
        'transportation_reason_id': fields.many2one('stock.picking.transportation_reason', 'Reason for transportation'),
        'ddt_number':  fields.char('DDT', size=64),
        'ddt_date':  fields.date('DDT date'),
        'volume': fields.char('Volume',size=64),
        'note_ddt':fields.text('Note'),
        'actual_date': fields.date('Data'),
        'invoice_id':fields.many2one('account.invoice','numberDDT'),
#         'eureka_state':fields.selection((
#                                         ('INVIATO', 'Inviato'),
#                                         ('CONFERMATO', 'Confermato'),
#                                         ),
#                                         'Stato DDT'),
        'ddt_reason':fields.selection((
                                        ('MITTENTE', 'Mittente'),
                                        ('DESTINATARIO', 'Destinatario'),
                                        ('VETTORE', 'Vettore'),
                                        ),
                                        'Trasporto a Cura di'),
        'delivery_address':  fields.many2one('res.partner',string="Indirizzo di spedizione secondario"),
    }
