from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta

class HallInvoice(models.Model):
    _name = 'hall.invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hall Invoice'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    date = fields.Date(string='Date', default=fields.Date.today)
    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.today)
    end_date = fields.Date(string='End Date', required=True)
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
    
    payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid')
    ], string='Payment Status', default='not_paid', tracking=True)
    
    amount_paid = fields.Monetary(string='Amount Paid', compute='_compute_amount_paid', store=True)
    amount_residual = fields.Monetary(string='Amount Due', compute='_compute_amount_paid', store=True)
    payment_ids = fields.Many2many('account.payment', string='Payments')

    @api.onchange('start_date', 'end_date')
    def _onchange_dates(self):
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise UserError(_('End date cannot be earlier than start date.'))
            delta = (self.end_date - self.start_date).days + 1
            for line in self.line_ids:
                line.number_of_days = delta

    @api.depends('payment_ids.amount', 'amount_total')
    def _compute_amount_paid(self):
        for invoice in self:
            paid_amount = sum(invoice.payment_ids.mapped('amount'))
            invoice.amount_paid = paid_amount
            invoice.amount_residual = invoice.amount_total - paid_amount
            
            if paid_amount >= invoice.amount_total:
                invoice.payment_state = 'paid'
            elif paid_amount > 0:
                invoice.payment_state = 'partial'
            else:
                invoice.payment_state = 'not_paid'

    @api.depends('line_ids.price_subtotal', 'line_ids.price_tax')
    def _compute_amounts(self):
        for invoice in self:
            invoice.amount_untaxed = sum(invoice.line_ids.mapped('price_subtotal'))
            invoice.amount_tax = sum(invoice.line_ids.mapped('price_tax'))
            invoice.amount_total = invoice.amount_untaxed + invoice.amount_tax

    def action_register_payment(self):
        return {
            'name': _('Register Payment'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': self._name,
                'active_ids': self.ids,
                'default_payment_type': 'inbound',
                'default_partner_type': 'customer',
                'default_partner_id': self.partner_id.id,
                'default_amount': self.amount_residual,
            },
            'target': 'new',
        }