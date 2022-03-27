{
    # Module Information
    'name' : 'Leave Portal',
    'category' : 'Website',
    'version' : '1.0',
    'license': 'LGPL-3',
    'summary': 'Portal user can manage leaves from Website Portal',
    'description': """
        Portal user can manage leaves from Website Portal
    """,

    # Dependencies
    'depends': [
        'website',
        'portal',
        'hr_holidays',
    ],

    # Views
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/templates.xml',
        'views/subordinates_leaves.xml',
        'views/subordinates_allocations.xml',
    ],

    # Author
    'author': 'NETLINKS LTD',
    'website': 'www.netlinks.af',

    # Technical
    'installable': True,
}
