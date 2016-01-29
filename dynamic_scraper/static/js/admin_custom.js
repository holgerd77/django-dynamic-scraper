var $ = django.jQuery

// From: https://djangosnippets.org/snippets/1492/, 2015-09-16
$(document).ready(function() {
	$('div.inline-group div.inline-related:not(.tabular)').each(function() {
        fs = $(this).find('fieldset')
        h3 = $(this).find('h3:first')

        // Don't collapse if fieldset contains errors
        if (fs.find('div').hasClass('errors'))
            fs.addClass('stacked_collapse');
        else
            fs.addClass('stacked_collapse collapsed');
        
        // Add toggle link
        h3.prepend('<a class="stacked_collapse-toggle" style="color:#5b80b2;" href="#">(' + gettext('Show') + ')</a>&nbsp; ');
        h3.find('a.stacked_collapse-toggle').bind("click", function(){
            fs = $(this).parent('h3').next('fieldset');
            if (!fs.hasClass('collapsed'))
            {
                fs.addClass('collapsed');
                $(this).html('(' + gettext('Show') + ')');
            }
            else
            {
                fs.removeClass('collapsed');
                $(this).html('(' + gettext('Hide') + ')');
            }
        }).removeAttr('href').css('cursor', 'pointer');
				
				// Limit height of common textarea_fields
				var c_ta_fields = 'div.field-pagination_page_replace textarea, ';
				c_ta_fields += 'div.dynamic-requestpagetype_set textarea';
				$(c_ta_fields).css('height', '54px');
				
				// Limit height of ScraperElem textarea fields
				var ta_fields = 'tr.dynamic-scraperelem_set textarea, ';
				ta_fields += 'div.field-checker_x_path textarea, ';
				ta_fields += 'div.field-checker_x_path_result textarea';
				$(ta_fields).css('height', '40px');
				$(ta_fields).css('width', '220px');
    });
});