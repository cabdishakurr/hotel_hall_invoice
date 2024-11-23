from odoo import api, fields, models

class HallInvoiceLine(models.Model):
    _name = 'hall.invoice.line'
    _description = 'Hall Invoice Line'

    invoice_id = fields.Many2one('hall.invoice', string='Invoice', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    name = fields.Text(string='Description', required=True)
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    number_of_days = fields.Integer(string='Number of Days', default=1, required=True)
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price')
    tax_ids = fields.Many2many('account.tax', string='Taxes')
    
    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_amounts', store=True)
    price_tax = fields.Monetary(string='Tax', compute='_compute_amounts', store=True)
    price_total = fields.Monetary(string='Total', compute='_compute_amounts', store=True)
    currency_id = fields.Many2one(related='invoice_id.currency_id')

    @api.depends('quantity', 'number_of_days', 'price_unit', 'tax_ids')
    def _compute_amounts(self):
        for line in self:
            price = line.price_unit * line.quantity * line.number_of_days
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

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.get_product_multiline_description_sale()
            self.price_unit = self.product_id.list_price