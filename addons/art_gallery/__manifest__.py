{  
    'name': 'Art Gallery',
    'version': '19.0.1.0.1',
    'summary': 'Browse and import artworks from a public API',
    'description': 'A simple gallery module that displays artworks fetched from an external API.',
    'author': 'DeepFelipe',
    'website': 'https://example.com',
    'category': 'Tools',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_artworks_wizard_views.xml',
        'views/artwork_views.xml',
        'views/dashboard_views.xml',
        'views/art_gallery_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'art_gallery/static/src/js/dashboard.js',
            'art_gallery/static/src/xml/dashboard.xml',
            'art_gallery/static/src/css/dashboard.css',
        ],
    },
    'external_dependencies': {
    'python': ['requests'],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}