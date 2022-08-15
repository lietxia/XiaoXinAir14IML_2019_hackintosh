#!/usr/bin/perl -w

#
# Error would occur on RedHat, it maybe without full perl library
# 
use CGI qw(:standard); 
use JSON;
use Plack::Builder;

use constant TRUE            => 1;
use constant FALSE           => 0;

my $gPlatformInfoFile        = "../PlatformInfo.txt";
my $gOperationLog            = "../../logs/operation.log";
my $gPlatformInfoStr         = "";
my $gHttpQuery               = new CGI;

sub ReadPlatformInfo {
  my @DataList;
  my $i;
  my @DataPattern;
  
  $gPlatformInfoStr = "";
  
  if (!open(FILE, "<$gPlatformInfoFile")) {
    `echo "Can't not open $gPlatformInfoFile" 1>>$gOperationLog`;
    return FALSE;
  }
  
  @DataList=<FILE>;
  
  foreach $i (0 ..$#DataList) {
    chomp($DataList[$i]);
    $DataList[$i] =~ s/\//-/g;
    $DataList[$i] =~ s/ //g;
    @DataPattern = split (/=/, $DataList[$i]);
    if ($i > 0) {
      $gPlatformInfoStr .= "_";
    }
    $gPlatformInfoStr .= $DataPattern[1];
  }
  
  close (FILE);
  
  return TRUE;
}

#print "Content-type: text/html\n\n";
print $gHttpQuery->header (); 


my $app = sub {
    my $env = shift;
    if ($env->{PATH_INFO} eq '/whatever.json') {
        my $body = JSON::encode_json({
            hello => 'world',
        });
        return [ 200, ['Content-Type', 'application/json'], [ $body ] ];
    }
    return [ 404, ['Content-Type', 'text/html'], ['Not Found']];
};

builder {
    enable "JSONP";
    $app;
};
