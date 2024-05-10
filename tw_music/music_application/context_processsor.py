from .models import *


def privileges(request):
   
    if request.user.is_authenticated and not request.user.is_superuser:
        user_details = UserDetails.objects.get(user_id=request.user.id)
       
        privileges = []
        roles = []
        for role in user_details.role.all():
            roles.append(role.name)
            for privilege in role.privileges.all():
                privileges.append(privilege.name)
    else:
        privileges = []
        roles = []


    return {'privileges':privileges,'roles':roles}
