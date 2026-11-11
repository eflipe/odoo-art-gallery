{
    'name': 'Art Marketplace',
    'version': '19.0.1.0.0',
    'summary': 'Sell artworks and register sales in accounting',
    'category': 'Sales',
    'author': 'DeepFelipe',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'art_gallery',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/artwork_sale_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}
