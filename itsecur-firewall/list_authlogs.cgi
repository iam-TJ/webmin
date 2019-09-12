#!/usr/bin/perl
# list_logs.cgi
# Real-time view of the security log file

require './itsecur-lib.pl';
&can_use_error("authlogs");
$theme_no_table++;
$| = 1;
&header($text{'authlogs_title'}, "");
print &ui_hr();

$log = $config{'authlog'} || &get_authlog_file();
print "<b>",&text('logs_viewing', "<tt>$log</tt>"),"</b><p>\n";
print "<applet code=LogViewer width=90% height=70%>\n";
print "<param name=url value='authtail.cgi'>\n";
print "<param name=pause value=1>\n";
print "<param name=buttonlink value=authdownload.cgi>\n";
print "<param name=buttonname value='$text{'logs_download'}'>\n";
if ($session_id) {
	print "<param name=session value=\"sid=$session_id\">\n";
	}
print "</applet>\n";

print &ui_hr();
&footer("", $text{'index_return'});

