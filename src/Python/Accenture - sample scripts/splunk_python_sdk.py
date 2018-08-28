#!/usr/bin/python

import splunklib.client

import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

host = '10.0.31.167'
port = '8089'
username = 'admin'
password = ''


service = splunklib.client.connect(host=host,port=port,username=username,password=password)
#users = service.users.list()
roles = service.roles

#for user in users:
#    print user.name

admin_capabilities = []

for role in roles:
    if role.name == 'admin':
        for cap in role.capabilities:
            admin_capabilities.append(cap)

# create new role
newrole = service.roles.create("gdpr-test-role")
# Import properties from admin role
kwargs = {"imported_roles": ["admin", "can_delete"], "capabilities": admin_capabilities }
newrole.update(**kwargs).refresh()

#for cap in newrole.capabilities:
#    print cap
