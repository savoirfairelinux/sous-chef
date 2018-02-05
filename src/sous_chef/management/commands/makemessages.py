from django.core.management.commands import makemessages


class Command(makemessages.Command):
    """
    Support argument --add-location of GNU gettext utilities.

    A feature request has been submitted to Django at the time of writing
    this module (Django 1.11rc1). If a future Django version supports this
    argument, we can then safely remove this module.

    Ref: https://groups.google.com/forum/#!topic/django-developers/IkrjfBDA7iE
    """

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--add-location',
            action='store',
            default='full',
            type=str,
            choices=['full', 'file', 'never'],
            help='If full, generates the location lines with both file name '
                 'and line number. If file, the line number part is omitted. '
                 'If never, completely suppresses the lines '
                 '(same as --no-location).',
            dest='add_location',
        )

    def handle(self, *args, **options):
        add_location = options.pop('add_location')
        arg_str = "--add-location={}".format(add_location)
        self.msgmerge_options = (
            makemessages.Command.msgmerge_options[:] + [arg_str]
        )
        self.msguniq_options = (
            makemessages.Command.msguniq_options[:] + [arg_str]
        )
        self.msgattrib_options = (
            makemessages.Command.msgattrib_options[:] + [arg_str]
        )
        self.xgettext_options = (
            makemessages.Command.xgettext_options[:] + [arg_str]
        )

        super(Command, self).handle(*args, **options)
