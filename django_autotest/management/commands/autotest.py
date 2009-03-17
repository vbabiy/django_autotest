from django.core.management.base import BaseCommand
from optparse import make_option
import sys


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--noinput', action='store_false', dest='interactive', default=False,
            help='Tells Django to NOT prompt the user for input of any kind.'),
    )
    help = 'Runs the test suite for the specified applications, or the entire site if no apps are specified.'
    args = '[appname ...]'

    requires_model_validation = False

    def handle(self, *args, **kargs):
        from django.utils import autoreload
        try:
            autoreload.main(self.test, args, kargs)
        except KeyboardInterrupt, e:
            print e
    
    def test( self, *test_labels, **options):
        from django.conf import settings

        verbosity = int(options.get('verbosity', 1))
        interactive = options.get('interactive', True)

        test_path = settings.TEST_RUNNER.split('.')
        # Allow for Python 2.5 relative paths
        if len(test_path) > 1:
            test_module_name = '.'.join(test_path[:-1])
        else:
            test_module_name = '.'
        test_module = __import__(test_module_name, {}, {}, test_path[-1])
        test_runner = getattr(test_module, test_path[-1])
        
        failures = test_runner(test_labels, verbosity=verbosity, interactive=interactive)
        self.alert(failures)
            
    def alert(self, failures):
        _pynotify = True
        try:
            import pygtk
            pygtk.require('2.0')
            import pynotify
            import gtk 
            import os
        except ImportError:
            _pynotify = False
        
        if _pynotify:
            pynotify.init("Autotests Results")
            
            # Image URI
            if failures == 0:
                uri = "file://" + os.path.abspath(os.path.join(os.path.dirname(__file__), "pass.png"))
                n = pynotify.Notification("Django Autotest", "All of your test are passing.", uri)
            else:
                uri = "file://" + os.path.abspath(os.path.join(os.path.dirname(__file__), "fail.png"))
                n = pynotify.Notification("Djagno Autotest", "%d test are failing" % (failures,), uri)            

            if not n.show():
                print "Failed to send notification"
