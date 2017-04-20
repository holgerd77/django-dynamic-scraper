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
    
    def add_arguments(self, parser):
        parser.add_argument('--only-active', type=bool, default=False, help="Run checker delete checks only for active scrapers, default=False")
        parser.add_argument('--send-admin-mail', type=bool, default=False, help="Send report mail to Django admins if last deletes are too old, default=False")
        parser.add_argument('--with-next-alert', type=bool, default=False, help="Only run for scrapers with past next alert timestamp/update timestamp afterwards, default=False")
    
    
    def handle(self, *args, **options):
        mail_to_admins = False
        msg = ''
        
        only_active = options['only_active']
        send_admin_mail = options['send_admin_mail']
        with_next_alert = options['with_next_alert']
        
        
        if with_next_alert:
            scrapers = Scraper.objects.filter(next_last_checker_delete_alert__lte=datetime.datetime.now())
            print("{num} scraper(s) with future next alert timestamp found in DB...\n".format(num=len(scrapers)))
        else:
            scrapers = Scraper.objects.all()
            print("{num} scraper(s) found in DB...\n".format(num=len(scrapers)))
        
        for s in scrapers:
            if not (only_active and s.status != 'A'):
                td = s.get_last_checker_delete_alert_period_timedelta()
                if td:
                    period = s.last_checker_delete_alert_period
                    s_str = "SCRAPER: {scraper}\nID:{id}, Status:{status}, Alert Period:{period}".format(
                        scraper=str(s), id=s.pk, status=s.get_status_display(), period=period)
                    print(s_str)
                    
                    if with_next_alert:
                        s.next_last_checker_delete_alert = datetime.datetime.now() + td
                        s.save()
                    
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
                else:
                    print("Ommitting scraper {scraper}, no (valid) time period set.\n".format(scraper=str(s)))
            else:
                print("Ommitting scraper {scraper}, not active.\n".format(scraper=str(s)))
        
        if send_admin_mail and mail_to_admins:
            print("Send mail to admins...")
            if 'django.contrib.sites' in settings.INSTALLED_APPS:
                from django.contrib.sites.models import Site
                subject = Site.objects.get_current().name
            else:
                subject = 'DDS Scraper Site'
            subject += " - Last checker delete check for scraper(s) failed"
            
            mail_admins(subject, msg)
