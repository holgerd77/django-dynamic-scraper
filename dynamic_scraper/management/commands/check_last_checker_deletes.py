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
    help = 'Checks last checker deletes of a scraper being older than <last_checker_delete_alert_period> period provided in admin form'
    
    option_list = BaseCommand.option_list + (
        make_option(
            '--only-active',
            action="store_true",
            dest="only_active",
            default=False,
            help="Run checker delete checks only for active scrapers"),
        make_option(
            '--send-admin-mail',
            action="store_true",
            dest="send_admin_mail",
            default=False,
            help="Send report mail to Django admins if last deletes are too old"),
    )
    
    
    def handle(self, *args, **options):
        mail_to_admins = False
        msg = ''
        
        for s in Scraper.objects.all():
            td = s.get_last_checker_delete_alert_period_timedelta()
            if not (options.get('only_active') and s.status != 'A') and td:
                period = s.last_checker_delete_alert_period
                s_str = "SCRAPER: {scraper}\nID:{id}, Status:{status}, Alert Period:{period}".format(
                    scraper=str(s), id=s.pk, status=s.get_status_display(), period=period)
                print(s_str)
                
                if not s.last_checker_delete or \
                    (s.last_checker_delete < (datetime.datetime.now() - td)):
                    if s.last_checker_delete:
                        error_str = "Last checker delete older than alert period ({date_str})!".format(
                            date_str=s.last_checker_delete.strftime('%Y-%m-%d %H:%m'),)
                    else:
                        error_str = "Last checker delete not available!"
                    print(error_str)
                    msg += s_str + '\n' + error_str + '\n\n'
                    mail_to_admins = True
                else:
                    print("OK")
            print()
        
        if options.get('send_admin_mail') and mail_to_admins:
            print("Send mail to admins...")
            if 'django.contrib.sites' in settings.INSTALLED_APPS:
                from django.contrib.sites.models import Site
                subject = Site.objects.get_current().name
            else:
                subject = 'DDS Scraper Site'
            subject += " - Last checker delete check for scraper(s) failed"
            
            mail_admins(subject, msg)
