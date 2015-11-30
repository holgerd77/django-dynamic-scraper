#Stage 2 Update (Python 3)
from __future__ import print_function
from __future__ import unicode_literals
from builtins import str
import datetime
from optparse import make_option
from django.conf import settings
from django.core.mail import mail_admins
from django.core.management import CommandError
from django.core.management.base import BaseCommand
from dynamic_scraper.models import Scraper

class Command(BaseCommand):
    help = 'Checks last item saves of a scraper being older than <num_hours>'
    args = '<num_hours>'
    
    option_list = BaseCommand.option_list + (
        make_option(
            '--only-active',
            action="store_true",
            dest="only_active",
            default=False,
            help="Run scraper save checks only for active scrapers"),
        make_option(
            '--send-admin-mail',
            action="store_true",
            dest="send_admin_mail",
            default=False,
            help="Send report mail to Django admins if last saves are too old"),
    )
    
    
    def handle(self, num_hours, *args, **options):
        mail_to_admins = False
        msg = ''
        try:
            num_hours = int(num_hours)
        except ValueError:
            raise CommandError("Please provide number of hours as an integer value!")
        
        
        for scraper in Scraper.objects.all():
            if not (options.get('only_active') and scraper.status != 'A'):
                scraper_str  = str(scraper) + " "
                scraper_str += "(ID:" + str(scraper.pk) + ", Status: " + scraper.get_status_display() + ")"
                print("Check last scraper saves for scraper {}".format(scraper_str))
                
                if not scraper.last_scraper_save or \
                    (scraper.last_scraper_save < (datetime.datetime.now() - datetime.timedelta(0, 0, 0, 0, 0, num_hours))):
                    date_str = 'None'
                    if scraper.last_scraper_save:
                        date_str = scraper.last_scraper_save.strftime('%Y-%m-%d %H:%m')
                    error_str = "Last scraper save older than {} hours ({})!".format(str(num_hours), date_str)
                    print(error_str)
                    msg += 'Last scraper save check for scraper %s failed:\n' % scraper_str
                    msg += error_str + '\n\n'
                    mail_to_admins = True
                else:
                    print("OK")
        
        if options.get('send_admin_mail') and mail_to_admins:
            print("Send mail to admins...")
            if 'django.contrib.sites' in settings.INSTALLED_APPS:
                from django.contrib.sites.models import Site
                subject = Site.objects.get_current().name
            else:
                subject = 'DDS Scraper Site'
            subject += " - Last scraper save check for scraper(s) failed"
            
            mail_admins(subject, msg)
