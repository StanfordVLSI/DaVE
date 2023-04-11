// No Conflict in later (our) version of jQuery
window.$jqTheme = jQuery.noConflict(true);
jQuery.htmlPrefilter = function( html ) {
	return html;
};