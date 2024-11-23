{
    'name': 'Hotel Hall Invoice',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Manage Hall Invoices',
    'description': """
        Module for managing hall invoices
    """,
    'depends': ['base', 'mail', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'reports/hall_invoice_reports.xml',
        'reports/hall_invoice_templates.xml',
        'views/hall_invoice_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
