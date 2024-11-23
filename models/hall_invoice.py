from odoo import api, fields, models

class HallInvoice(models.Model):
    _name = 'hall.invoice'
    _description = 'Hall Invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    date = fields.Date(string='Date', default=fields.Date.today)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    line_ids = fields.One2many('hall.invoice.line', 'invoice_id', string='Invoice Lines')
    amount_untaxed = fields.Monetary(string='Untaxed Amount', compute='_compute_amounts', store=True)
    amount_tax = fields.Monetary(string='Tax Amount', compute='_compute_amounts', store=True)
    amount_total = fields.Monetary(string='Total', compute='_compute_amounts', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('hall.invoice') or 'New'
        return super().create(vals_list)

    def action_post(self):
        """Post the invoice"""
        self.ensure_one()
        if self.state == 'draft':
            self.state = 'posted'
        return True

    def action_cancel(self):
        """Cancel the invoice"""
        self.ensure_one()
        if self.state in ['draft', 'posted']:
            self.state = 'cancelled'
        return True

    def action_draft(self):
        """Reset to draft"""
        self.ensure_one()
        if self.state == 'cancelled':
            self.state = 'draft'
        return True

    @api.depends('line_ids.price_subtotal', 'line_ids.price_tax')
    def _compute_amounts(self):
        for invoice in self:
            invoice.amount_untaxed = sum(invoice.line_ids.mapped('price_subtotal'))
            invoice.amount_tax = sum(invoice.line_ids.mapped('price_tax'))
            invoice.amount_total = invoice.amount_untaxed + invoice.amount_tax 