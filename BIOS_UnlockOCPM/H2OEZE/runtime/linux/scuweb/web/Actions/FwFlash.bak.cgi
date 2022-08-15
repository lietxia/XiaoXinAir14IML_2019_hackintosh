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

use strict; 

use CGI qw( :standard );
use Switch;
use File::Basename; 
use LWP::UserAgent;
use HTTP::Request;


use constant TRUE            => 1;
use constant FALSE           => 0;

#----------
# Global settings
#----------
$CGI::POST_MAX = 1024 * 5000;  # 5MB (The maximun size of uploading file)

#----------
# Global Constants
#----------
my $DateToday                = `date +"%m-%d-%y"`;
chomp ($DateToday);
my $gOperationLog            = "../../logs/operation_$DateToday.log";

my $gFlashBin                = "../../bin/flashit.sh -i ";
my $gFlashLog                = "../../logs/Flash.log";
my $gSafeFilenameCharacters  = "a-zA-Z0-9_.-"; 
my $gUploadDir               = "../UploadFiles"; 
my $gDlRomDir                = "../RomFiles";
my $gExeRomDir               = "../../web/RomFiles";
my $gFlashToolDir            = "../../bin/FlashTool";

#----------
# Global Variables
#----------
my $gHttpQuery               = new CGI; 


