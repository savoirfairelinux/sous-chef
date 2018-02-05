# -*- coding: utf-8 -*-

import rules
from rules.predicates import is_authenticated
from rules.predicates import is_staff
from rules.predicates import is_superuser


# Note: only two global "permissions" are considered in this project for now.
# "read" and "edit". Should fine-grained permissions be needed, these basic
# permissions should be removed and replaced by permissions associated with
# each app.
rules.add_perm('sous_chef.edit', is_authenticated & is_superuser)
rules.add_perm('sous_chef.read', is_authenticated & is_staff)
