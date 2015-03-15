from flask.ext.babel import gettext
name = "Self IP"
description = gettext('Display your source IP address if the query expression is "ip"')
default_on = True


# attach callback to the pre search hook
#  request: flask request object
#  ctx: the whole local context of the pre search hook
def pre_search(request, ctx):
    if ctx['search'].query == 'ip':
        x_forwarded_for = request.headers.getlist("X-Forwarded-For")
        if x_forwarded_for:
            ip = x_forwarded_for[0]
        else:
            ip = request.remote_addr
        ctx['search'].answers.clear()
        ctx['search'].answers.add(ip)
        # return False prevents exeecution of the original block
        return False
    return True
