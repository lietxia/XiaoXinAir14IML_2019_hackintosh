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

use CGI qw(:standard);
use IO::File;
use Switch;
use Fcntl qw(:flock);
use LWP::UserAgent;


use constant TRUE            => 1;
use constant FALSE           => 0;
use constant HTTP_POST_DATA  => 1;
use constant HTTP_GET_DATA   => 0;

use constant UPDATE_PROCESS_COMPLETE            => "Update process complete";
use constant UPDATE_PROCESS_COMPLETE_REBOOT     => "Update process complete, system is rebooting...";

#----------
# Global Constants
#----------
my $DateToday = `date +"%m-%d-%y"`;
chomp ($DateToday);
my $gCgiLog                  = "../../logs/cgi_$DateToday.log";
my $gGenScuXmlLog            = "../../logs/GenXml.log";
my $gUpdateScuLog            = "../../logs/UpdateXml.log";

my $gSetupHtmlFile           = "../setup.html";
my $gXmlSrcFile              = "BiosSetupInfo.xml";
my $gXmlDestFile             = "../BiosSetupInfo.xml";
my $gScuPropFile             = "ScuSettings.prop";
my $gGenScuXmlExe            = "../../bin/GenScuConfig -x ".$gXmlDestFile." -t ../Scu.txt";
my $gGenScuHtml              = "xsltproc ../setup.xslt ".$gXmlDestFile." > ".$gSetupHtmlFile;
my $gGenScuTxtExe            = "../../bin/GenScuTxt -o ../Scu.txt";
my $gUpdateScuExe            = "../../bin/UpdateScuConfig";
my $gParseScuTxtExe          = "../../bin/GenScuTxt -i ";
my $gUploadDir               = "../UploadFiles";
my $gExculsiveFile           = "running";



#----------
# Global Variables
#----------
my $gXmlFileDate             = "";
my $gYear                    = "";
my $gMonth                   = "";
my $gDay                     = "";
my $gHour                    = "";
my $gMinute                  = "";
my $gSecond                  = "";
my $gIsReboot                = FALSE;
my $gExclusiveLockFd;

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
  my ($Msg, $IsError) = @_;

  print '{"resp": "' . $Msg . '", ';
  if ($IsError) {
    print '"iserr": "true"}';
  } else {
    print '"iserr": "false"}';
  }
  LogPf ($Msg);
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

sub ReadUrlGetParams {
  my $HttpData = $ENV{'QUERY_STRING'};
  my @pairs;
  my $pair;
  my %UrlParams;
  my ($name, $value);

  if (!$HttpData) {
    return;
  }

  @pairs = split(/&/, $HttpData);

  foreach $pair (@pairs) {
    ($name, $value) = split(/=/, $pair);
#    $value =~ tr/+/ /;
#    $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
    $UrlParams{$name} = $value;
  }

  return %UrlParams;
}
sub IsProcessRunning {
  # Open the file for appending.  Note the file path is quoted
  # in the error message.  This helps debug situations where you
  # have a stray space at the start or end of the path.
#  open (my $fh, '>>', $file) or die "Could not open '$file' - $!";
  open ($gExclusiveLockFd, '>', $gExculsiveFile) or return TRUE;

  # Get exclusive lock (will block until it does)
#  flock($fh, LOCK_EX) or die "Could not lock '$file' - $!";
  flock ($gExclusiveLockFd, LOCK_EX) or return TRUE;

  # Do something with the file here...
  #
  # Write process id of this process in locked file to identify which process
  # is running or not but still own this file
  #
  print $gExclusiveLockFd $$;

  # Do NOT use flock() to unlock the file if you wrote to the
  # file in the "do something" section above.  This could create
  # a race condition.  The close() call below will unlock the
  # file for you, but only after writing any buffered data.

  # In a world of buffered i/o, some or all of your data may not
  # be written until close() completes.  Always, always, ALWAYS
  # check the return value of close() if you wrote to the file!
#  close ($fh) or die "Could not write '$file' - $!";
#  close ($gExclusiveLockFd) or return TRUE;

  return FALSE;
}

