#!/usr/bin/perl
# index.cgi
# Show icons for rules, services, groups and NAT

require './itsecur-lib.pl';
&header($text{'index_title'}, "", undef, 1, 1, 0, &apply_button(), undef, undef,
	&text('index_version', $module_info{'version'}));

print &ui_hr();

# Icons table
@can_opts = grep { $_ eq "backup" || $_ eq "restore" || $_ eq "remote" || $_ eq "import" ? &can_edit($_) : &can_use($_) } @opts;
@links = map { "list_".$_.".cgi" } @can_opts;
@titles = map { $text{$_."_title"} } @can_opts;
@icons = map { "images/".$_.".gif" } @can_opts;
@hrefs = map { ($_ eq "logs" || $_ eq "authlogs") && $config{'open_logs'} ? "target=_new" : "" } @can_opts;
&itsecur_icons_table(\@links, \@titles, \@icons, 4, \@hrefs);

if (&can_edit("apply") || &can_edit("bootup")) {
	print &ui_hr();
	}

print &ui_buttons_start();

if (&can_edit("apply")) {
	# Apply button
    print &ui_buttons_row("apply.cgi", $text{'index_apply'}, $text{'index_applydesc'});
	}

if (&can_edit("bootup")) {
	&foreign_require("init", "init-lib.pl");
	$atboot = &init::action_status("itsecur-firewall") == 2;

	# At-boot button
    print &ui_buttons_row("bootup.cgi", $text{'index_bootup'}, $text{'index_bootupdesc'}, undef,
        &ui_yesno_radio("boot", ( $atboot ? 1 : 0 ), 1, 0));
	}

print &ui_buttons_end();

print &ui_hr();
&footer("/", $text{'index'});

# itsecur_icons_table(&links, &titles, &icons, [columns], [href], [width], [height])
# Renders a 4-column table of icons
sub itsecur_icons_table
{
&load_theme_library();
if (defined(&theme_icons_table)) {
	&theme_icons_table(@_);
	return;
	}
my ($i, $need_tr);
my $cols = $_[3] ? $_[3] : 4;
my $per = int(100.0 / $cols);
print &ui_table_start(undef,"width=100% cellpadding=5",2);
for($i=0; $i<@{$_[0]}; $i++) {
	if ($i%$cols == 0) { print "<tr>\n"; }
	print "<td width=$per% align=center valign=top>\n";
	&generate_icon($_[2]->[$i], $_[1]->[$i], $_[0]->[$i],
		       ref($_[4]) ? $_[4]->[$i] : $_[4], $_[5], $_[6]);
	print "</td>\n";
        if ($i%$cols == $cols-1) { print "</tr>\n"; }
        }
while($i++%$cols) { print "<td width=$per%></td>\n"; $need_tr++; }
print "</tr>\n" if ($need_tr);
print &ui_table_end();
}


