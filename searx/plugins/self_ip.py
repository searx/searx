
name = "Self IP"
description = "Display your source IP address"
default_on = True


def pre_search(request, ctx):
    if ctx['search'].query == 'ip':
        x_forwarded_for = request.headers.getlist("X-Forwarded-For")
        if x_forwarded_for:
            ip = x_forwarded_for[0]
        else:
            ip = request.remote_addr
        ctx['search'].answers.clear()
        ctx['search'].answers.add(ip)
        return False
    return True
