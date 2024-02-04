from flask_rbac import RBAC, Permission



# Define permissions
create_permission = Permission("create")
read_permission = Permission("read")
update_permission = Permission("update")
delete_any_campaign_permission = Permission("delete_any_campaign")
delete_own_campaign_permission = Permission("delete_own_campaign")

# Define roles with associated permissions
admin_role = Role("admin", [
    create_permission,
    read_permission,
    update_permission,
    delete_any_campaign_permission
])

user_role = Role("user", [
    read_permission,
    update_permission,
    delete_own_campaign_permission
])