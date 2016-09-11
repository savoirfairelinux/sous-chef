# usage : python dataexec.py [santropolFeast.settingsSPECIAL]
import os
import sys


def run():
    if len(sys.argv) > 1:
        settings = sys.argv[1]
    else:
        settings = 'sous-chef.settings'
    os.environ['DJANGO_SETTINGS_MODULE'] = settings
    import django
    django.setup()
    from dataload import insert_all
    insert_all()

run()
