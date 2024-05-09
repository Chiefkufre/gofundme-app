

class Routes:

    """AUTHENTICATION ROUTES """

    LOGIN = '/login'
    REGISTER = '/register'
    LOGOUT = "/logout"
    SINGLE_USER = "/users/<int:id>"
    EDIT_USER = '/users/<int:id>/edit'


    
    """ADMIN ROUTES """

    ADMIN_USERS = 'admin/users'
    ADMIN_LOGIN =  'admin/worfhijdnd/login'
    ADMIN_DASHBOARD = 'admin/dashbord'


    """DOCUMENTATION ROUTES """
    DOC = "/doc"
    TEST = "/test"

    """APP ROUTES"""
    COMPAIGNS_ALL = "/campaigns/"
    CAMPAIGN_CREATE = "/campaigns/create"
    CAMPAIGN_BY_ID = "/campaigns/<int:id>/"
    CAMPAIGN_STATUS = "/campaigns/<int:id>/status"
    CAMPAIGN_PUBLISH = "/campaigns/<int:id>/publish"
    CAMPAIGN_UPDATE  = "/campaigns/<int:id>/update"
    CAMPAIGN_DELETE = "/campaigns/<int:id>/delete"
    CAMPAIGN_DONATION = "/campaigns/<int:id>/donation"
    CAMPAIGN_DONATION_FETCH = "/campaigns/donation/<int:campaign_id>/"
    CAMPAIGN_DONATION_DELETE = "/campaigns/donation/<int:id>/delete"