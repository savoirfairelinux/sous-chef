from django import forms
from note.models import Note


class NoteForm(forms.ModelForm):

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
