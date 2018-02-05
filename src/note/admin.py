from django.contrib import admin
from note.models import Note, NotePriority, NoteCategory

# Register your models here.
admin.site.register((Note, NotePriority, NoteCategory))
