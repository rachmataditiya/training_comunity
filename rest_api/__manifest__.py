{
    'name': 'Odoo Rest API',
    'version': '13.0.0',
    'author': 'Arkana Solusi Digital',
    'category': 'Backend',
    'website': 'https://www.arkana.co.id/',
    'summary': 'Restful Api Service',
    'description': '''''',
    'external_dependencies': {
         #'python': ['pyjwt','simplejson'],
    },
    'depends': ['base','product'],
    'data': [
            'security/ir.model.access.csv',
            'views/refresh_token.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
}
