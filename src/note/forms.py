from django import forms
from member.models import Client
from note.models import Note


class NoteForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NoteForm, self).__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.all().select_related(
            'member'
        ).only(
            'member__firstname',
            'member__lastname'
        )

    class Meta:
        model = Note
        fields = ['note', 'client', 'priority']

        widgets = {
            'note': forms.Textarea(attrs={'rows': 5}),
            'client': forms.Select(
                attrs={'class': 'ui search dropdown'}
            ),
            'priority': forms.Select(
                attrs={'class': 'ui dropdown'}
            ),
        }
