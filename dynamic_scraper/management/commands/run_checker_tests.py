import os
from django.core.management.base import BaseCommand
from dynamic_scraper.models import Scraper

class Command(BaseCommand):
    help = 'Runs all checker tests'

    def handle(self, *args, **options):
        scraper_list = Scraper.objects.filter(checker_x_path__isnull=False, checker_ref_url__isnull=False)

        for scraper in scraper_list:
            print "Run checker test for scraper " + unicode(scraper) + " (" + unicode(scraper.pk) + ")..."
            cmd  = 'scrapy crawl checker_test -L WARNING -a id=' + str(scraper.pk)
            os.system(cmd)
            #self._run_spider(id=scraper.id, spider='checker_test', run_type='TASK', do_action='yes')
        
            
        