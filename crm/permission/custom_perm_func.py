def can_add_customer(req,*args,**kwargs):
    if req.resolver_match.kwargs['table_name'] == 'customer':
        print(req.resolver_match.kwargs['table_name'])
        return True
    else:return False

def can_add_user(req, *args, **kwargs):
    if req.resolver_match.kwargs['table_name'] == 'userprofile':
        return True
    else:
        return False