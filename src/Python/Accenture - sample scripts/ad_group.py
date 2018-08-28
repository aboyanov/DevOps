from pyad import *


pyad.set_defaults(ldap_server="directory.accenture.com", username="username", password="password")

ou = pyad.adcontainer.ADContainer.from_dn("ou=All_Users, dc=accenture, dc=com")
new_user = ADUser.create("test.user", ou, password="Secret")



#It is also possible to edit users and groups using set_attribute and add users to groups. For example:

new_user.set_attribute("mail", "test.user@accenture.com")
group = ADGroup.from_dn("test_gdpr_user")
group.add_member(new_user)

#And to delete:

#new_user.delete()
