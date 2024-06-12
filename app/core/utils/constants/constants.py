class Routes:

    """AUTHENTICATION ROUTES"""

    LOGIN = "/login"
    REGISTER = "/register"
    LOGOUT = "/logout"
    SINGLE_USER = "/user/<id>"
    EDIT_USER = "/user/<id>/edit"

    """ADMIN ROUTES """

    ADMIN_USERS = "/users"
    ADMIN_LOGIN = "/worfhijdnd/login"
    ADMIN_DASHBOARD = "/dashbord"

    """DOCUMENTATION ROUTES """
    DOC = "/doc"
    TEST = "/test"

    """INDEX ROUTES"""
    ABOUT = "/about"
    CONTACT = "/contact"

    """APP ROUTES"""
    COMPAIGNS_ALL = "/campaigns"
    CAMPAIGN_CREATE = "/campaigns/create"
    CAMPAIGN_BY_ID = "/campaigns/<id>/"
    CAMPAIGN_STATUS = "/campaigns/<id>/status"
    CAMPAIGN_PUBLISH = "/campaigns/<id>/publish"
    CAMPAIGN_UPDATE = "/campaigns/<id>/update"
    CAMPAIGN_DELETE = "/campaigns/<id>/delete"
    CAMPAIGN_DONATION = "/campaigns/<uuid:id>/donation"
    CAMPAIGN_DONATION_FETCH = "/campaigns/donation/<uuid:campaign_id>"
    CAMPAIGN_DONATION_DELETE = "/campaigns/donation/<id>/delete"
