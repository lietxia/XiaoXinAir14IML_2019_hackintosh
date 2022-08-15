#!/usr/bin/perl

#use CGI qw(:standard); 
use IO::File;
use Switch;

use strict;
use warnings;


use constant TRUE            => 1;
use constant FALSE           => 0;
use constant HTTP_POST_DATA  => 1;
use constant HTTP_GET_DATA   => 0;


my $gXmlFileDate             = "";
my $gXmlSrcFile              = "BiosSetupInfo.xml";
my $gXmlDestFile             = "../BiosSetupInfo.xml";
my $gScuPropFile             = "ScuSettings.prop";
my $gGenScuXmlExe            = "../../bin/GenScuConfig -x ".$gXmlSrcFile." -t ../Scu.txt";
#my $gGenScuTxtExe            = "../../bin/GenScuTxt -o ../Scu.txt";
my $gUpdateScuExe            = "../../bin/UpdateScuConfig";
my $gOperationLog            = "../../logs/operation.log";
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
  
  `echo "property file: $PropFile" 1>>$gOperationLog`;
  if (!open(FILE, ">$PropFile")) {
    #
    # the '\n' at the end of line means do not show the error line number and source code file name
    #
#    die "Can't not open logfile: $!\n";
#    print "Can't not open logfile: $!\n";
    `echo "Can't not open logfile" 1>>$gOperationLog`;
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
    `echo "$TimeVal is not equal to $gXmlFileDate" 1>>$gOperationLog`;
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
# Send message to client
#---
sub SendMsg {
  my $Msg = $_[0];
  
  print "$Msg";
  `echo "$Msg" 1>>$gOperationLog`;
}

#---
# Execute scu settings variable update
#---
sub UpdateScuSettings {
#  my $Result = `./$gGenScuXml 2>/dev/null`;
#  my $Result = `./$gGenScuXml 1>>$gOperationLog`;
  my $FunNum = $_[0];
  my $Result = "";
  
  `echo "$gUpdateScuExe" 1>>$gOperationLog`;
  
  switch ($FunNum) {
    case /1|3/ { 
      #
      # 1: Save changes and exit
      # 3: Save changes
      #
      `echo "save changes" 1>>$gOperationLog`;
      $Result = `$gUpdateScuExe -s $gScuPropFile 1>>$gUpdateScuLog`;
    }

    case /5/ { 
      #
      # 5: Load optimal defaults
      #
      `echo "load optimal defaults" 1>>$gOperationLog`;
      $Result = `$gUpdateScuExe -d 1>>$gUpdateScuLog`;
    }
    
    case /6/ { 
      #
      # 6: Load customized defaults
      #
      `echo "load customized defaults" 1>>$gOperationLog`;
      $Result = `$gUpdateScuExe -l 1>>$gUpdateScuLog`;
    }

    case /7/ { 
      #
      # 7: Save customized defaults
      #
      `echo "save customized defaults" 1>>$gOperationLog`;
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
  
  `echo "$gGenScuXmlExe" 1>>$gOperationLog`;
  $Result = `$gGenScuXmlExe 1>$gGenScuXmlLog`;
#  $Result = `$gGenScuXmlExe 1>>/dev/null`;
  
  if ($Result ne "") {
    return FALSE;
  }
  
  return TRUE;
  
}

#---
# Remove file
#---
sub RemoveFile {
  my $TargetSrc = $_[0];
  
  if (IsFileExist ($TargetSrc)) {
    `rm -f $TargetSrc 2>>$gOperationLog`;
    return TRUE;
  } else {
    `echo "Can't find file: $TargetSrc" 1>>$gOperationLog`;
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
#  print `pwd &>>$gOperationLog`;
#  `ls -al $TargetSrc &>>$gOperationLog`;
  if (IsFileExist ($TargetSrc)) {
    `mv -f $TargetSrc $TargetDes 2>>$gOperationLog`;
    return TRUE;
  } else {
#    print "Can't find file: $TargetSrc\n";
    `echo "Can't find file: $TargetSrc" 1>>$gOperationLog`;
    return FALSE;
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
    print "1:Critical error occured!<br />Please contact administrator or developers!<br />";
    `echo "Critical error occured!<br />Please contact administrator or developers!" 1>>$gOperationLog`;
    return FALSE;
  }
  
  if (MoveFile ($gXmlSrcFile, $gXmlDestFile) == FALSE) {
    print "1:Can't find web files<br />";
    `echo "Can't find web files" 1>>$gOperationLog`;
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
          print "1:Update settings failed!<br />";
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
    print "1:Update settings failed!<br />";
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
  

  `echo "Process[$FunNum] is starting..." >$gOperationLog`;
  #
  # The first command must be '>' to truncate file then write new logs
  #
  `pwd 1>>$gOperationLog`;
  
  #
  # Get http data (POST/GET)
  #
  $HttpGetData = ReadHttpData (HTTP_GET_DATA);
  $HttpPostData = ReadHttpData (HTTP_POST_DATA);
  
  `echo "$HttpPostData" 1>>$gOperationLog`;
  print $HttpPostData;
  
  if ($IsOutOfDate == TRUE) {
    SendMsg ("Settings are out of date! <br />Other administrators may have changed settings...<br />");
  }
  `echo "Process is finished" 1>>$gOperationLog`;
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

