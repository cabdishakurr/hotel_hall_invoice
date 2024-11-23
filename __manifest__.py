{
    'name': 'Hotel Hall Invoice',
    'version': '1.0',
    'category': 'Accounting/Accounting',
    'summary': 'Hotel Hall Invoice Management',
    'description': """
        Manage hotel hall invoices with:
        - Number of days calculation
        - Price with days computation
        - Custom invoice report
    """,
    'depends': ['account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/hall_invoice_views.xml',
        'reports/hall_invoice_report.xml',
        'data/sequence.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
