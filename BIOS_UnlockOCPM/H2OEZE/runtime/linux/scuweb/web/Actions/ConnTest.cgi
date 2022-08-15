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
#use CGI qw(:standard); 
use IO::File;

use constant TRUE            => 1;
use constant FALSE           => 0;

my $gPlatformInfoFile        = "../PlatformInfo.txt";
my $gOperationLog            = "../../logs/operation.log";
my $gPlatformInfoStr         = "";
#my $gHttpQuery               = new CGI;

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

#print "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">";
print "Content-type: text/html\n\n";
#print $gHttpQuery->header (); 
#print "<html><body>";

#`echo "Conneciton test and return platform information" 1>>$gOperationLog`;

if (ReadPlatformInfo () == TRUE) {
  print $gPlatformInfoStr;
} else {
  print "1:Can't read platform information";
}
#print "</body></html>";

