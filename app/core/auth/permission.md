This is what i want to achieve

1. Create a permission package for the flask app
2. The application will have the following roles
            SUPER_ADMIN = "super_admin"
            ADMIN = 'admin'
            USER = 'user'
            MODERATOR = 'moderator'
            OWNER = 'owner'
    
    Explanation of roles

    A super admin can perform all responsibilities in this system inck=luding but not limited to
        - deleting all other accounts with other roles except super admin
        - edit, delete or patch resources such as campaigns, etc
        - promote users from one role to the other
    
    An admin can perform this responsibilites except deleting a Super admin]

    A Moderator can only change resource status from active to inactive and vice versa

    A user is anyone who creates an account on the platform
        - a user can create a new resource like a campaign
    
    AN owner is someone who create a new resource(Example: campaign)
        - so a new resource should be tied to an owner
        - an owner can edit, delete his resource
        - an only can not change resource status to active or inactive


Create this package for me