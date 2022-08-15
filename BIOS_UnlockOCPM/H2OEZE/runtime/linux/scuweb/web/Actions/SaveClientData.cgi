#!/usr/bin/perl

#;******************************************************************************
#;* Copyright (c) 2002-2014, Insyde Software Corp. All Rights Reserved.
#;*
#;* You may not reproduce, distribute, publish, display, perform, modify, adapt,
#;* transmit, broadcast, present, recite, release, license or otherwise exploit
#;* any part of this publication in any form, by any means, without the prior
#;* written permission of Insyde Software Corp.
#;*
#;******************************************************************************

use strict;
use warnings;

#use CGI qw(:standard); 
use IO::File;
use Switch;


use constant TRUE            => 1;
use constant FALSE           => 0;
use constant HTTP_POST_DATA  => 1;
use constant HTTP_GET_DATA   => 0;


# Logs
my $DateToday                = `date +"%m-%d-%y"`;
chomp ($DateToday);
my $gCgiLog                  = "../../logs/cgi_$DateToday.log";
my $gClientFolder            = "../ClientData/";


#----------
# Common Functions
#----------
sub DebugPf {
  my ($msg, $DebugLineNo) = @_;
  my @LocalFileNameArray = split (/\//, __FILE__);
  my $DebugTitle = $LocalFileNameArray[$#LocalFileNameArray] . ":" . $DebugLineNo;
  
  `echo "[DBG-$DebugTitle] $msg" 1>>$gCgiLog`;
}

sub LogPf {
  my $msg = $_[0];
  my @LocalFileNameArray = split (/\//, __FILE__);
  my $LogTitle = $LocalFileNameArray[$#LocalFileNameArray];
  
  `echo "[$LogTitle] $msg" 1>>$gCgiLog`;
}

sub LogProcessStart {
  my $WhatTimeIsIt = `date +"%H:%M:%S"`;
  
  chomp ($WhatTimeIsIt);
  LogPf ("--- start at $WhatTimeIsIt ---");
}

sub LogProcessEnd {
  LogPf ("--- end ---");
}

sub PrintJsonTextMessage {
  my $Msg = $_[0];
  my $IsError = FALSE;
  
  if ($#_ == 1) {
    $IsError = $_[1];
  }
  
  print '{"resp": "' . $Msg . '", ';
  if ($IsError) {
    print '"iserr": "true"}';
  } else {
    print '"iserr": "false"}';
  }
}

#
# Remove whitespace from the start and end of the string  
#
sub trim ($)  
{  
    my $string = shift;  

    $string =~ s/^\s+//;  
    $string =~ s/\s+$//;  
    return $string;  
}

sub trimHttpNewLine {
  my $String = $_[0];

  $String =~ s/(\%0[D|A])*$//;
  
  return $String;
}

#----------
# Functionss
#----------

#---
# Save POST data
#---
sub ReadHttpData {
  my $Type = $_[0];
  my $HttpData = "";
  
  #
  # Read Http data
  #
  if ($Type eq HTTP_POST_DATA) {
    read (STDIN, $HttpData, $ENV{'CONTENT_LENGTH'});
  } else {
    $HttpData = $ENV{'QUERY_STRING'};
  }
  if (!$HttpData) {
    $HttpData = "";
  }
  
#  $HttpData = "Main-1-56=1&Main-34-788=1&Advanced-1-33=0&Advanced-45-12=1&Advanced-33-11=1Advanced-677-99=1Advanced-66-122=1&FileGenTime=1332471896";

  return $HttpData;
}

sub ReadClientData {
  my $ClientFileName = $_[0];
  my @DataLines;
  my $RtnString = "";
  my $i;

  LogPf ("Open $ClientFileName");
  if (!open (FILE, "<$ClientFileName")) {
    #
    # the '\n' at the end of line means do not show the error line number and source code file name
    #
    LogPf ("Can't not open $ClientFileName");
    return "";
  }
  
  @DataLines=<FILE>;
  
  foreach $i (0 ..$#DataLines) {
    chomp ($DataLines[$i]);
    
    LogPf ("$DataLines[$i]");
    if ($i != 0) {
      $RtnString .= "&" . $DataLines[$i];
    } else {
      $RtnString .= $DataLines[$i];
    }
  }
  
  close (FILE);
  
  if ($RtnString eq "") {
    LogPf ("Retrun string is empty");
  }
  
  return $RtnString;
}

#---
# Save POST data
#   NOTE: Must do ReadHttpData first
#---
sub SaveClientData {
  my (@HttpDataArr, $i, $Key, $Val);
  my $ClientFileName = $_[0];
  my $HttpData = $_[1];
  
  LogPf ("client file: $ClientFileName");
  if (!open (FILE, ">$ClientFileName")) {
    #
    # the '\n' at the end of line means do not show the error line number and source code file name
    #
    LogPf ("Can't not open $ClientFileName");
    return FALSE;
  }

  #
  # split string to each key-value
  #
  @HttpDataArr = split (/&/, $HttpData);

  #
  # separate key and value
  #
  foreach $i (0 ..$#HttpDataArr) {
    ($Key, $Val) = split (/=/, $HttpDataArr[$i]);
    $Key = trim ($Key);
    $Val = trim ($Val);

    if ($Key eq "FileGenTime") {
    } elsif ($Key eq "Year") {
    } elsif ($Key eq "Month") {
    } elsif ($Key eq "Day") {
    } elsif ($Key eq "Hour") {
    } elsif ($Key eq "Minute") {
    } elsif ($Key eq "Second") {
    } elsif ($Key eq "xREBOOTx") {
    } else {
      print FILE "$HttpDataArr[$i]\n";
      `echo "$HttpDataArr[$i]" 1>>$gCgiLog`;
    }
  }

  close (FILE);
  
  if (-e $ClientFileName) {
    `less $ClientFileName 1>>$gCgiLog`;
  } else {
    LogPf ("$ClientFileName does'nt exist");
  }
  
  return TRUE;
}

#---
# Main process
#---
sub Main {
  my ($HttpPostData, $HttpGetData);
  my $FunNum;
  my $ClientId;
  my $FormData;
  my $ServerSettings;
  my $ReadData;
  my ($Code, $FileName);
  
  LogProcessStart ();

  LogPf ("Save client data process is starting...");
  
  $HttpGetData = ReadHttpData (HTTP_GET_DATA);
  if ($HttpGetData) {
    ($Code, $FileName) = split (/=/, $HttpGetData);
    if ($Code ne "fn") {
      $FileName = "";
    }
  }

  $HttpPostData = ReadHttpData (HTTP_POST_DATA);
  if (!$HttpPostData) {
    LogPf ("No post data");
    return;
  }
  ($FunNum, $ClientId, $FormData, $ServerSettings) = split (/::/, $HttpPostData);
  if (!$FileName) {
    $FileName = $ClientId;
  }
  LogPf ("File name is $FileName");

  switch ($FunNum) {
    #
    # Save
    #
    case /1/ {
      if ((SaveClientData ($gClientFolder . $FileName . "_post", $FormData) == TRUE) && 
        (SaveClientData ($gClientFolder . $FileName . "_server", $ServerSettings) == TRUE)) {
        
        PrintJsonTextMessage ("Save data complete!", FALSE);
      } else {
        PrintJsonTextMessage ("Save data failed!", TRUE);
      }
    }
    #
    # Read
    #
    case /2/ {
      $ReadData = ReadClientData ($gClientFolder . $FileName . "_post");
      $ReadData .= "::" . ReadClientData ($gClientFolder . $FileName . "_server");
      PrintJsonTextMessage ($ReadData, FALSE);
    }
    #
    # default
    #
    else {
      PrintJsonTextMessage ("Invalid parameters", TRUE);
    }
  } # end of switch
  LogProcessEnd ();
}

#################################
# Process start here....
#################################

#
# This statement is necessary to be display on browser
#
print "Content-type: text/html\n\n";
Main ();

