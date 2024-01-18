def deepcopy(inobj):
    outobj = inobj.__class__() # assume default empty constructor OK
    for field_name in inobj.__dict__:
        setattr(outobj, field_name, getattr(inobj, field_name))
    return outobj

        
