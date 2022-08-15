#!/usr/bin/perl -w

#;******************************************************************************
#;* Copyright (c) 2002-2014, Insyde Software Corp. All Rights Reserved.
#;*
#;* You may not reproduce, distribute, publish, display, perform, modify, adapt,
#;* transmit, broadcast, present, recite, release, license or otherwise exploit
#;* any part of this publication in any form, by any means, without the prior
#;* written permission of Insyde Software Corp.
#;*
#;******************************************************************************


#
# Error would occur on RedHat, it maybe without full perl library
# 
use CGI qw(:standard);

use constant TRUE            => 1;
use constant FALSE           => 0;

my $DateToday                = `date +"%m-%d-%y"`;
chomp ($DateToday);
my $gPlatformInfoFile        = "../PlatformInfo.txt";
my $gCgiLog                  = "../../logs/cgi_$DateToday.log";
my $gPlatformInfoStr;
my $gVersionStr;
#my $gHttpQuery               = new CGI;

sub ReadPlatformInfo {
  my $IsRawInfo = $_[0];
  my @DataList;
  my $i;
  my @DataPattern;
  
  $gPlatformInfoStr = "";
  
  if (!open(FILE, "<$gPlatformInfoFile")) {
    `echo "Can't not open $gPlatformInfoFile" 1>>$gCgiLog`;
    return FALSE;
  }
  
  @DataList=<FILE>;
  
  foreach $i (0 ..$#DataList) {
    chomp($DataList[$i]);
    
    if ($IsRawInfo == FALSE) {
      $DataList[$i] =~ s/\//-/g;
      $DataList[$i] =~ s/ //g;
      if ($i == 0) {
        $gPlatformInfoStr = $DataList[$i];
      } elsif ($i == 1) {
        $gVersionStr = $DataList[$i];
      } elsif ($i > 1) {
        last;
      }
    } else {
      if ($i == 0) {
        $gPlatformInfoStr = $DataList[$i];
      } elsif ($i == 1) {
        $gVersionStr = $DataList[$i];
      } elsif ($i > 1) {
        last;
      }
    }
  }
  
  close (FILE);
  
  return TRUE;
}

print "Content-type: text/html\n\n";

my $gHttpQuery = new CGI;
my $gParam = $gHttpQuery->param("t");
my $gResult;

if (!$gParam) {
  $gResult = ReadPlatformInfo (FALSE);
} else {
  $gResult = ReadPlatformInfo (TRUE);
}
if ($gResult == TRUE) {
  print "{" . $gPlatformInfoStr . "," . $gVersionStr . "}";
} else {
  print "{\"ModelName\": \"unknown\", \"ModelVersion\":\"unknown\"}";
}

