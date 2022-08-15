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
my $gCgiLog            = "../../logs/cgi_$DateToday.log";

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
  
  `echo "[DBG-$DebugTitle] $msg" 1>>$gCgiLog`;
}

sub LogPf {
  my $msg = $_[0];
  my @LocalFileNameArray = split (/\//, __FILE__);
  my $LogTitle = $LocalFileNameArray[$#LocalFileNameArray];
  
  `echo "[$LogTitle] $msg" 1>>$gCgiLog`;
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

sub CmpCheckSum {
  my ($LocaFilePath, $RemoteFileCs) = @_;
  my $LocalFileCs;
  my $Result;
  my @Md5Result;
  
  $LocalFileCs = `md5sum $LocaFilePath`;
  $Result = ($? >> 8);
  DebugPf ("Gen md5 checksum result is $Result", __LINE__);
  if ($Result == 0) {
    @Md5Result = split (/ /, $LocalFileCs);
    LogPf ("Compare 2 checksums, local file is '" . $Md5Result[0] . 
      "', remote file is '$RemoteFileCs'");
    if ($RemoteFileCs ne $Md5Result[0]) {
      return "Checksum is not correct";
    }
    LogPf ("Same checksum!");
    
    return "";
  } else {
    return "Generate checksum failed";
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

sub PrintFileLinkJson {
  my ($Type, $FileName, $LinkName, $Result) = @_;
  
  print '{"type": "' . $Type . '", ' . 
         '"link": "<a href=\"RomFiles/' . $FileName . '\">' . $LinkName . '</a>", ' . 
         '"resp": "' . $Result . '"}'; 
}

sub CheckFileLinkProcess {
  my $CheckFile = $gHttpQuery->param("dl");
  my $FileName;
  my $NowLoc = `pwd`;
  my $Result = 1;
  
  LogPf ("Process $CheckFile");
  if ($CheckFile eq "b") {
    $FileName = "bios.rom";
    if (-e "../RomFiles/$FileName") {
      PrintFileLinkJson ($CheckFile, $FileName, "BIOS ROM", "");
#      print "<a href=\"RomFiles/$FileName\">BIOS ROM</a>";
    } else {
      PrintFileLinkJson ($CheckFile, $FileName, "BIOS ROM", "BIOS ROM doesn't exist");
#      print "BIOS ROM doesn't exist";
    }
  } elsif ($CheckFile eq "c") {
    $FileName = "cmos";
    if (-e "../RomFiles/$FileName") {
      PrintFileLinkJson ($CheckFile, $FileName, "CMOS file", "");
#      print "<a href=\"RomFiles/$FileName\">CMOS file</a>";
    } else {
      PrintFileLinkJson ($CheckFile, $FileName, "BIOS ROM", "CMOS file doesn't exist");
#      print "CMOS file doesn't exist";
    }
  } elsif ($CheckFile eq "v") {
    $FileName = "variable";
    if (-e "../RomFiles/$FileName") {
      PrintFileLinkJson ($CheckFile, $FileName, "Variable file", "");
#      print "<a href=\"RomFiles/$FileName\">Variable file</a>";
    } else {
      PrintFileLinkJson ($CheckFile, $FileName, "BIOS ROM", "Variable file doesn't exist");
#      print "Variable file doesn't exist";
    }
  } else {
    PrintFileLinkJson ($CheckFile, "", "", "Invalid parameters");
#    print "Invalid parameters";
  }
}

sub GenFileLinkProcess {
  my $CheckFile = $gHttpQuery->param("dl");
  my $FileName = $gHttpQuery->param("fn");
  my $NowLoc = `pwd`;
  my $Result = 1;
  
  if (!$CheckFile || !$FileName) {
    print "Invalid parameters";
  }
  
  LogPf ("Process $CheckFile");
  if ($CheckFile eq "b") {
#    $FileName = "bios.rom";
    $Result = FlashFwEx ("../../web/RomFiles/$FileName", "-g");
    if (!$Result) {
      PrintFileLinkJson ($CheckFile, $FileName, "BIOS ROM", "");
#      print "<a href=\"RomFiles/$FileName\">BIOS ROM</a>";
      return;
    }
  } elsif ($CheckFile eq "c") {
#    $FileName = "cmos";
    $Result = FlashFwEx ("../../web/RomFiles/$FileName", "-cr");
    if (!$Result) {
      PrintFileLinkJson ($CheckFile, $FileName, "CMOS file", "");
#      print "<a href=\"RomFiles/$FileName\">CMOS file</a>";
      return;
    }
  } elsif ($CheckFile eq "v") {
#    $FileName = "variable";
    $Result = FlashFwEx ("../../web/RomFiles/$FileName", "-vr");
    if (!$Result) {
      PrintFileLinkJson ($CheckFile, $FileName, "Variable file", "");
#      print "<a href=\"RomFiles/$FileName\">Variable file</a>";
      return;
    }
  } else {
#    print "Invalid parameters";
  }
  PrintFileLinkJson ($CheckFile, "", "", "Generate new file failed");
#  print "Generate new file failed";
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
  my ($RomFile, $OptFile, $RmoteAddr, $RemoteChecksum) = @_;
  my $CheckSum;
  my $Response;
  
  $Response = $ua->get("http://$RmoteAddr/UploadFiles/$RomFile");
  if ($Response->is_success) { 
    if (!StoreUrlDownloadFile ($Response->content, "$gUploadDir/$RomFile")) {
      return "Save BIOS rom file failed!";
    }
  } else {
    return "Download BIOS rom file failed!";
  }
#  $CheckSum = `md5sum $gUploadDir/$RomFile`;
#  LogPf ("$gUploadDir/$RomFile md5 checksum is $CheckSum");
  $Response = CmpCheckSum ("$gUploadDir/$RomFile", $RemoteChecksum);
  if ($Response) {
    return $Response;
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
  my ($RomFile, $FlashOptHash) = @_;
  my $FileType = $gHttpQuery->param("ft");
#  my $Checksum = $gHttpQuery->param("cs");
  my $FlashOptStr;
  my $OptValue;
  my $OptTimes;
  my $OptDelay;
  
#  DebugPf ("File type is $FileType, checksum is $Checksum", __LINE__);
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
#  `echo "do flash fw" 1>/dev/null`;
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
  my $Result;
  my %FlashOptHash = ();
  my $FlashOptStr;
  
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

sub FlashRemoteFwProcess {
  my ($RomFile, $OptFile) = @_;
  my $HostIp = $ENV{'REMOTE_ADDR'};
  my $HostPort = $gHttpQuery->param("hport");
  my $Checksum = $gHttpQuery->param("cs");
  my $Result;
  my %FlashOptHash = ();
  my $FlashOptStr;

  DebugPf ("check received addr: $HostIp/$HostPort", __LINE__);
  #
  # File is on remote server
  #
  LogPf ("Download file from remote server ($HostIp:$HostPort)");
  $Result = DownloadFromRemoteServer ($RomFile, $OptFile, "$HostIp:$HostPort", $Checksum);
  if ($Result) {
    PrintJsonTextMessage ($Result, TRUE);
    return;
  }
  FlashFwProcess ($RomFile, $OptFile);

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
    FlashRemoteFwProcess ($RomFile, $OptFile);
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


