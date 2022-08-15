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


my $gXmlFileDate             = "";
my $gXmlSrcFile              = "BiosSetupInfo.xml";
my $gXmlDestFile             = "../BiosSetupInfo.xml";
my $gScuPropFile             = "ScuSettings.prop";
my $gGenScuXmlExe            = "../../bin/GenScuConfig -x ".$gXmlSrcFile." -t ../Scu.txt";
my $gGenScuHtml              = "xsltproc setup.xslt ".$gXmlSrcFile." > ../setup.html";
#my $gGenScuTxtExe            = "../../bin/GenScuTxt -o ../Scu.txt";
my $gUpdateScuExe            = "../../bin/UpdateScuConfig";

my $DateToday = `date +"%m-%d-%y"`;
chomp ($DateToday);
#my $gCgiLog                  = "../../logs/cgi_$DateToday.log";
my $gCgiLog                  = "../../logs/cgi.log";
my $gGenScuXmlLog            = "../../logs/GenXml.log";
my $gUpdateScuLog            = "../../logs/UpdateXml.log";
my $gYear                    = "";
my $gMonth                   = "";
my $gDay                     = "";
my $gHour                    = "";
my $gMinute                  = "";
my $gSecond                  = "";
my $gIsReboot                = FALSE;


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

#---
# Save POST data
#---
sub ReadHttpData {
  my $HttpData = "";
  my $HttpLen = 0;

  #
  # Read Http data
  #
  if ($_[0] eq HTTP_POST_DATA) {
    if ($ENV{'REQUEST_METHOD'} ne "POST") {
      return "";
    }
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

#---
# Save POST data
#   NOTE: Must do ReadHttpData first
#---
sub SavePropData {
  my (@HttpDataArr, $i, $Key, $Val);
  my $PropFile = $_[0];
  my $HttpData = $_[1];

  `echo "property file: $PropFile" 1>>$gCgiLog`;
  if (!open(FILE, ">$PropFile")) {
    #
    # the '\n' at the end of line means do not show the error line number and source code file name
    #
    `echo "Can't not open logfile" 1>>$gCgiLog`;
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
      $gXmlFileDate = $Val;
#      print $gXmlFileDate;
    } elsif ($Key eq "Year") {
      $gYear = $Val;
    } elsif ($Key eq "Month") {
      $gMonth = $Val;
    } elsif ($Key eq "Day") {
      $gDay = $Val;
    } elsif ($Key eq "Hour") {
      $gHour = $Val;
    } elsif ($Key eq "Minute") {
      $gMinute = $Val;
    } elsif ($Key eq "Second") {
      $gSecond = $Val;
    } elsif ($Key eq "xREBOOTx") {
      print FILE "$HttpDataArr[$i]\n";
      if ($Val eq "1") {
        $gIsReboot = TRUE;
      } else {
        $gIsReboot = FALSE;
      }
    } else {
      print FILE "$HttpDataArr[$i]\n";
#      print "$HttpDataArr[$i]<br/>";
    }
  }

  close (FILE);

  `less $PropFile >$gUpdateScuLog`;

  return TRUE;
}

#---
# Must do this function after sava http data
#---
sub CheckXmlGenDate {
  my $TimeVal = `stat -c %Z $gXmlDestFile`;

  $TimeVal = trimHttpNewLine (trim ($TimeVal));
  $gXmlFileDate = trimHttpNewLine (trim ($gXmlFileDate));

#  print "Get from Server: ".$TimeVal.". Get from client: ".$gXmlFileDate.".<br />";
  #
  # GetTime of xml file on server should equal to client's, because system time
  # may be change, we must check they are same instead of > or <
  #
#  print "$TimeVal, $gXmlFileDate";
#  if ($TimeVal gt $gXmlFileDate) { # string is great than
  if ($TimeVal ne $gXmlFileDate) { # string not equal
    `echo "$TimeVal is not equal to $gXmlFileDate" 1>>$gCgiLog`;
    return FALSE;
  }

  return TRUE;
}

#---
# Check if ScuSettings.prop file exists or not
#---
sub IsFileExist {
  my $TargetFile = $_[0];
#  my $IsExist = `ls $TargetFile 2>/dev/null`;

#  if ($IsExist ne "") {
#    return TRUE;
#  }

  if (-e $TargetFile) {
    return TRUE;
  }

  return FALSE;
}

#---
# Execute scu settings variable update
#---
sub UpdateScuSettings {
#  my $Result = `./$gGenScuXml 2>/dev/null`;
#  my $Result = `./$gGenScuXml 1>>$gCgiLog`;
  my $FunNum = $_[0];
  my $Result = "";

  `echo "$gUpdateScuExe" 1>>$gCgiLog`;

  switch ($FunNum) {
    case /1|3/ {
      #
      # 1: Save changes and exit
      # 3: Save changes
      #
      `echo "save changes" 1>>$gCgiLog`;
      $Result = `$gUpdateScuExe -s $gScuPropFile 1>>$gUpdateScuLog`;
    }

    case /5/ {
      #
      # 5: Load optimal defaults
      #
      `echo "load optimal defaults" 1>>$gCgiLog`;
      $Result = `$gUpdateScuExe -d 1>>$gUpdateScuLog`;
    }

    case /6/ {
      #
      # 6: Load customized defaults
      #
      `echo "load customized defaults" 1>>$gCgiLog`;
      $Result = `$gUpdateScuExe -l 1>>$gUpdateScuLog`;
    }

    case /7/ {
      #
      # 7: Save customized defaults
      #
      `echo "save customized defaults" 1>>$gCgiLog`;
      $Result = `$gUpdateScuExe -c $gScuPropFile 1>>$gUpdateScuLog`;
    }

    else {
      #
      # 2: Discard changes and exit
      # 4: Discard changes
      # Other situations
      #
    }
  }

  if ($Result ne "") {
    return FALSE;
  }

  return TRUE;
}

#---
# Read scu settings
#---
sub ReadScuSettings {
  my $FunNum = $_[0];
  my $Result;

  `echo "$gGenScuXmlExe" 1>>$gCgiLog`;
  $Result = `$gGenScuXmlExe 1>$gGenScuXmlLog`;
#  $Result = `$gGenScuXmlExe 1>>/dev/null`;

  if ($Result ne "") {
    return FALSE;
  }
  `$gGenScuHtml`;

  return TRUE;

}

#---
# Remove file
#---
sub RemoveFile {
  my $TargetSrc = $_[0];

  if (IsFileExist ($TargetSrc)) {
    `rm -f $TargetSrc 2>>$gCgiLog`;
    return TRUE;
  } else {
    `echo "Can't find file: $TargetSrc" 1>>$gCgiLog`;
#    print "Can't find file: $TargetSrc\n";
    return FALSE;
  }
}

#---
# Move source file to destinaction
#---
sub MoveFile {
  my $TargetSrc = $_[0];
  my $TargetDes = $_[1];

#  print "src:".$TargetSrc.", des:".$TargetDes."<br />";
#  print `whoami`;
#  print `pwd &>>$gCgiLog`;
#  `ls -al $TargetSrc &>>$gCgiLog`;
  if (IsFileExist ($TargetSrc)) {
    `mv -f $TargetSrc $TargetDes 2>>$gCgiLog`;
    return TRUE;
  } else {
#    print "Can't find file: $TargetSrc\n";
    `echo "Can't find file: $TargetSrc" 1>>$gCgiLog`;
    return FALSE;
  }
}

sub GenErrorMsgStr {
  if ($#_ == 0) {
    return "{\"StatusCode\": \"500\", \"Response\": \"".$_[0]."\"}";
  } else {
    return "{\"StatusCode\": \"".$_[0]."\", \"Response\": \"".$_[1]."\"}";
  }
}

sub LoadProcess {
  my $FunNum = $_[0];
  my $Reault = FALSE;

  #
  # After update scu is success, read the new scu to create a new xml as html page
  #
  $Reault = ReadScuSettings ($FunNum);
  if ($Reault == FALSE) {
    #
    # This situation should not happen
    #
    print GenErrorMsgStr ("Critical error occured!<br />Please contact administrator or developers!<br />");
    `echo "Critical error occured!<br />Please contact administrator or developers!" 1>>$gCgiLog`;
    return FALSE;
  }

  if (MoveFile ($gXmlSrcFile, $gXmlDestFile) == FALSE) {
    print GenErrorMsgStr ("Can't find web files");
    `echo "Can't find web files" 1>>$gCgiLog`;
    return FALSE;
  }

  return TRUE;
}

sub UpdateProcess {
  my $FunNum = $_[0];
  my $Reault = FALSE;
  my $TimeRtn;

  $Reault = UpdateScuSettings ($FunNum);
  if ($Reault == TRUE) {
    #
    # Set and write system time
    #
    if (($FunNum == 1) || ($FunNum == 3)) {
      if (($gYear ne "") && ($gMonth ne "") && ($gDay ne "") &&
        ($gHour ne "") && ($gMinute ne "") && ($gSecond ne "")) {

        $TimeRtn = `date -s "$gYear/$gMonth/$gDay $gHour:$gMinute:$gSecond" 1>/dev/null`;
        if ($TimeRtn eq "") {
          `hwclock -w`;
        } else {
          print GenErrorMsgStr ("Update settings failed!");
          return FALSE;
        }
      }
      $gYear = "";
      $gMonth = "";
      $gDay = "";
      $gHour = "";
      $gMinute = "";
      $gSecond = "";
    }
  } else {
    print GenErrorMsgStr ("Update settings failed!");
    return FALSE;
  }

  if ($FunNum != 7) {
    if (LoadProcess ($FunNum) == FALSE) {
      return FALSE;
    }
  }

  return TRUE;
}

#---
# Main process
#---
sub Main {
  my $IsOutOfDate = FALSE;
  my $HttpPostData;
  my $HttpGetData;
  my ($Fun, $FunNum);
  my $Result;


  `echo "Process[$FunNum] is starting..." >$gCgiLog`;
  #
  # The first command must be '>' to truncate file then write new logs
  #
  `pwd 1>>$gCgiLog`;

  #
  # Get http data (POST/GET)
  #
  $HttpGetData = ReadHttpData (HTTP_GET_DATA);
  $HttpPostData = ReadHttpData (HTTP_POST_DATA);

  if ($HttpGetData ne "") {
    ($Fun, $FunNum) = split (/=/, $HttpGetData);
  }
  if ($HttpPostData eq "") {
    return;
  }

  if (IsFileExist ($gScuPropFile) == TRUE) {
    print GenErrorMsgStr ("System is updating! <br />Please save settings later...");
    return;
  }
  if (($FunNum ne "5") && (SavePropData ($gScuPropFile, $HttpPostData) == FALSE)) {
    print GenErrorMsgStr ("Parsing data failed!");
    return;
  }
  if (($FunNum ne "5") && (CheckXmlGenDate () == FALSE)) {
    if ($FunNum ne "5") {
      #
      # Xml file is out of date but the new property file has saved, we need
      # to delete it to avoid the next request would occur "System is updating"
      # issue.
      # Please note that when funnum is 5, we don't save a property file, so
      # there is no such file to remove.
      #
      RemoveFile ($gScuPropFile);
    }
    `echo "Property file is out of date" 1>>$gCgiLog`;
    $IsOutOfDate = TRUE;
  }

  switch ($FunNum) {
    case /1|3|5|6|7/ {
      #
      # 1: Save changes and exit
      # 3: Save changes
      # 5: Load optimal defaults
      # 6: Load customized defaults
      # 7: Save customized defaults
      #
      if ($IsOutOfDate == FALSE) {
        if (UpdateProcess ($FunNum) == TRUE) {
          `echo "Process is success!" 1>>$gCgiLog`;
          print GenErrorMsgStr (200, "Process is success!");
          if ($gIsReboot == TRUE) {
            #
            # Reboot after 1 minute
            #
            `echo "System is going to restart!" 1>>$gCgiLog`;
#            `shutdown -r +1`;
#            print "[{";
#            `at -f ../../bin/RestartSystem now + 1 minutes`;
#            `at -f /var/local/insyde/scu_utility/bin/RestartSystem now`;
#            `shutdown -r +1`;
            `shutdown -r now`;
#            print "}]";
#            print "<b>Server will restart after 1 minute</b>";
          }
        } else {
          `echo "Process failed!" 1>>$gCgiLog`;
          print GenErrorMsgStr ("Process failed!");
        }
        #
        # No matter update scu is success or not, the scu propertity file should be deleted
        #
        if (($FunNum != 5) && (RemoveFile ($gScuPropFile) == FALSE)) {
          #
          # This situation should not happen
          #
          print GenErrorMsgStr ("Critical error occured!<br />Can't delete cache file");
          return FALSE;
        }
      }
    }

    #
    # default
    #
    else {
      `echo "Run default function: do Nothing" 1>>$gCgiLog`;
      print GenErrorMsgStr ("Parameter error! Do nothing!");
      #
      # 2: Discard changes and exit
      # 4: Discard changes
      # Other situations
      #
    }
  }
  if ($IsOutOfDate == TRUE) {
    print GenErrorMsgStr ("Settings are out of date! <br />Other administrators may have changed settings...");
  }
  `echo "Process is finished" 1>>$gCgiLog`;
}

#################################
# Process start here....
#################################

#
# This statement is necessary to be display on browser
#
print "Content-type: text/html\n\n";
#  print "<html>\n<head>\n<title>Test</title>\n</head>\n<body>\n";
Main ();
#  print "</body>\n</html>\n";