sub ProcessFinish {
  # In a world of buffered i/o, some or all of your data may not
  # be written until close() completes.  Always, always, ALWAYS
  # check the return value of close() if you wrote to the file!
#  close ($fh) or die "Could not write '$file' - $!";
  close ($gExclusiveLockFd) or return FALSE;

  return TRUE
}

#----------
# Functions
#----------

sub IsOutOfDate {
  my $PostDataHashRef = $_[0];
  my $FileGenTimeClient = $PostDataHashRef->{'FileGenTime'};
#  my $FileGenTimeLocal = `stat -c %Z $gXmlDestFile`;
  my $FileGenTimeLocal = `stat -c %Z $gSetupHtmlFile`;

  chomp ($FileGenTimeLocal);
  chomp ($FileGenTimeClient);
#  $FileGenTimeLocal = trimHttpNewLine (trim ($FileGenTimeLocal));
#  $FileGenTimeClient = trimHttpNewLine (trim ($FileGenTimeClient));

  LogPf ("FileGenTimeLocal: $FileGenTimeLocal, FileGenTimeClient: $FileGenTimeClient.");
  if ($FileGenTimeLocal ne $FileGenTimeClient) {
    return TRUE;
  }

  return FALSE;
}

#---
# Execute scu settings variable update
#---
sub UpdateScuSettings {
  my ($ExitFunNo, $ScuFile) = @_;
  my $Result = "";

  #
  # Use  2>&1>$gUpdateScuLog to log record would occur
  # sh: Syntax error: redirection unexpected
  #
  switch ($ExitFunNo) {
    case /1|3/ {
      #
      # 1: Save changes and exit
      # 3: Save changes
      #
      LogPf ("Save changes ($ExitFunNo)");
#      DebugPf ("$gUpdateScuExe -s $ScuFile 1>>$gUpdateScuLog 2>&1>>$gUpdateScuLog", __LINE__);
#      `$gUpdateScuExe -s $ScuFile 1>>$gUpdateScuLog 2>&1>>$gUpdateScuLog`;
#      $Result = system ("$gUpdateScuExe -s $ScuFile &>$gUpdateScuLog 2>&1>$gUpdateScuLog");
#      `$gUpdateScuExe -s $ScuFile &>$gUpdateScuLog 2>&1>$gUpdateScuLog`;
      `$gUpdateScuExe -s $ScuFile 1>>$gUpdateScuLog`;
      $Result = ($? >> 8);
    }

    case /5/ {
      #
      # 5: Load optimal defaults
      #
      LogPf ("Load optimal defaults ($ExitFunNo)");
      `$gUpdateScuExe -d 1>>$gUpdateScuLog`;
      $Result = ($? >> 8);
    }

    #
    # NOTE: Load customized defaults doesn't run here!!
    #
    case /6/ {
      #
      # 6: Load customized defaults
      #
      # NOTE: Should not update settings here, generate a file for client to
      #       change settings on browser instead.
      #
#      LogPf ("Load customized defaults ($ExitFunNo)");
#      `$gUpdateScuExe -l &>$gUpdateScuLog`;
#      $Result = ($? >> 8);
    }

    case /7/ {
      #
      # 7: Save customized defaults
      #
      LogPf ("Save customized defaults ($ExitFunNo)");
#      `$gUpdateScuExe -c $ScuFile 1>>$gUpdateScuLog 2>&1>>$gUpdateScuLog`;
      `$gUpdateScuExe -c $ScuFile 1>>$gUpdateScuLog`;
      $Result = ($? >> 8);
    }

    else {
      #
      # 2: Discard changes and exit
      # 4: Discard changes
      # Other situations
      #
    }
  }

  LogPf ("Return Code is $Result");

  if ($Result != 0) {
    DebugPf ("Return FALSE", __LINE__);
    return FALSE;
  }
  DebugPf ("Return TRUE", __LINE__);

  return TRUE;
}