#----------
# Common Functions
#----------
sub DebugPf {
  my ($msg, $DebugLineNo) = @_;
  my @LocalFileNameArray = split (/\//, __FILE__);
  my $DebugTitle = $LocalFileNameArray[$#LocalFileNameArray] . ":" . $DebugLineNo;
  
  `echo "[DBG-$DebugTitle] $msg" 1>>$gOperationLog`;
}

sub LogPf {
  my $msg = $_[0];
  my @LocalFileNameArray = split (/\//, __FILE__);
  my $LogTitle = $LocalFileNameArray[$#LocalFileNameArray];
  
  `echo "[$LogTitle] $msg" 1>>$gOperationLog`;
}

sub PrintJsonTextMessage {
  my ($Msg, $IsError) = @_;
  
  LogPf ($Msg);
  print '{"resp": "' . $Msg . '", ';
  if ($IsError) {
    print '"iserr": "true"}';
  } else {
    print '"iserr": "false"}';
  }
}

#----------
# Functions
#----------

sub GenRomFile {
  my $Target = $_[0];
  my $IsSuccess = FALSE;
  my $MyPwd = `pwd`;
  my $Result;
  my $LocNow;

  $LocNow = `pwd`;
  chdir "../../bin/LinuxFlash/LinRelease/static_pkg";
  switch ($Target) {
    #
    # Generate bios rom file
    #
    case /b/ {
#      `./flashit_s.sh ../../../../web/RomFiles/bios.rom -g`;
      $Target = "bios.rom";
    }
    #
    # Generate cmos binary file
    #
    case /c/ {
#      `./flashit_s.sh ../../../../web/RomFiles/cmos.rom -cr`;
      $Target = "cmos.rom";
    }
    #
    # default
    #
    else {
      $Target ="";
    }
  } # end of switch
  chdir "$LocNow";
  
  return $Target;
}

sub ChkRomFile {
  my $Target = $_[0];
  my $IsSuccess = FALSE;
  my $Result = "";

  switch ($Target) {
    #
    # Check if bios rom file exists
    #
    case /cb/ {
#      `ls ../RomFiles/bios.rom 1>/dev/null 2>&1>/dev/null`;
      `ls ../RomFiles/bios.rom 1>/dev/null`;
      $Result = $?;
    }
    #
    # Check if coms binary file exists
    #
    case /cc/ {
#      `ls ../RomFiles/cmos.rom 1>/dev/null 2>&1>/dev/null`;
      `ls ../RomFiles/cmos.rom 1>/dev/null`;
      $Result = $?;
    }
    #
    # default
    #
    else {
    }
  } # end of switch
  if ($Result eq "0") {
    $IsSuccess = TRUE;
  }
  
  return $IsSuccess;
}

sub CheckFileLinkProcess {
  my $CheckFile = $gHttpQuery->param("dl");
  my $FileName;
  my $NowLoc = `pwd`;
  my $Result = 1;
  
  LogPf ("Process $CheckFile");
  if ($CheckFile eq "gb") {
    $FileName = "bios.rom";
    if (-e "../RomFiles/$FileName") {
      print "<a href=\"../RomFiles/$FileName\">BIOS rom file</a>";
    } else {
      print "BIOS rom file doesn't exist";
    }
  } elsif ($CheckFile eq "gc") {
    $FileName = "cmos";
    if (-e "../RomFiles/$FileName") {
      print "<a href=\"../RomFiles/$FileName\">CMOS file</a>";
    } else {
      print "CMOS file doesn't exist";
    }
  } elsif ($CheckFile eq "gv") {
    $FileName = "variable";
    if (-e "../RomFiles/$FileName") {
      print "<a href=\"../RomFiles/$FileName\">Variable file</a>";
    } else {
      print "Variable file doesn't exist";
    }
  } else {
    print "Invalid parameters";
  }
}

sub GenFileLinkProcess {
  my $CheckFile = $gHttpQuery->param("dl");
  my $FileName;
  my $NowLoc = `pwd`;
  my $Result = 1;
  
  LogPf ("Process $CheckFile");
  if ($CheckFile eq "gb") {
    $FileName = "bios.rom";
    $Result = FlashFwEx ("../../web/RomFiles/$FileName", "-g");
    if (!$Result) {
      print "<a href=\"RomFiles/$FileName\">BIOS rom file</a>";
      return;
    }
  } elsif ($CheckFile eq "gc") {
    $FileName = "cmos";
    $Result = FlashFwEx ("../../web/RomFiles/$FileName", "-cr");
    if (!$Result) {
      print "<a href=\"RomFiles/$FileName\">CMOS file</a>";
      return;
    }
  } elsif ($CheckFile eq "gv") {
    $FileName = "variable";
    $Result = FlashFwEx ("../../web/RomFiles/$FileName", "-vr");
    if (!$Result) {
      print "<a href=\"RomFiles/$FileName\">Variable file</a>";
      return;
    }
  } else {
    print "Invalid parameters";
  }
  print "Generate new file failed";
}

sub StoreUrlDownloadFile {
  my ($FileData, $ToSaveFile) = @_;
  
#  open (DLFILE, ">$ToSaveFile") or die "$!"; 
  open (DLFILE, ">$ToSaveFile") or return FALSE; 
  binmode DLFILE; 

  print DLFILE $FileData; 

  close DLFILE;
  
  return TRUE;
}

sub DownloadFromRemoteServer {
  my $ua = LWP::UserAgent->new (env_proxy => 1,keep_alive => 1, timeout => 30);
  my ($RomFile, $OptFile, $RmoteAddr) = @_;
  my $Response;
  
  $Response = $ua->get("http://$RmoteAddr/UploadFiles/$RomFile");
  if ($Response->is_success) { 
    if (!StoreUrlDownloadFile ($Response->content, "$gUploadDir/$RomFile")) {
      return "Save BIOS rom file failed!";
    }
  } else {
    return "Download BIOS rom file failed!";
  }
  
  $Response = $ua->get("http://$RmoteAddr/UploadFiles/$OptFile");
  if ($Response->is_success) { 
    if (!StoreUrlDownloadFile ($Response->content, "$gUploadDir/$OptFile")) {
      return "Save flash options file failed!";
    }
  } else {
    return "Download flash options file failed!";
  }
  
  return "";
}

sub ReadFlashOptions {
  my ($FlashOptHash, $OptFile) = @_;
  my $OptStr;
  my @OptPairs;
  my $Pair;
  my ($Name, $Value);
  
  LogPf ("Options is in $OptFile");
  open (OPTFILE, "<$gUploadDir/$OptFile") or return FALSE; 
  $OptStr = <OPTFILE>;
  
  @OptPairs = split (/&/, $OptStr);
  foreach $Pair (@OptPairs) {
    ($Name, $Value) = split (/=/, $Pair);
    $FlashOptHash->{$Name} = $Value;
    DebugPf ("Opt: " . $FlashOptHash->{$Name}, __LINE__);
  }
  
  close OPTFILE;
  
  return TRUE;
}

sub ReadHashData {
  my ($FlashOptHash, $ParamName) = @_;
  
  if ($FlashOptHash->{$ParamName}) {
    return $FlashOptHash->{$ParamName};
  }
  
  return "";
}

sub ParseFlashOpts {
  my $FileType = $gHttpQuery->param("ft");
  my ($RomFile, $FlashOptHash) = @_;
  my $FlashOptStr;
  my $OptValue;
  my $OptTimes;
  my $OptDelay;
  
  DebugPf ("File type is $FileType", __LINE__);
  #
  # Flash options string
  #
  if ($FileType eq "1") {
    $FlashOptStr = ReadHashData ($FlashOptHash, "FlashOpt");
    $FlashOptStr .= " " . ReadHashData ($FlashOptHash, "FlashRom");
    $FlashOptStr .= " " . ReadHashData ($FlashOptHash, "MsgMode");
    #
    # When verify error, retry how many times
    #
    $OptTimes = ReadHashData ($FlashOptHash, "vrt-times");
    if ($OptTimes) {
      $FlashOptStr .= " -vrt:$OptTimes";
    }
    #
    # When SMI error, retry how many times with how many delay time
    #
    $OptTimes = ReadHashData ($FlashOptHash, "rt-times");
    $OptDelay = ReadHashData ($FlashOptHash, "rt-delay");
    if ($OptTimes and $OptDelay) {
      $FlashOptStr .= " -rt:$OptTimes,$OptDelay";
    }
    #
    # -r option is not a option for flash tool, just a reminder for user to know 
    # that after flash will reboot system. 
    # NOTE: default is reboot after flash.
    #
    $OptValue = ReadHashData ($FlashOptHash, 'FinishAct');
    if ($OptValue ne "-r") {
      $FlashOptStr .= " " . $OptValue;
    }
    DebugPf ("Flash option string is: $FlashOptStr", __LINE__);
  } elsif ($FileType eq "3") {
    #
    # Write CMOS only
    #
    $FlashOptStr = "-cw";
  } else {
    LogPf ("Empty flash options");
    return "";
  }
  
  return "../../web/UploadFiles/$RomFile $FlashOptStr";
}

sub GetFlashReturnCode {
  my ($RtnCode, $DftErrMsg) = @_;

=head
  [ReturnCodeDefinition]
  RETURN_SUCCESSFUL=0,0
  RETURN_MODEL_CHECK_FAIL=1,1
  RETURN_USER_CONFIRM_CANCEL=2,2
  RETURN_AC_NOT_CONNECT=3,3
  RETURN_LOAD_DRIVER_FAIL=4,4
  RETURN_NEED_REBOOT=5,5
  RETURN_USER_EXIT=6,6
  RETURN_SAME_VERSION_CHECK=7,7
=cut
  if ($RtnCode == 0) {
    #
    # Success
    # 
    return "";
  } elsif ($RtnCode == 2) {
    #
    # User confirm cancel
    # 
    return "";
  } elsif ($RtnCode == 5) {
    #
    # Need to reboot
    # 
    return "";
  } elsif ($RtnCode == 7) {
    #
    # Same version check
    # 
    return "";
  } elsif ($RtnCode == 1) {
    return "Model check failed";
  } elsif ($RtnCode == 3) {
    return "AC doesn't connect";
  } elsif ($RtnCode == 4) {
    return "Load driver failed";
  } elsif ($RtnCode == 6) {
    #
    # This won't happen
    #
    return "User exit";
  } elsif ($RtnCode == 8) {
    return "File not found";
  } elsif ($RtnCode == 9) {
    return "Error before flash";
  } elsif ($RtnCode == 10) {
    return "Write rom failed";
  } elsif ($RtnCode == 11) {
    return "Write EC failed";
  } elsif ($RtnCode == 12) {
    return "Write extra data failed";
  } else {
    return $DftErrMsg;
  }
}

sub FlashFw {
  my $FlashOptStr = $_[0];
  my $Result;
  my $NowLoc = `pwd`;
  
  DebugPf ("Flashit: $FlashOptStr", __LINE__);
  #
  # Flash tool must run on its folder or it can't find specific files to driver, 
  # and flash options string must contain the rom file (BIOS/CMOS/Variable)
  #
  chdir $gFlashToolDir;
  DebugPf ("./flashit_s.sh $FlashOptStr", __LINE__);
#  `./flashit_s.sh $FlashOptStr 1>/dev/null 2>&1>/dev/null`;
  `./flashit_s.sh $FlashOptStr 1>/dev/null`;
  $Result = ($? >> 8);
  chomp ($Result);
  chomp ($NowLoc);
  chdir $NowLoc;
  
  DebugPf ("check result: $Result", __LINE__);
  #
  # echo $? in shell return a numeric value, so use '==' to compare
  #
  return GetFlashReturnCode ($Result, "Flash failed");
}

sub FlashFwEx {
  my ($FilePath, $FlashOpt) = @_;
  my $Result;
  my $NowLoc = `pwd`;
  
  DebugPf ("Flashit: $FilePath $FlashOpt", __LINE__);
  #
  # Flash tool must run on its folder or it can't find specific files to driver, 
  # and flash options string must contain the rom file (BIOS/CMOS/Variable)
  #
  chdir $gFlashToolDir;
  DebugPf ("./flashit_s.sh $FilePath $FlashOpt", __LINE__);
#  `./flashit_s.sh $FilePath $FlashOpt 1>/dev/null 2>&1>/dev/null`;
  `./flashit_s.sh $FilePath $FlashOpt 1>/dev/null`;
  $Result = ($? >> 8);
  chomp ($Result);
  chomp ($NowLoc);
  chdir $NowLoc;
  
  DebugPf ("check result: $Result", __LINE__);
  #
  # echo $? in shell return a numeric value, so use '==' to compare
  #
  return GetFlashReturnCode ($Result, "Read firmware failed");
}

sub FlashFwProcess {
  my ($RomFile, $OptFile) = @_;
  my $HostIp = $ENV{'REMOTE_ADDR'};
  my $HostPort = $gHttpQuery->param("hport");
  my $Result;
  my %FlashOptHash = ();
  my $FlashOptStr;
  
  #
  # $HostPort exists means firmware files on remote server, otherwise firmware 
  # files on localhost
  #
  if ($HostPort) {
    DebugPf ("check received addr: $HostIp/$HostPort", __LINE__);
    #
    # File is on remote server
    #
    LogPf ("Download file from remote server ($HostIp:$HostPort)");
    $Result = DownloadFromRemoteServer ($RomFile, $OptFile, "$HostIp:$HostPort");
    if ($Result) {
      PrintJsonTextMessage ($Result, TRUE);
#      print $Result;
      return;
    }
  }
  #
  # File is on local server now
  #
  LogPf ("File is in local server now");
  ReadFlashOptions (\%FlashOptHash, $OptFile);
  if (!%FlashOptHash) {
    PrintJsonTextMessage ("Read flash options failed", TRUE);
    return;
  }
  $FlashOptStr = ParseFlashOpts ($RomFile, \%FlashOptHash);
  if (!$FlashOptStr) {
    PrintJsonTextMessage ("Parse flash options failed", TRUE);
    return;
  }
  $Result = FlashFw ($FlashOptStr);
  if ($Result) {
    PrintJsonTextMessage ($Result, TRUE);
    return;
  }
  
  PrintJsonTextMessage ("Firmware updated", FALSE);
}

sub Main {
  my $FlashFunc = $gHttpQuery->param("func");
  my $RomFile = $gHttpQuery->param("fn");
  my $OptFile = $gHttpQuery->param("pd");
  my $WhatTimeIsIt = `date +"%H:%M:%S"`;
  
  chomp ($WhatTimeIsIt);
  LogPf ("--- start at $WhatTimeIsIt ---");
  if ((!$FlashFunc && !$RomFile) || (!$FlashFunc && !$OptFile)) {
    PrintJsonTextMessage ("Invalid parameters", TRUE);
#    print "Invalid parameters";
    return;
  }
  
  LogPf ("Flash func = $FlashFunc");
  if ($FlashFunc eq "chk") {
    #
    # Check rom file and use javascirpt to append a link on browser
    #
    CheckFileLinkProcess ();
  } elsif ($FlashFunc eq "gen") {
    #
    # Generate rom file and use javascirpt to append a link on browser
    #
    GenFileLinkProcess ();
  } elsif ($FlashFunc eq "fsf") {
    #
    # Flash firmware on self
    #
    FlashFwProcess ($RomFile, $OptFile);
  } elsif ($FlashFunc eq "ffw") {
    #
    # Flash firmware which on remote server
    #
    FlashFwProcess ($RomFile, $OptFile);
  } else {
    PrintJsonTextMessage ("Invalid parameters", TRUE);
#    print "Invalid parameters";
  }
  LogPf ("--- end ---");
}

#
# Must return text/html or may cause errors
#
#print $gHttpQuery->header (); 
print "Content-type: text/html\n\n";
Main ();


