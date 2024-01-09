from flask_assets import Environment, Bundle


bundles = {

    'api_js': Bundle(
        'js/api.js',
        output='gen/api.js'),

    'api_css': Bundle(
        'css/api.css',
        output='gen/front.css'),

    'front_js': Bundle(
        'js/common.js',
        'js/front.js',
        output='gen/front.js'),

    'front_css': Bundle(
        'css/common.css',
        'css/front.css',
        output='gen/front.css'),

    'admin_js': Bundle(
        'js/common.js',
        'js/admin.js',
        output='gen/admin.js'),

    'admin_css': Bundle(
        'css/common.css',
        'css/admin.css',
        output='gen/admin.css'),

    'dashboard_js': Bundle(
        'js/common.js',
        'js/dashboard.js',
        output='gen/dashboard.js'),

    'dashboard_css': Bundle(
        'css/common.css',
        'css/dashbord.css',
        output='gen/dashboard.css'),
    
}


def configure_assets(app):
    assets = Environment(app)
    assets.register(bundles)
    return assets
