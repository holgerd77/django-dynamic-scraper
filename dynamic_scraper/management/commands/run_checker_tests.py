#Stage 2 Update (Python 3)
from __future__ import print_function
from __future__ import unicode_literals
from builtins import str
from optparse import make_option
from subprocess import Popen, PIPE
from django.conf import settings
from django.core.mail import mail_admins
from django.core.management.base import BaseCommand
from dynamic_scraper.models import Scraper

class Command(BaseCommand):
    help = 'Runs all checker tests'
    
    def add_arguments(self, parser):
        parser.add_argument('--only-active', type=bool, default=False, help="Run checker tests only for active scrapers, default=False")
        parser.add_argument('--report-only-errors', type=bool, default=False, help="Report only if checker is returning ERROR, default: WARNING/ERROR)")
        parser.add_argument('--send-admin-mail', type=bool, default=False, help="Send report mail to Django admins if errors occured, default=False")
    
    
    def handle(self, *args, **options):
        
        only_active = options['only_active']
        report_only_errors = options['report_only_errors']
        send_admin_mail = options['send_admin_mail']
        
        
        '''
        if only_active:
            scraper_list = Scraper.objects.filter(
                checker_x_path__isnull=False, 
                checker_ref_url__isnull=False,
                status='A'
            )
        else:
            scraper_list = Scraper.objects.filter(
                checker_x_path__isnull=False, 
                checker_ref_url__isnull=False
            )
        '''
        mail_to_admins = False
        msg = ''
        for scraper in Scraper.objects.all():
            if not (only_active and scraper.status != 'A') and scraper.checker_set.count() > 0:
                scraper_str  = str(scraper) + " "
                scraper_str += "(ID:" + str(scraper.pk) + ", Status: " + scraper.get_status_display() + ")"
                print("Run checker test for scraper {}".format(scraper_str))
                
                cmd  = 'scrapy crawl checker_test '
                if report_only_errors:
                    cmd += '-L ERROR '
                else:
                    cmd += '-L WARNING '
                cmd += '-a id=' + str(scraper.pk)
                
                p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
                stderr = p.communicate()[1]
                
                if stderr != b'':
                    print(stderr)
                    msg += 'Checker test for scraper {s} failed:\n'.format(s=scraper_str)
                    msg += str(stderr) + '\n\n'
                    mail_to_admins = True
                else:
                    print("Checker configuration working.")
        
        if send_admin_mail and mail_to_admins:
            print("Send mail to admins...")
            if 'django.contrib.sites' in settings.INSTALLED_APPS:
                from django.contrib.sites.models import Site
                subject = Site.objects.get_current().name
            else:
                subject = 'DDS Scraper Site'
            subject += " - Errors while running checker configuration tests"
            
            mail_admins(subject, msg)
                
            
            
            
            
            
        
            
        