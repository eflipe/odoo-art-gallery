{  
    'name': 'Art Gallery',
    'version': '19.0.1.0.1',
    'summary': 'Browse and import artworks from a public API',
    'description': 'A simple gallery module that displays artworks fetched from an external API.',
    'author': 'DeepFelipe',
    'website': 'https://example.com',
    'category': 'Tools',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/artwork_views.xml',
        'views/art_gallery_menus.xml',
    ],
    'external_dependencies': {
    'python': ['requests'],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}