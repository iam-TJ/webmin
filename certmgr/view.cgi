#!/usr/local/bin/perl
# view.cgi
# Views certificates and keys in detail

require './certmgr-lib.pl';
$access{'view'} || &error($text{'ecannot'});
&ReadParse();

if (!$in{'wildcard'}){$in{'wildcard'}=$config{'default_wildcard'}}
$wildcard_pattern=$in{'wildcard'};
$wildcard_pattern=~s/\./\\./g;
$wildcard_pattern=~s/\*/[^\/]*?/g;
$wildcard_pattern=~s/\?/./g;


if ($in{'dl'} ne "yes" && $in{'pkcs12'} ne "yes") {
	&header($text{'view_title'}, "");
	print &ui_hr();
}
if ($in{'delete'} eq "yes"){
	if ($in{'keyfile'}) { $file=$in{'keyfile'} }
	elsif ($in{'certfile'}) { $file=$in{'certfile'} }
	elsif ($in{'csrfile'}) { $file=$in{'csrfile'} }
	elsif ($in{'keycertfile'}) { $file=$in{'keycertfile'} }
	if (!($file)&&((-f $file)||(-s $file))){ print "<b>$file</b>: $text{'view_e_nofile'}\n<p>\n"; }
	if (unlink($file)) { print "<b>$file</b>: $text{'view_deleted'}\n<p>\n"; }
	else { print "<b>$file</b>: $text{'view_e_not_deleted'}\n<p>\n"; }
	&footer("", $text{'index_return'});
	exit;
}

if (($in{'filename'}) && ($in{'view'} eq $text{'view_view'})) {
	$in{'filename'}=$config{'ssl_dir'}."/".$in{'filename'};
	if (!open(FILE,$in{'filename'})) {
		print "$text{'e_file'}\n<p>\n";
		&footer("", $text{'index_return'});
		exit;
	}
	while(<FILE>){ $buffer.=$_;}
	if ($buffer=~/^\s*-+BEGIN\s*RSA\s*PRIVATE\s*KEY-*\s*$/mi) { $key=1; }
	if ($buffer=~/^\s*-+BEGIN\s*PRIVATE\s*KEY-*\s*$/mi) { $key=1; }
	if ($buffer=~/^\s*-+BEGIN\s*CERTIFICATE-*\s*$/mi) { $cert=1; }
	if ($buffer=~/^\s*-+BEGIN\s*CERTIFICATE\s*REQUEST-*\s*$/mi) { $csr=1; }
	if ($buffer=~/^\s*-+BEGIN\s*X509\s*CRL-*\s*$/mi) { $crl=1; }
	if (($key)&&($cert)) {$in{'keycertfile'}=$in{'filename'};}
	elsif ($key) {$in{'keyfile'}=$in{'filename'};}
	elsif ($cert) {$in{'certfile'}=$in{'filename'};}
	elsif ($csr) {$in{'csrfile'}=$in{'filename'};}
	elsif ($crl) {$in{'crlfile'}=$in{'filename'};}
	else {
		print "$text{'e_file'}<br>\n$text{'e_notcert'}\n<p>\n";
		&footer("", $text{'index_return'});
		exit;
	}
	undef($buffer);
	undef($key);
	undef($cert);
		
}

if ($in{'keyfile'}) {
	if ($in{'dl'} eq 'yes') {
		# Just output in PEM format
		&output_cert($in{'keyfile'});
	} elsif ($in{'pkcs12'} eq 'yes') {
		# Just output in PKCS8 format
		&output_pkcs12($in{'keyfile'});
	}

	open(OPENSSL,"$config{'openssl_cmd'} rsa -in $in{'keyfile'} -text -noout|");
	while(<OPENSSL>){ $buffer.=$_; }
	close(OPENSSL);
    print &ui_table_start($in{'keyfile'}, "width=60%", 2);
    print &ui_table_row(undef, (!$buffer ? $text{'e_file'} : show_key_info(1,$buffer) ) );
    print &ui_table_end()."<br>";
	&download_form("keyfile", $in{'keyfile'}, $text{'key'});
	print &ui_hr();
	&footer("", $text{'index_return'});
	exit;
}
if ($in{'certfile'}||$in{'csrfile'}) {
	if ($in{'csrfile'}){
		$in{'certfile'}=$in{'csrfile'};
		$text{'certificate'}=$text{'csr'};
	}
	if ($in{'dl'} eq 'yes') {
		# Just output in PEM format
		&output_cert($in{'certfile'});
	} elsif ($in{'pkcs12'} eq 'yes') {
		# Just output in PKCS8 format
		&output_pkcs12($in{'certfile'});
	}

	if ($in{'csrfile'}) {
		open(OPENSSL,"$config{'openssl_cmd'} req -in $in{'certfile'} -text -noout|");
	} else {
		open(OPENSSL,"$config{'openssl_cmd'} x509 -in $in{'certfile'} -text -fingerprint -noout|");
	}
	while(<OPENSSL>){ $buffer.=$_; }
	close(OPENSSL);

    print &ui_table_start($in{'certfile'}, "width=60%", 2);
    print &ui_table_row(undef, (!$buffer ? $text{'e_file'} : show_cert_info(1,$buffer) ) );
    print &ui_table_end()."<br>";
	&download_form("certfile", $in{'certfile'}, $text{'certificate'});
	print &ui_hr();
	&footer("", $text{'index_return'});
	exit;
}
if ($in{'keycertfile'}) {
	if ($in{'dl'} eq 'yes') {
		# Just output in PEM format
		&output_cert($in{'keycertfile'});
	} elsif ($in{'pkcs12'} eq 'yes') {
		# Just output in PKCS8 format
		&output_pkcs12($in{'keycertfile'});
	}

	open(OPENSSL,"$config{'openssl_cmd'} x509 -in $in{'keycertfile'} -text -fingerprint -noout|");
	while(<OPENSSL>){ $buffer.=$_; }
	close(OPENSSL);

    print &ui_table_start($in{'keycertfile'}, "width=60%", 2);
    print &ui_table_row($text{'certificate'}, $text{'key'});
    print &ui_table_row(undef, (!$buffer ? $text{'e_file'} : show_cert_info(1,$buffer) ) );

	undef($buffer);
	open(OPENSSL,"$config{'openssl_cmd'} rsa -in $in{'keycertfile'} -text -noout|");
	while(<OPENSSL>){ $buffer.=$_; }
	close(OPENSSL);

    print &ui_table_row(undef, (!$buffer ? $text{'e_file'} : show_key_info(1,$buffer) ) );
    print &ui_table_end()."<br>";

	&download_form("keycertfile", $in{'keycertfile'}, "$text{'certificate'} / $text{'key'}");
	print &ui_hr();
	&footer("", $text{'index_return'});
	exit;
}

