from odoo import api, fields, models, _
from odoo.exceptions import UserError

class HallInvoice(models.Model):
    _name = 'hall.invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hall Invoice'
    _order = 'date desc, name desc'

    # Private attributes
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Invoice number must be unique!')
    ]

    # Default methods
    @api.model
    def _get_default_currency(self):
        return self.env.company.currency_id

    # Fields
    name = fields.Char(string='Number', readonly=True, copy=False, default='/')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    date = fields.Date(string='Invoice Date', default=fields.Date.context_today, tracking=True)
    start_date = fields.Date(string='Start Date', required=True, tracking=True)
    end_date = fields.Date(string='End Date', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True, copy=False)
    payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
    ], string='Payment Status', default='not_paid', tracking=True, copy=False)
    
    line_ids = fields.One2many('hall.invoice.line', 'invoice_id', string='Invoice Lines', copy=True)
    currency_id = fields.Many2one('res.currency', string='Currency', 
        default=_get_default_currency, required=True)
    
    amount_untaxed = fields.Monetary(string='Untaxed Amount', compute='_compute_amounts', store=True)
    amount_tax = fields.Monetary(string='Tax Amount', compute='_compute_amounts', store=True)
    amount_total = fields.Monetary(string='Total', compute='_compute_amounts', store=True)
    amount_residual = fields.Monetary(string='Amount Due', compute='_compute_amounts', store=True)
    amount_paid = fields.Monetary(string='Amount Paid', compute='_compute_amounts', store=True)

    # Compute and depends methods
    @api.depends('line_ids.price_subtotal', 'line_ids.price_tax')
    def _compute_amounts(self):
        for invoice in self:
            lines = invoice.line_ids
            invoice.amount_untaxed = sum(lines.mapped('price_subtotal'))
            invoice.amount_tax = sum(lines.mapped('price_tax'))
            invoice.amount_total = invoice.amount_untaxed + invoice.amount_tax
            invoice.amount_paid = 0.0  # To be implemented with payment functionality
            invoice.amount_residual = invoice.amount_total - invoice.amount_paid

    # CRUD methods
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('hall.invoice')
        return super().create(vals_list)

    # Action methods
    def action_post(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Only draft invoices can be posted.'))
        if not self.line_ids:
            raise UserError(_('Cannot post an invoice without lines.'))
        self.state = 'posted'

    def action_cancel(self):
        self.ensure_one()
        if self.state == 'posted' and self.payment_state != 'not_paid':
            raise UserError(_('Cannot cancel a paid invoice.'))
        self.state = 'cancelled'

    def action_draft(self):
        self.ensure_one()
        if self.state != 'cancelled':
            raise UserError(_('Only cancelled invoices can be reset to draft.'))
        self.state = 'draft'

    def action_register_payment(self):
        self.ensure_one()
        if self.state != 'posted':
            raise UserError(_('You can only register payments for posted invoices.'))
        if self.payment_state == 'paid':
            raise UserError(_('This invoice is already paid.'))
            
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