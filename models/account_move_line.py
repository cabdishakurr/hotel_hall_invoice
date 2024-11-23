from odoo import api, fields, models

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    number_of_days = fields.Integer(string='Number of Days', default=1)
    price_with_days = fields.Monetary(string='Price with Days', compute='_compute_price_with_days', store=True)

    @api.depends('price_unit', 'number_of_days')
    def _compute_price_with_days(self):
        for line in self:
            line.price_with_days = line.price_unit * line.number_of_days

    @api.depends('quantity', 'number_of_days', 'discount', 'price_unit', 'tax_ids', 'currency_id')
    def _compute_price_subtotal(self):
        for line in self:
            price = line.price_with_days * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_ids.compute_all(
                price, 
                line.currency_id,
                line.quantity,
                product=line.product_id,
                partner=line.partner_id
            )
            line.price_subtotal = taxes['total_excluded']
            line.price_total = taxes['total_included']

    @api.onchange('quantity', 'number_of_days', 'discount', 'price_unit', 'tax_ids')
    def _onchange_price_subtotal(self):
        return self._compute_price_subtotal()