if ($in{'crlfile'}) {
	if ($in{'dl'} eq 'yes') {
		# Just output in PEM format
		&output_cert($in{'crlfile'});
	}

	open(OPENSSL,"$config{'openssl_cmd'} crl -in $in{'crlfile'} -text -noout|");
	while(<OPENSSL>){ $buffer.=$_; }
	close(OPENSSL);

    print &ui_table_start($in{'crlfile'}, "width=60%", 2);
    print &ui_table_row(undef, (!$buffer ? $text{'e_file'} : show_crl_info(1,$buffer) ) );
    print &ui_table_end()."<br>";
	&download_form("crlfile", $in{'crlfile'}, "CRL");
	print &ui_hr();
	&footer("", $text{'index_return'});
	exit;
}

print &ui_form_start("view.cgi", "post");
print &ui_table_start($text{'view_select'}, undef, 2);
print &ui_table_row($text{'view_wildcard'}.": ".&ui_textbox("wildcard", $in{'wildcard'}), &ui_submit($text{'view_update'},"update"), undef, $valign_middle);
my @cert_directory;
push(@cert_directory, [ "", $text{'view_choose'}, "selected" ]);
foreach $f ( grep { /^(.*\/)*$wildcard_pattern$/ && -f "$config{'ssl_dir'}/$_" } &getfiles($config{'ssl_dir'})) {
    push(@cert_directory, [ $f, $config{'ssl_dir'}."/".$f ]);
}
print &ui_table_row(&ui_select("filename", undef, \@cert_directory), &ui_submit($text{'view_view'},"view"), undef, $valign_middle);
print &ui_table_end();
print &ui_form_end();
print &ui_hr();
&footer("", $text{'index_return'});

sub output_cert
{
print "Content-type: text/plain\n\n";
open(OPENSSL, $_[0]);
while(<OPENSSL>){ print; }
close(OPENSSL);
exit;
}

sub output_pkcs12
{
print "Content-type: application/pkcs12\n\n";
local $qp = quotemeta($in{'pass'});
open(OPENSSL, "$config{'openssl_cmd'} pkcs12 -in $_[0] -export -passout pass:$qp |");
while(<OPENSSL>){ print; }
close(OPENSSL);
exit;
}

sub pkcs12_filename
{
local $fn = &my_urlize($_[0]);
$fn =~ s/\.pem$/\.p12/i;
return $fn;
}

# download_form(mode, file, suffix)
sub download_form
{
local ($mode, $keyfile, $suffix) = @_;
$suffix = "";
$keyfile =~ /\/([^\/]*)$/;
local $filename = &my_urlize($1);
local $p12filename = &pkcs12_filename($1);

my $rv1 = "";
my $rv2 = "";
my $rv3 = "";

$rv1 = "<form id='view_downlod' action='view.cgi/$filename' method=post>";
$rv1 .= &ui_hidden("dl", "yes");
$rv1 .= &ui_hidden($mode, $keyfile);
$rv1 .= &ui_submit("$text{'view_download'} $suffix");
$rv1 .= "</form>";

if ($mode ne "crlfile") {
    $rv2 = "<form id='view_p12filename' action='view.cgi/$p12filename' method=post>";
    $rv2 .= &ui_hidden("pkcs12", "yes");
    $rv2 .= &ui_hidden($mode, $keyfile);
    $rv2 .= &ui_submit("$text{'view_download'} $suffix $text{'view_pkcs12'}");
    $rv2 .= &ui_password("pass","",20);
    $rv2 .= "</form>";
}

$rv3 = "<form id='view' action='view.cgi' method=post>";
$rv3 .= &ui_hidden("delete", "yes");
$rv3 .= &ui_hidden($mode, $keyfile);
$rv3 .= &ui_submit("$text{'view_delete'} $suffix");
$rv3 .= "</form>";

print &ui_table_start(undef, undef, 3);
print &ui_columns_row([$rv1, $rv2, $rv3], [ "valign=middle padding=2","valign=middle padding=2","valign=middle padding=2" ] );
print &ui_table_end();

}

