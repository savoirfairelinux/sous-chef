from django.forms import formset_factory
from .forms import ClientEmergencyContactInformation


CreateEmergencyContactFormset = formset_factory(
    ClientEmergencyContactInformation, min_num=1, extra=1
)
UpdateEmergencyContactFormset = formset_factory(
    ClientEmergencyContactInformation, min_num=1, extra=0
)
