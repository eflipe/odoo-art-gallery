{
    'name': 'Art App Launcher',
    'version': '19.0.1.0.0',
    'summary': 'Visual app launcher grid (client action)',
    'description': 'Replaces the standard apps dropdown with a visual grid of apps.',
    'author': 'DeepFelipe',
    'website': 'https://example.com',
    'category': 'Tools',
    'depends': ['base', 'web'],
    'data': [
        'views/app_launcher_action.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'art_app_launcher/static/src/js/app_launcher.js',
            'art_app_launcher/static/src/js/home_systray.js',
            'art_app_launcher/static/src/xml/app_launcher.xml',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

