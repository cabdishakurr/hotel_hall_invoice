from odoo import api, fields, models

class HallInvoiceLine(models.Model):
    _name = 'hall.invoice.line'
    _description = 'Hall Invoice Line'

    invoice_id = fields.Many2one('hall.invoice', string='Invoice')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    name = fields.Text(string='Description', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    number_of_days = fields.Integer(string='Number of Days', default=1)
    price_unit = fields.Float(string='Unit Price')
    price_with_days = fields.Float(string='Price with Days', compute='_compute_price_with_days', store=True)
    tax_ids = fields.Many2many('account.tax', string='Taxes')
    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_amounts', store=True)
    price_tax = fields.Monetary(string='Tax Amount', compute='_compute_amounts', store=True)
    price_total = fields.Monetary(string='Total', compute='_compute_amounts', store=True)
    currency_id = fields.Many2one(related='invoice_id.currency_id')

    @api.depends('price_unit', 'number_of_days')
    def _compute_price_with_days(self):
        for line in self:
            line.price_with_days = line.price_unit * line.number_of_days

    @api.depends('quantity', 'price_with_days', 'tax_ids')
    def _compute_amounts(self):
        for line in self:
            price = line.price_with_days * line.quantity
            taxes = line.tax_ids.compute_all(
                price,
                line.currency_id,
                1.0,
                product=line.product_id,
                partner=line.invoice_id.partner_id
            )
            line.price_subtotal = taxes['total_excluded']
            line.price_tax = taxes['total_included'] - taxes['total_excluded']
            line.price_total = taxes['total_included'] 