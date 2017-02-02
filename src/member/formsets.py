from django.forms import formset_factory
from .forms import ClientEmergencyContactInformation


CreateEmergencyContactFormset = formset_factory(
    ClientEmergencyContactInformation, extra=1
)
UpdateEmergencyContactFormset = formset_factory(
    ClientEmergencyContactInformation, extra=0
)
