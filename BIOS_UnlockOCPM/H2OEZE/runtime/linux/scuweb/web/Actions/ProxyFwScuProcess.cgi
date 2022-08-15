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
use warnings;

use CGI qw(:standard);
use CGI::Carp;
use LWP::UserAgent;
use HTTP::Status ();
use File::Basename;
use IO::File;


#----------
# Global Constants
#----------

use constant TRUE            => 1;
use constant FALSE           => 0;

# Logs
my $DateToday                = `date +"%m-%d-%y"`;
chomp ($DateToday);
my $gCgiLog                  = "../../logs/cgi_$DateToday.log";

# Files and folders
my $gPlatformInfoFile        = "../PlatformInfo.txt";
my $gFwFrameHtml             = "../FwFrame.html";
my $gUploadFrame             = "../UploadFrame.html";
my $gUploadDir               = "../UploadFiles"; 
my $gTempPostDataFileName    = "PostData.txt";
my $gTempFlashOptFile        = "FlashOptions.txt";

# Others
my $gSafeFilenameCharacters  = "a-zA-Z0-9_.-"; 

# Javascript function names
my $gInvalidOperationAlarm   = "InvalidOperationAlarm";
my $gFwIframeInitJsFunc      = "InitUploadFw";
my $gUploadInitJsFunc        = "InitUploadFile";

#----------
# Global Variables
#----------
#my $gHttpQuery               = new CGI; 
my $gHttpQuery; 
my $gPlatformInfoStr;
my $gVersionStr;


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

sub CallClientJsFunc {
  my ($JsFunc, $Msg, $IsError) = @_;
  my $ArgErr = "false";
  
  if ($IsError) {
    $ArgErr = "true";
  }
  DebugPf ("Return script is $ArgErr|$IsError", __LINE__);
  print "<script type=\"text/javascript\">";
  print "window.parent." . $JsFunc . "('$Msg', $ArgErr);";
  print "</script>";
  LogPf ($Msg);
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
  foreach $pair (@pairs)
  {
    ($name, $value) = split(/=/, $pair);
#    $value =~ tr/+/ /;
#    $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
    $UrlParams{$name} = $value;
    LogPf ("$name=$value");
  }
  
  return %UrlParams;
}

sub ValidateIpPort {
  my ($Ip, $Port) = @_;
  
  if (!$Ip || !$Port) {
    return "Invalide parameters";
  }
  DebugPf ("TargetIp=$Ip, TargetPort=$Port", __LINE__);
  #
  # Check ip format
  #
  if (!($Ip =~ /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/)) {
    return "Invalid IP formate";
  }
  
  return "";
}

