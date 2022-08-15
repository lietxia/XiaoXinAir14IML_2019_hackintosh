#!/usr/bin/perl -w

use CGI qw(:standard); 

use constant TRUE            => 1;
use constant FALSE           => 0;

my $DateToday = `date +"%m-%d-%y"`;
chomp ($DateToday);
my $gOpFileByDate = "../../logs/operation_$DateToday.log";

print $gOpFileByDate;
