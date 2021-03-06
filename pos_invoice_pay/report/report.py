# Copyright 2017 Artyom Losev
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import datetime
from odoo import api, fields, models


class ReportSaleDetails(models.AbstractModel):

    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, configs=False):
        res = super(ReportSaleDetails, self).get_sale_details(date_start=False, date_stop=False, configs=False)

        if date_start:
            date_start = fields.Datetime.from_string(date_start)
        else:
            date_start = datetime.date.today()
        if date_stop:
            date_stop = fields.Datetime.from_string(date_stop)
        else:
            date_stop = datetime.date.today() + datetime.timedelta(days=1, seconds=-1)

        date_stop = max(date_stop, date_start)

        date_start = fields.Datetime.to_string(date_start)
        date_stop = fields.Datetime.to_string(date_stop)

        payments = self.env['account.payment'].search([
            ('payment_date', '>=', date_start),
            ('payment_date', '<=', date_stop),
            ('paid_by_pos', '=', True)
        ])

        res['invoices'] = []
        unique = []
        total = 0.0
        for p in payments:
            if (p.invoice_ids.id not in unique):
                invoice = p.invoice_ids
                cashier = p.cashier
                amount = p.amount if (p.amount <= invoice.amount_total) else invoice.amount_total

                data = {
                    'invoice_no': invoice.number,
                    'so_origin': invoice.origin,
                    'customer': invoice.partner_id.name,
                    'cashier': cashier.name or cashier.partner_id.name,
                    'amount_total': invoice.amount_total,
                    'amount': amount
                }
                res['invoices'].append(data)
                unique.append(p.invoice_ids.id)
                total += amount
        user_currency = self.env.user.company_id.currency_id
        res['total_paid'] = user_currency.round(total)

        return res
