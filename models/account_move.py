from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    number_of_days = fields.Integer(string='Number of Days', default=1)

    @api.depends('quantity', 'number_of_days', 'discount', 'price_unit', 'tax_ids', 'currency_id')
    def _compute_price_subtotal(self):
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_ids.compute_all(price, line.currency_id, line.quantity * line.number_of_days, product=line.product_id, partner=line.partner_id)
            line.price_subtotal = taxes['total_excluded']
            line.price_total = taxes['total_included']

    @api.onchange('quantity', 'number_of_days', 'discount', 'price_unit', 'tax_ids')
    def _onchange_price_subtotal(self):
        return self._compute_price_subtotal()