#---
# Check if ScuSettings.prop file exists or not
#---
sub IsFileExist {
  my $TargetFile = $_[0];

  if (-e $TargetFile) {
    return TRUE;
  }

  return FALSE;
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
    LogPf ("Can't find file: $TargetSrc");
    return FALSE;
  }
}

#---
# Move source file to destinaction
#---
sub MoveFile {
  my $TargetSrc = $_[0];
  my $TargetDes = $_[1];

  if (IsFileExist ($TargetSrc)) {
    `mv -f $TargetSrc $TargetDes 2>>$gCgiLog`;
    return TRUE;
  } else {
    LogPf ("Can't find file: $TargetSrc");
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
  my ($RemoteAddr, $RemoteFileName, $LocalFilePath) = @_;
  my $Response;

  LogPf ("Download $RemoteFileName from $RemoteAddr and save as $LocalFilePath");
  $Response = $ua->get ("http://$RemoteAddr/UploadFiles/$RemoteFileName");
  if ($Response->is_success) {
    LogPf ("Download success");
    if (!StoreUrlDownloadFile ($Response->content, $LocalFilePath)) {
      return "Save SCU file failed!";
    }
  } else {
    LogPf ($Response->status_line);
    return "Download SCU file failed!";
  }

  return "";
}

sub UpdateSystemTime {
  my $ExitFunNo = $_[0];
  my $Result;

  LogPf ("Update system time...");
  if (($ExitFunNo == 1) || ($ExitFunNo == 3)) {
    if (($gYear ne "") && ($gMonth ne "") && ($gDay ne "") &&
      ($gHour ne "") && ($gMinute ne "") && ($gSecond ne "")) {

      LogPf ("New time is [$gYear/$gMonth/$gDay $gHour:$gMinute:$gSecond]");
      `date -s "$gYear/$gMonth/$gDay $gHour:$gMinute:$gSecond" 1>/dev/null`;
      $Result = ($? >> 8);

      if ($Result != 0) {
        return "Set date failed";
      }
      `hwclock -w`;
      $Result = ($? >> 8);
      if ($Result == 0) {
        return "Write clock failed";
      }
    }
  }

  return "";
}

sub CreatePostDataHashTbl {
  my %PostDataHash = ();
  my $PostData;
  my @PropDataArray;
  my ($Key, $Val);
  my $i;

  DebugPf ("Read post data...", __LINE__);
  read (STDIN, $PostData, $ENV{'CONTENT_LENGTH'});
  #
  # split string to each key-value
  #
  @PropDataArray = split (/&/, $PostData);
  foreach $i (0 ..$#PropDataArray) {
    ($Key, $Val) = split (/=/, $PropDataArray[$i]);
    $Key = trim ($Key);
    $Val = trim ($Val);
    $PostDataHash{$Key} = $Val;
  }

  return \%PostDataHash;
}

sub RemovePostData {
  my $ScuFile = $_[0];

  DebugPf ("Remove post data file: $ScuFile", __LINE__);
  if (-e $ScuFile) {
    unlink $ScuFile;
  }
}

sub GenNewScuFile {
  my $Result;

  LogPf ("Generate new file");
#  `$gGenScuXmlExe &>$gGenScuXmlLog 2>&1>>$gGenScuXmlLog`;
  `$gGenScuXmlExe 1>>$gGenScuXmlLog`;
  $Result = ($? >> 8);
  if ($Result != 0) {
    return "Generate a new SCU file failed";
  }

  `$gGenScuHtml`;
  $Result = ($? >> 8);
  if ($Result != 0) {
    return "Translate XML to HTML failed";
  }

  return "";
}

sub ReadDlFileSaveToPropFile {
  my ($DlFile, $ScuFile) = @_;
  my $FileData;
  my $Item;
  my @Pair;
  my ($Key, $Val);


  LogPf ("Read downloaded file ($DlFile) and parse to property file ($ScuFile)");
  if (!open(DLFILE, "<$DlFile")) {
    return "Open downloaded file failed";
  }
  $FileData = <DLFILE>;
  close (DLFILE);

  if (!open(FILE, ">$ScuFile")) {
    return "Open property file failed";
  }
  @Pair = split (/&/, $FileData);
  foreach $Item (@Pair) {
#    DebugPf ($Item, __LINE__);
    ($Key, $Val) = split (/=/, $Item);
    if ($Key eq "FileGenTime") {
#      $gXmlFileDate = $Val;
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
      # Remote reboot setting comes from url parameter
    } else {
      print FILE "$Key=$Val\n";
    }
  }

  close (FILE);

  return "";
}

sub SavePostData {
  my ($PostDataHashRef, $ScuFile) = @_;
  my ($Key, $Val);

  DebugPf ("Save post data to $ScuFile", __LINE__);

  if (!open(FILE, ">$ScuFile")) {
    return "Open property file failed";
  }
  for $Key (keys %$PostDataHashRef) {
    $Val = $PostDataHashRef->{$Key};

    if ($Key eq "FileGenTime") {
#      $gXmlFileDate = $Val;
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
      print FILE "$Key=$Val\n";
      if ($Val eq "1") {
        $gIsReboot = TRUE;
      } else {
        $gIsReboot = FALSE;
      }
    } else {
      print FILE "$Key=$Val\n";
    }
    `echo $Key=$Val >>$gUpdateScuLog`;
  } # End of for loop

  close (FILE);

  return "";
}

sub RebootSystem {
    #
    # at service may not exist in SUSE, need some common way to reboot
    #
#    `at -f ../../bin/RestartSystem now + 1 minutes`;
#    `shutdown -r now`;
#    `nohup at -f /var/local/insyde/scu_utility/bin/RestartSystem now + 1 minutes &`;
#    `at -f /var/local/insyde/scu_utility/bin/RestartSystem now + 1 minutes 1>/dev/null 2>&1>/dev/null`;
#    return "Process complete <br /> System reboots within 1 minute.";

    #
    # As for reaping, children of a parent whose SIGCHLD handler is
    # explicitely set to IGNORE will be reaped automatically by the system.
    #
#    $SIG{CHLD} = "IGNORE"; # Still blocking
    my $Pid = fork();

    LogPf ("Do reboot...");
    if (not defined $Pid) {
      return "Resources not available";
    } elsif ($Pid == 0) {
      LogPf ("child process starts...");
      sleep 3;
 #     `shutdown -r now &>/dev/null 2>&1>/dev/null`;
      `shutdown -r now 1>>/dev/null`;
      LogPf ("child process ends...");
      exit (0);
    } else {
      LogPf ("Do parent process first to return message...");
    }
    #
    # Client would get response after child process terminates
    # (because child sleep few seconds)
    #

#    return "Process complete <br /> System reboots within 30 seconds.";
    return "";
}

sub UpdateScuProcess {
  my ($ExitFunNo, $ScuFile) = @_;
  my $Result;

  $Result = UpdateScuSettings ($ExitFunNo, $ScuFile);
  if ($Result == FALSE) {
#    PrintJsonTextMessage ("Update failed", TRUE);
    return "Update failed";
  }
  $Result = UpdateSystemTime ($ExitFunNo, $ScuFile);
  if ($Result) {
#    PrintJsonTextMessage ($Result, TRUE);
    return $Result;
  }
  $Result = GenNewScuFile ();
  if (!$Result) {
#    PrintJsonTextMessage ("Process complete", FALSE);
    return "";
  } else {
#    PrintJsonTextMessage ($Result, TRUE);
  }
  return $Result;
}

sub LoadScuProcess {
  my $ExitFunNo = $_[0];
  my $Result = "";

  #
  # Generate customized defaults as a hash table for client
  #
  DebugPf ("Load defaults...", __LINE__);
  # NOTE: Should not update settings here, generate a file for client to
  #       change settings on browser instead.
  #

  if (!$Result) {
    PrintJsonTextMessage ("Process complete", FALSE);
  } else {
    PrintJsonTextMessage ($Result, TRUE);
  }
}

sub ScuExitFuncProcess {
  my ($ExitFunNo, $PostDataHashRef) = @_;
  my $Result;

  DebugPf ("Exit function no: $ExitFunNo", __LINE__);
  #
  # 1: Save changes and exit
  # 3: Save changes
  # 5: Load optimal defaults # Complete on client
  # 6: Load customized defaults
  # 7: Save customized defaults
  #
  if (($ExitFunNo == 1) || ($ExitFunNo == 3) || ($ExitFunNo == 7)) {
    my $Result;

    $Result = SavePostData ($PostDataHashRef, $gScuPropFile);
    if ($Result) {
      RemovePostData ($gScuPropFile);
      PrintJsonTextMessage ("Store post data failed", TRUE);
      return;
    }
    $Result = UpdateScuProcess ($ExitFunNo, $gScuPropFile);
    RemovePostData ($gScuPropFile);
    if ($Result) {
      PrintJsonTextMessage ($Result, TRUE);
      return;
    }
    if ($gIsReboot) {
      $Result = RebootSystem ();
      if (!$Result) {
        PrintJsonTextMessage (UPDATE_PROCESS_COMPLETE_REBOOT, FALSE);
      } else {
        PrintJsonTextMessage ($Result, TRUE);
      }
    } else {
      PrintJsonTextMessage (UPDATE_PROCESS_COMPLETE, FALSE);
    }
  } elsif ($ExitFunNo == 6) {
    LoadScuProcess ($ExitFunNo);
  } else {
    PrintJsonTextMessage ("Invalid parameters", TRUE);
  }
}

sub RemoteScuDataProcess {
  my ($ExitFunNo, $RemoteAddr, $ScuFileName) = @_;
  my $LocalFilePath;
  my $Result;

  DebugPf ("Exit function no: $ExitFunNo, $RemoteAddr, $ScuFileName", __LINE__);
  #
  # 1: Save changes and exit
  # 3: Save changes
  # 5: Load optimal defaults # Complete on client
  # 6: Load customized defaults
  # 7: Save customized defaults
  #
  if (($ExitFunNo == 1) || ($ExitFunNo == 3) || ($ExitFunNo == 7)) {
    my $HttpQuery = new CGI;
    my $IsReboot = $HttpQuery->param("xREBOOTx");

    $LocalFilePath = "$gUploadDir/$ScuFileName";
    $Result = DownloadFromRemoteServer ($RemoteAddr, $ScuFileName, $LocalFilePath);
    if ($Result) {
      PrintJsonTextMessage ($Result, TRUE);
      return;
    }
    $Result = ReadDlFileSaveToPropFile ($LocalFilePath, $gScuPropFile);
    if ($Result) {
      PrintJsonTextMessage ($Result, TRUE);
      return;
    }
    $Result = UpdateScuProcess ($ExitFunNo, $gScuPropFile);
    RemovePostData ($gScuPropFile); # Downloaded file
    RemovePostData ($LocalFilePath); # Property file
    if (!$Result) {
      my $HttpQuery = new CGI;
      my $IsReboot = $HttpQuery->param("xREBOOTx");

      if ($IsReboot) {
        $Result = RebootSystem ();
        if (!$Result) {
          PrintJsonTextMessage (UPDATE_PROCESS_COMPLETE_REBOOT, FALSE);
        } else {
          PrintJsonTextMessage ($Result, TRUE);
        }
      } else {
        PrintJsonTextMessage (UPDATE_PROCESS_COMPLETE, FALSE);
      }
    } else {
      PrintJsonTextMessage ($Result, TRUE);
    }
  } elsif ($ExitFunNo == 6) {
    LoadScuProcess ($ExitFunNo);
  } else {
    PrintJsonTextMessage ("Invalid parameters", TRUE);
  }
}

sub UpdateTxtScuProcess {
  my $TxtConfigPath = $_[0];
  my $Result;

  if (! -e $TxtConfigPath) {
    return "Text configuration file doesn't exist";
#    PrintJsonTextMessage ("Text configuration file doesn't exist", TRUE);
#    return FALSE;
  }
#  `$gParseScuTxtExe $TxtConfigPath 1>>$gUpdateScuLog 2>&1>>$gUpdateScuLog`;
  `$gParseScuTxtExe $TxtConfigPath 1>>$gUpdateScuLog`;
  $Result = ($? >> 8);
  LogPf ("Update text config result: $Result");
  if ($Result != 0) {
    #
    # 0 is STATUS_SUCCESS
    # 1 is STATUS_FAILURE
    # 2 is STATUS_BUFFER_TOO_SMALL
    # 3 is STATUS_SYNTAX_ERROR
    #
    if ($Result == 3) {
      return "Syntax error";
    } else {
      return "Parse and update SCU settings failed";
    }
#    PrintJsonTextMessage ("Parse and update SCU settings failed", TRUE);
#    return FALSE;
  }
=head
  `$gGenScuTxtExe &>$gUpdateScuLog 2>&1>>$gUpdateScuLog`;
  $Result = ($? >> 8);
  if ($Result != 0) {
    return "Generate new text configuration failed";
#    PrintJsonTextMessage ("Generate new text configuration failed", TRUE);
#    return FALSE;
  }
=cut
#  `$gGenScuXmlExe &>$gGenScuXmlLog 2>&1>>$gGenScuXmlLog`;
  `$gGenScuXmlExe 1>>$gGenScuXmlLog`;
  $Result = ($? >> 8);
  if ($Result != 0) {
    return "Generate new configuration failed";
#    PrintJsonTextMessage ("Generate new configuration failed", TRUE);
#    return FALSE;
  }
  `$gGenScuHtml`;

  return "";
#  PrintJsonTextMessage ("Update with text configurateion complete", FALSE);
#  return TRUE;
}

sub UpdateScuWithTxtConfigProcess {
  my $TxtConfiFileName = $_[0];
  my $TxtFilePath = "$gUploadDir/$TxtConfiFileName";
  my $Result;

  #
  # TODO: Check if filename is illegal
  #
  $Result = UpdateTxtScuProcess ($TxtFilePath);
  if (!$Result) {
#    $Result = RebootSystem ();
#    PrintJsonTextMessage ($Result, FALSE);
    PrintJsonTextMessage (UPDATE_PROCESS_COMPLETE, FALSE);
  } else {
    PrintJsonTextMessage ($Result, TRUE);
  }
}

sub UpdateRemoteServerWithTxtConfigProcess {
  my ($RemoteAddr, $TxtScuFileName) = @_;
  my $LocalFilePath;
  my $Result;

  #
  # TODO: Check if filename is illegal
  #
  $LocalFilePath = "$gUploadDir/$TxtScuFileName";
  $Result = DownloadFromRemoteServer ($RemoteAddr, $TxtScuFileName, $LocalFilePath);
  if ($Result) {
    PrintJsonTextMessage ($Result, TRUE);
    return;
  }
  $Result = UpdateTxtScuProcess ($LocalFilePath);
  if (!$Result) {
    my $HttpQuery = new CGI;
    my $IsReboot = $HttpQuery->param("xREBOOTx");

    if ($IsReboot) {
      $Result = RebootSystem ();
    } else {
      PrintJsonTextMessage (UPDATE_PROCESS_COMPLETE, FALSE);
      return;
    }
    if (!$Result) {
      PrintJsonTextMessage (UPDATE_PROCESS_COMPLETE_REBOOT, FALSE);
    } else {
      PrintJsonTextMessage ($Result, TRUE);
    }
  } else {
    PrintJsonTextMessage ($Result, TRUE);
  }
}

sub MainProcess {
  my %HttpParamHash; # init hash table
  my $FuncName;
  my $ExitFunNo;

  %HttpParamHash = ReadUrlGetParams ();
  if (!%HttpParamHash) {
    PrintJsonTextMessage ("Invalid parameters", TRUE);
    return;
  }

  $FuncName = $HttpParamHash{'func'};
  if (!$FuncName) {
    PrintJsonTextMessage ("Invalid parameters", TRUE);
    return;
  }

#  `echo "" >$gUpdateScuLog`;
  if ($FuncName eq "sef") {
    #
    # Scu exit function process
    #
    my $PostDataHashRef = {};

    $ExitFunNo = $HttpParamHash{'ef'};
    if (!$ExitFunNo) {
      PrintJsonTextMessage ("Invalid parameters", TRUE);
      return;
    }
    LogPf ("Scu exit function process");
    $PostDataHashRef = CreatePostDataHashTbl ();
    if (IsOutOfDate ($PostDataHashRef)) {
      PrintJsonTextMessage ("Settings is out of date, please refresh and try again.", TRUE);
      return;
    }
    ScuExitFuncProcess ($ExitFunNo, $PostDataHashRef);
  } elsif ($FuncName eq "stc") {
    #
    # Update SCU settings with text configuration file
    #
    my $ScuFileName = $HttpParamHash{'fn'};

    if (!$ScuFileName) {
      PrintJsonTextMessage ("Invalid parameters", TRUE);
      return;
    }
    LogPf ("Remote scu data process");
    UpdateScuWithTxtConfigProcess ($ScuFileName);
  } elsif ($FuncName eq "rsp") {
    #
    # Remote scu data process
    #
    my $ScuFileName = $HttpParamHash{'fn'};
    my $HostIp = $ENV{'REMOTE_ADDR'};
    my $HostPort = $HttpParamHash{'hport'};

    $ExitFunNo = $HttpParamHash{'ef'};
    if (!$ExitFunNo || !$ScuFileName) {
      PrintJsonTextMessage ("Invalid parameters", TRUE);
      return;
    }
    if (!$HostPort) {
      $HostPort = "80";
    }
    LogPf ("Remote scu data process");
    RemoteScuDataProcess ($ExitFunNo, "$HostIp:$HostPort", $ScuFileName);
  } elsif ($FuncName eq "rtc") {
    #
    # Update remote SCU settings with text configuration file
    #
    my $ScuFileName = $HttpParamHash{'fn'};
    my $HostIp = $ENV{'REMOTE_ADDR'};
    my $HostPort = $HttpParamHash{'hport'};

    if (!$ScuFileName) {
      PrintJsonTextMessage ("Invalid parameters", TRUE);
      return;
    }
    if (!$HostPort) {
      $HostPort = "80";
    }
    UpdateRemoteServerWithTxtConfigProcess ("$HostIp:$HostPort", $ScuFileName);
  } else {
    PrintJsonTextMessage ("Invalid parameters", TRUE);
  }
}

#---
# Main process
#---
sub Main {
  LogProcessStart ();

  #
  # Check process status and file gen time before save post data,
  # must guaratee that post data would be rejected.
  # Or we save post data each time, but remove it when process finished
  #
  if (IsProcessRunning ()) {
    PrintJsonTextMessage ("Update process is running, please wait for a while.", TRUE);
    return;
  }
  MainProcess ();
  ProcessFinish ();
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

