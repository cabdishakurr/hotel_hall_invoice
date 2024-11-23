{
    'name': 'Hotel Hall Invoice',
    'version': '1.0',
    'category': 'Accounting/Accounting',
    'summary': 'Extend invoicing for hotel halls',
    'description': """
This module extends the invoicing functionality for hotel halls.
It adds a 'Number of Days' field and adjusts the subtotal calculation.
    """,
    'depends': ['account'],
    'data': [
        'views/account_move_views.xml',
        'reports/hotel_hall_invoice_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
