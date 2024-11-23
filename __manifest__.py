{
    'name': 'Hotel Hall Invoice',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Hall Invoicing System',
    'description': """
        Manage hall invoices with number of days calculation
    """,
    'depends': ['account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/hall_invoice_views.xml',
        'reports/hall_invoice_reports.xml',
        'reports/hall_invoice_templates.xml',
        'data/sequence.xml',
    ],
    'installable': True,
    'application': True,
}
