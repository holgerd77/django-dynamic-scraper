from optparse import make_option
from subprocess import Popen, PIPE
from django.conf import settings
from django.core.mail import mail_admins
from django.core.management.base import BaseCommand
from dynamic_scraper.models import Scraper

class Command(BaseCommand):
    help = 'Runs all checker tests'
    
    option_list = BaseCommand.option_list + (
        make_option(
            '--only-active',
            action="store_true",
            dest="only_active",
            default=False,
            help="Run checker tests only for active scrapers"),
        make_option(
            '--report-only-errors',
            action="store_true",
            dest="report_only_errors",
            default=False,
            help="Report only if checker is returning ERROR (default: WARNING/ERROR)"),
        make_option(
            '--send-admin-mail',
            action="store_true",
            dest="send_admin_mail",
            default=False,
            help="Send report mail to Django admins if errors occured"),
    )
    
    
    def handle(self, *args, **options):
        '''
        if options.get('only_active'):
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
            if not (options.get('only_active') and scraper.status != 'A') and scraper.checker_set.count() > 0:
                scraper_str  = unicode(scraper) + " "
                scraper_str += "(ID:" + unicode(scraper.pk) + ", Status: " + scraper.get_status_display() + ")"
                print "Run checker test for scraper %s..." % scraper_str
                
                cmd  = 'scrapy crawl checker_test '
                if options.get('report_only_errors'):
                    cmd += '-L ERROR '
                else:
                    cmd += '-L WARNING '
                cmd += '-a id=' + str(scraper.pk)
                
                p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
                stderr = p.communicate()[1]
                
                if stderr != '':
                    print stderr
                    msg += 'Checker test for scraper %s failed:\n' % scraper_str
                    msg += stderr + '\n\n'
                    mail_to_admins = True
                else:
                    print "Checker configuration working."
        
        if options.get('send_admin_mail') and mail_to_admins:
            print "Send mail to admins..."
            if 'django.contrib.sites' in settings.INSTALLED_APPS:
                from django.contrib.sites.models import Site
                subject = Site.objects.get_current().name
            else:
                subject = 'DDS Scraper Site'
            subject += " - Errors while running checker configuration tests"
            
            mail_admins(subject, msg)
                
            
            
            
            
            
        
            
        