sub ValidateIdIpPort {
  my ($Id, $Ip, $Port) = @_;
  
  if (!$Id || !$Ip || !$Port) {
#    DebugPf ("Empty id or ip or port", __LINE__);
    return "Invalide parameters";
  }
  DebugPf ("ClientId=$Id, TargetIp=$Ip, TargetPort=$Port", __LINE__);
  #
  # Check ip format
  #
  if (!($Ip =~ /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/)) {
#    DebugPf ("Invalid IP formate", __LINE__);
    return "Invalid IP formate";
  }
  
  return "";
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

sub ParseAndPrintHtmlText {
  my $HtmlFile = $_[0];
  my @HtmlBody;
  
  open (HTMLFILE, "<$HtmlFile") or return "Can't open html file"; 
  binmode HTMLFILE; 
  
#  print <HTMLFILE>;
  #
  # Change action location, remove "Actions/" to avoid 
  # browser append Actions/ again.
  #
  @HtmlBody = <HTMLFILE>;
  foreach my $Item (@HtmlBody) {
    if ($Item =~ m/Actions/) {
      $Item =~ s/Actions\///g;
    }
    print $Item;
  }

  close HTMLFILE;
 
  return ""; 
}

sub CmpCheckSum {
  my ($LocalFilePath, $RemoteFileCs) = @_;
  my $LocalFileCs;
  my $Result;
  my @Md5Result;
  
  $LocalFileCs = `md5sum $LocalFilePath`;
  $Result = ($? >> 8);
  DebugPf ("Gen md5 checksum result is $Result", __LINE__);
  if ($Result == 0) {
    @Md5Result = split (/ /, $LocalFileCs);
    LogPf ("Compare 2 checksums, local file is '" . $Md5Result[0] . 
      "', remote file is '$RemoteFileCs'");
    if ($RemoteFileCs ne $Md5Result[0]) {
      return "Checksum is not correct";
    }
    
    return "";
  } else {
    return "Generate checksum failed";
  }
}

#----------
# Functions
#----------

sub TestRemoteConn {
  my $ua = LWP::UserAgent->new;
  my $response;
  
  $ua->timeout($_[1]);
  $response = $ua->get("http://".$_[0]."/Actions/TestConn.cgi");

  if (!$response->is_error) {
#    return $response->decoded_content;
    return $response->content;
  } else {
#    printf "Status Code: %d; %s", $response->code, $response->message;

    #
    # record the timeout
    # Suse doesn't allowed while "strict subs"
    #
#    if ($response->code == HTTP::Status::HTTP_REQUEST_TIMEOUT) {
#      LogPf ("Status Code: $response->code; $response->message");
#    }
    return GenErrorMsgStr ($response->code, $response->message);
  }
}

sub SubmitDataToRemoteServer {
  my $ua = LWP::UserAgent->new;
  my $HttpData = "";
  my $Reponse;
  
  read (STDIN, $HttpData, $ENV{'CONTENT_LENGTH'});
  
  $Reponse = $ua->post("http://".$_[0]."/Actions/TestSubmitForms.cgi", $HttpData);
  if (!$Reponse->is_error) {
    return $Reponse->content;
  } else {
#    if ($Reponse->code == HTTP::Status::HTTP_REQUEST_TIMEOUT) {
#      LogPf ("Status Code: $Reponse->code; $Reponse->message");
#    }
    return GenErrorMsgStr ($Reponse->code, $Reponse->message);
  }
}

sub CreateUploadedFile {
  my ($Fd, $ToSaveFile) = @_;
  
#  open (UPLOADFILE, ">$ToSaveFile") or die "$!"; 
  open (UPLOADFILE, ">$ToSaveFile") or return FALSE; 
  binmode UPLOADFILE; 

  while (<$Fd>) { 
    print UPLOADFILE; 
  } 

  close UPLOADFILE;
  
  return TRUE;
}

sub InitIframe {
  my $iFrameHtml = $_[0];
  
  print "<script type=\"text/javascript\">";
  print "window.parent." . $iFrameHtml . "();";
  print "</script>";
}

sub SaveUploadFile {
  my ($FileDir, $Filename, $ClientCheckSum) = @_;
  my ($name, $path, $extension);
  my $ToSaveFile;
  
  LogPf ("Original filename: $Filename");
  
  #
  # Parse filename and make sure that filename is valid
  #
  ($name, $path, $extension) = fileparse ($Filename, '\..*'); 
  $Filename = $name . $extension; 
  $Filename =~ tr/ /_/; 
  $Filename =~ s/[^$gSafeFilenameCharacters]//g;

  if ($Filename =~ /^([$gSafeFilenameCharacters]+)$/) {
  } else { 
    LogPf ("Invalid filename: $Filename");
    return "Invalid filename";
  }
  
  #
  # Get client id or use the default filename
  #
  $ToSaveFile = "$FileDir/$Filename";
  LogPf ("Final filename: $ToSaveFile");
  
  #
  # Save uploaded file transform from client
  #
  if (CreateUploadedFile ($gHttpQuery->param("FileToUpload"), $ToSaveFile)) {
    if ($ClientCheckSum) {
      return CmpCheckSum ($ToSaveFile, $ClientCheckSum);
    } else {
      return "";
    }
  } else {
    return "Create file failed";
  }
}

#
# If create a CGI object, this function wouldn't work
#
sub SavePostData {
  my ($FileDir, $FileName) = @_;
  my $PostData;

  LogPf ("Post data save to $FileName");
  #
  # STDIN doesn't work when we use new CGI ();
  #  
  DebugPf ("Save post data...", __LINE__);
  read (STDIN, $PostData, $ENV{'CONTENT_LENGTH'});
#  DebugPf ("HttpData: $PostData", __LINE__);
  if (!open(FILE, ">$FileDir/$FileName")) {
    #
    # the '\n' at the end of line means do not show the error line number and source code file name
    #
#    die "Can't not open logfile: $!\n";
    LogPf ("Can't open $FileDir/$FileName");
    return FALSE;
  }  
  
  if ($PostData) {
    print FILE $PostData;
  } else {
    LogPf ("Http post data is empty");
  }

  close FILE;
  
  return TRUE;
}

sub WriteFlashSingleOptInFile {
  my ($ParamName, $HasParam) = @_;

  if ($gHttpQuery->param($ParamName)) {
    DebugPf ("Write param to file: $ParamName", __LINE__);
    if ($HasParam) {
      print FILE "&$ParamName=".$gHttpQuery->param($ParamName);
    } else {
      print FILE "$ParamName=".$gHttpQuery->param($ParamName);
    }
    $HasParam = TRUE;
  }
  
  return $HasParam;
}

sub WriteFlashMultiOptInFile {
  my ($ParamName, $HasParam) = @_;
  my @FlashOpt;
  my $Idx;

  if ($gHttpQuery->param($ParamName)) {
    DebugPf ("Write param to file: $ParamName", __LINE__);
    @FlashOpt = $gHttpQuery->param($ParamName);
    if ($HasParam) {
      print FILE "&$ParamName=";
    } else {
      print FILE "$ParamName=";
    }
    for ($Idx = 0; $Idx<=$#FlashOpt; $Idx++) {
      if ($Idx != 0) {
        print FILE " ";
      }
      print FILE $FlashOpt[$Idx];
    }
    $HasParam = TRUE;
  }
  
  return $HasParam;
}

sub SaveFlashOptions {
  my ($FileDir, $FileName) = @_;
  my $FilePath;
  my @CheckBoxOpt;
  my @FlashOpt;
  my $FlashAll;
  my $HasParam = FALSE;
  
  $FilePath = "$FileDir/$FileName";
  LogPf ("Flash options file: $FilePath");
  if (!open(FILE, ">$FilePath")) {
    #
    # the '\n' at the end of line means do not show the error line number and source code file name
    #
#    die "Can't not open logfile: $!\n";
    LogPf ("Can't open $FilePath");
    return "Can't open flash options file";
  }
  
  $HasParam = WriteFlashMultiOptInFile ("FlashOpt", $HasParam);
  $HasParam = WriteFlashMultiOptInFile ("FlashRom", $HasParam);
  $HasParam = WriteFlashSingleOptInFile ("SelFileType", $HasParam);
  $HasParam = WriteFlashSingleOptInFile ("MsgMode", $HasParam);
  $HasParam = WriteFlashSingleOptInFile ("rt-times", $HasParam);
  $HasParam = WriteFlashSingleOptInFile ("rt-delay", $HasParam);
  $HasParam = WriteFlashSingleOptInFile ("FinishAct", $HasParam);

  close (FILE);
  
  return "";
}

sub SaveSubmitSettings {
  my $ClientId = $_[0];
  my $FileName;
  my $Result;
  
  if (!$ClientId) {
    PrintJsonTextMessage ("Invalide parameters", TRUE);
#    CallClientJsFunc ("SubmitClientSettingsComplete", "Invalide parameters", TRUE);
    return;
  }
  
  LogPf ("Client ID: $ClientId");
  #
  # Read post data
  #
  $FileName = "$ClientId-$gTempPostDataFileName";
  $Result = SavePostData ($gUploadDir, $FileName);
  if (!$Result) {
    PrintJsonTextMessage ($Result, TRUE);
#    CallClientJsFunc ("SubmitClientSettingsComplete", $Result, TRUE);
    return;
  }
  LogPf ("Result: $Result");
  
  #
  # Gen a JSON string for client
  #
  $Result = '{"fn": "' . $FileName . '", ' .
#             '"ft": "' . $FileType . '", ' .
             '"resp": "Uploaded, ready to update!", ' .
             '"iserr" : "false"}'; 
  print $Result;
#    PrintJsonTextMessage ($Result, FALSE);
#  CallClientJsFunc ("SubmitClientSettingsComplete", $Result, FALSE);
}

sub SaveTxtConfigFile {
  my ($ClientId, $UploadFileName, $CheckSum);
  my $FileName;
  my $Result;
  
  $gHttpQuery = new CGI;
  
  $ClientId = $gHttpQuery->param("FileUploadId");
  $UploadFileName = $gHttpQuery->param("FileToUpload");
  $CheckSum = $gHttpQuery->param("FileChecksum");
  
  LogPf ("Client ID: $ClientId");
  
  if (!$UploadFileName) {
    CallClientJsFunc ("UploadTxtConfigComplete", 
      "Error! Uploaded file name doesn't exist!", TRUE);
    return "Can't get uploaded file";
  }
  #
  # Save upload file
  #
  $FileName = "$ClientId-$UploadFileName";
  $Result = SaveUploadFile ($gUploadDir, $FileName, $CheckSum);
  if ($Result) {
    CallClientJsFunc ("UploadTxtConfigComplete", $Result, TRUE);
    return;
  }
  #
  # Gen a JSON string for client
  #
  $Result = '{"fn": "' . $FileName . '", ' . 
             '"cs": "' . $CheckSum . '", ' . 
             '"resp": "Uploaded, ready to update!"}'; 
  
  CallClientJsFunc ("UploadTxtConfigComplete", $Result, FALSE);
  ParseAndPrintHtmlText ($gUploadFrame);
}

sub SaveTempUploadFileAndPostData {
  my ($ClientId, $FileType, $UploadFileName, $CheckSum);
  my ($Reponse, $Result);
  my ($RomFileName, $OptFileName);
  
  $gHttpQuery = new CGI;
  
  $ClientId = $gHttpQuery->param("FileUploadId");
  $FileType = $gHttpQuery->param("SelFileType");
  $UploadFileName = $gHttpQuery->param("FileToUpload");
  $CheckSum = $gHttpQuery->param("FileChecksum");
  
  if (!$ClientId || !$CheckSum) {
    CallClientJsFunc ("UploadFileAndDataComplete", "Invalide parameters", TRUE);
    return;
  }
  
  LogPf ("Client ID: $ClientId, Check sum: $CheckSum");
  
  if (!$UploadFileName) {
    CallClientJsFunc ("UploadFileAndDataComplete", 
      "Error! Uploaded file name doesn't exist!", TRUE);
    return "Can't get uploaded file";
  }
  $RomFileName = $ClientId . "-" . $UploadFileName;
  $OptFileName = $ClientId . "-" . $gTempFlashOptFile;
  #
  # Save upload file
  #
  $Result = SaveUploadFile ($gUploadDir, $RomFileName, $CheckSum);
  DebugPf ("Result: $Result", __LINE__);
  if ($Result) {
    CallClientJsFunc ("UploadFileAndDataComplete", $Result, TRUE);
    return;
  }
  LogPf ("Save uploaded file done");
  #
  # Read post data
  #
  $Result = SaveFlashOptions ($gUploadDir, $OptFileName);
  DebugPf ("Result: $Result", __LINE__);
  if ($Result) {
    CallClientJsFunc ("UploadFileAndDataComplete", $Result, TRUE);
    return;
  }
  #
  # Gen a JSON string for client
  #
  $Result = '{"fn": "' . $RomFileName . '", ' .
             '"cs": "' . $CheckSum . '", ' . 
             '"pd": "' . $OptFileName . '", ' .
             '"ft": "' . $FileType . '", ' .
             '"resp": "Uploaded, ready to flash!"}'; 
  
  CallClientJsFunc ("UploadFileAndDataComplete", $Result, FALSE);
  LogPf ("Save post data done");
  
  ParseAndPrintHtmlText ($gFwFrameHtml);
}

sub FlashRemoteServerFw {
  my $ua = LWP::UserAgent->new;
  my ($RemoteAddr, $ClientId) = @_;
  my ($Filename, $FileType, $PostDataFile, $HostPort, $CheckSum);
  my $Reponse;
  my $Url;

  $gHttpQuery = new CGI;
  $Filename = $gHttpQuery->param("fn");
  $FileType = $gHttpQuery->param("ft");
  $PostDataFile = $gHttpQuery->param("pd");
  $HostPort = $gHttpQuery->param("hport");
  $CheckSum = $gHttpQuery->param("cs");
  
  LogPf ("Client ID: $ClientId");
  
  $Url = "http://$RemoteAddr/Actions/FwFlash.cgi?func=ffw" . 
    "&fn=$Filename&pd=$PostDataFile&hport=$HostPort&ft=$FileType&cs=$CheckSum";
  LogPf ($Url);
  $Reponse = $ua->get ($Url);
  DebugPf ("Reponse: " . $Reponse->content, __LINE__);

  if ($Reponse->is_success) {
#    CallClientJsFunc ("FlashRemoteServerFwComplete", $Reponse->content, FALSE);
    print $Reponse->content;
  } else {
#    CallClientJsFunc ("FlashRemoteServerFwComplete", "Request server to flash firmware failed", TRUE);
    PrintJsonTextMessage ("Request server to flash firmware failed", TRUE);
  }
}

sub UpdateRemoteServerScu {
  my $ua = LWP::UserAgent->new;
  my ($ServerFunc, $RemoteAddr) = @_;
  my ($Filename, $ExitFunNo, $HostPort);
  my $PostRebootParam;
  my $Reponse;
  my $Url;
  
  $gHttpQuery = new CGI;
  
  $Filename = $gHttpQuery->url_param("fn");
  $HostPort = $gHttpQuery->url_param("hport");
  $PostRebootParam = $gHttpQuery->param("xREBOOTx");
  
  if ($ServerFunc eq "urs") {
    $ExitFunNo = $gHttpQuery->url_param("ef");
    $Url = "http://$RemoteAddr/Actions/SubmitData.cgi?func=rsp&fn=$Filename&hport=$HostPort&ef=$ExitFunNo";
  } elsif ($ServerFunc eq "cst") {
    $Url = "http://$RemoteAddr/Actions/SubmitData.cgi?func=rtc&fn=$Filename&hport=$HostPort";
  } else {
    PrintJsonTextMessage ("Invalid parameters", TRUE);
    return;
  }
  LogPf ($Url);
  if ($PostRebootParam) {
    LogPf ("Reboot system");
    $Reponse = $ua->post ($Url, {'xREBOOTx' => $PostRebootParam});
  } else {
    LogPf ("Non-reboot system");
    $Reponse = $ua->get ($Url);
  }
  DebugPf ("Reponse: " . $Reponse->content, __LINE__);
  if ($Reponse->is_success) {
    print $Reponse->content;
  } else {
    PrintJsonTextMessage ("Request server to flash firmware failed", TRUE);
  }
}

sub MainProcess {
  my $UrlParamsRef = $_[0];
  my ($TargetIp, $TargetPort);
  my ($ServerFunc, $ClientId);
  
  $ServerFunc = $UrlParamsRef->{'func'};
  $ClientId = $UrlParamsRef->{'id'};
  $TargetIp = $UrlParamsRef->{'ip'};
  $TargetPort = $UrlParamsRef->{'port'};
  if (!$TargetPort) {
    $TargetPort = "80";
  }
  
  LogPf ("Func=$ServerFunc");
  #
  # Dispatch functions
  #
  if ($ServerFunc eq "utf") {
    #
    # Upload temporary file for next func to use
    #
    SaveTempUploadFileAndPostData ();
    #
    # To avoid content not initialize well, insert a script to do it
    # or it can't submit again.
    #
    InitIframe ($gFwIframeInitJsFunc);
  } elsif ($ServerFunc eq "ffw") {
    if (ValidateIdIpPort ($ClientId, $TargetIp, $TargetPort)) {
      CallClientJsFunc ($gInvalidOperationAlarm, "Invalide parameters", TRUE);
      return;
    }
    #
    # Flash remote server fw by using previous uploaded temporary file
    #
    FlashRemoteServerFw ("$TargetIp:$TargetPort", $ClientId);
  } elsif ($ServerFunc eq "scs") {
    #
    # Submit client posted settings
    #
    SaveSubmitSettings ($ClientId);
  } elsif ($ServerFunc eq "urs") {
    #
    # Update server scu settings
    #
    if (ValidateIpPort ($TargetIp, $TargetPort)) {
      CallClientJsFunc ($gInvalidOperationAlarm, "Invalide parameters", TRUE);
      return;
    }
    UpdateRemoteServerScu ($ServerFunc, "$TargetIp:$TargetPort");
  } elsif ($ServerFunc eq "utc") {
    #
    # Upload text configuration file
    #
    SaveTxtConfigFile ();
    InitIframe ($gUploadInitJsFunc);
  } elsif ($ServerFunc eq "cst") {
    #
    # Change remote server scu settings with text configuration file
    #
    if (ValidateIpPort ($TargetIp, $TargetPort)) {
      CallClientJsFunc ($gInvalidOperationAlarm, "Invalide parameters", TRUE);
      return;
    }
    UpdateRemoteServerScu ($ServerFunc, "$TargetIp:$TargetPort");
  } else {
    CallClientJsFunc ($gInvalidOperationAlarm, "Invalid parameters", TRUE);
  }
}

sub Main {
  my $ServerFunc;
  my %UrlParams;
  
  LogProcessStart ();
  
  %UrlParams = ReadUrlGetParams ();
  if (!%UrlParams) {
    CallClientJsFunc ($gInvalidOperationAlarm, "Invalid parameters", TRUE);
    return;
  }
  $ServerFunc = $UrlParams{'func'};
  
  #
  # Check function
  #
  if (!$ServerFunc) {
    CallClientJsFunc ($gInvalidOperationAlarm, "Invalid parameters", TRUE);
    return;
  }
  MainProcess (\%UrlParams);
  LogProcessEnd ();
}

#
# NOTE: Content-type must be text/html, javascript can work well
#
print "Content-type: text/html\n\n";

Main ();

