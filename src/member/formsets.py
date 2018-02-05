from django.forms import formset_factory
from .forms import ClientRelationshipInformation


CreateRelationshipFormset = formset_factory(
    ClientRelationshipInformation, min_num=0, extra=0
)
UpdateRelationshipFormset = formset_factory(
    ClientRelationshipInformation, min_num=0, extra=0
)
