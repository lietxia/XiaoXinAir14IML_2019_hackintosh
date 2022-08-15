#!/usr/bin/perl -w
use CGI qw(:standard); 

use constant TRUE            => 1;
use constant FALSE           => 0;

my $query = new CGI;

print "Content-type: text/html\n\n";
print $ENV{'REMOTE_ADDR'};
print ", ";
print $query->remote_host;;
