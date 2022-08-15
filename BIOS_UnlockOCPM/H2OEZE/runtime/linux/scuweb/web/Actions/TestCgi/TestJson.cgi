#!/usr/bin/perl -w

use CGI qw(:standard); 

print "Content-type: application/json\n\n";
print "{\"title\": \"test\", \"mesg\": \"test json is success\"}";

