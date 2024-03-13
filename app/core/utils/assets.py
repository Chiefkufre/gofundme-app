from flask_assets import Environment, Bundle


bundles = {
    "doc_js": Bundle(
        # "js/api.js", 
        "js/api/jquery.min.js",
        "js/api/bootstrap.bundle.min.js",
        "js/api/highlight.min.js",
        "js/api/jquery.easing.min.js",
        "js/api/jquery.magnific-popup.min.js",
        "js/api/theme.js",
        output="gen/doc.js"),


    "doc_css": Bundle(
        # "css/api.css",
        "css/api/bootstrap.min.css",
        "css/api/all.min.css",
        "css/api/magnific-popup.min.css",
        "css/api/github.css",
        "css/api/stylesheet.css",
        output="gen/doc.css"),



    "request_js": Bundle(
        "js/fetchRequest.js", "js/postRequest.js", output="gen/request.js"
    ),

    "frontend_css": Bundle(
         "css/frontend/bootstrap.min.css", 
        "css/frontend/owl.carousel.min.css", 
        "css/frontend/animate.css",
        "css/frontend/magnific-popup.css", 
        "css/frontend/all.min.css",
        "css/frontend/flaticon.css", 
        "css/frontend/font.css",
        "css/frontend/themify-icons.css",
        "css/frontend/metisMenu.css",
        "css/frontend/nice-select.css",
        "css/frontend/slick.css",
        "css/frontend/main.css",
        output="gen/frontend.css"
    ),

   

    "frontend_js": Bundle (
        "js/frontend/vendor/jquery-1.12.4.min.js",
        "js/frontend/popper.min.js",
        "js/frontend/bootstrap.min.js",
        "js/frontend/owl.carousel.min.js",
        "js/frontend/isotope.pkgd.min.js",
        "js/frontend/slick.min.js",
        "js/frontend/jquery.meanmenu.min.js",
        "js/frontend/metisMenu.min.js",
        "js/frontend/jquery.nice-select.js",
        "js/frontend/ajax-form.js",
        "js/frontend/wow.min.js",
        "js/frontend/jquery.counterup.min.js",
        "js/frontend/waypoints.min.js",
        "js/frontend/jquery.scrollUp.min.js",
        "js/frontend/imagesloaded.pkgd.min.js",
        "js/frontend/jquery.magnific-popup.min.js",
        "js/frontend/jquery.easypiechart.js",
        "js/frontend/tilt.jquery.js",
        "js/frontend/plugins.js",
        "js/frontend/main.js",
        
        output="gen/frontend.js"
    ),
    
    "backend_js": Bundle("js/backend.js", output="gen/backend.js"),
    "backend_css": Bundle("css/backend.css", output="gen/backend.css"),
}


def configure_assets(app):
    assets = Environment(app)
    assets.register(bundles)
    return assets
