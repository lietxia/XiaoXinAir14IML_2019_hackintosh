#!/usr/bin/perl -w

use strict;
use warnings;
#
# Error would occur on RedHat, it maybe without full perl library
# 
use CGI qw(:standard);
use CGI::Carp;
use LWP::UserAgent;
use HTTP::Status ();
use File::Basename;
use IO::File;


use constant TRUE            => 1;
use constant FALSE           => 0;

#----------
# Global Constants
#----------
# Logs
my $DateToday                = `date +"%m-%d-%y"`;
chomp ($DateToday);
my $gCgiLog                  = "../../logs/cgi_$DateToday.log";

# Files and folders
my $gPlatformInfoFile        = "../PlatformInfo.txt";
my $gFwFrameHtml             = "../FwFrame.html";
my $gUploadDir               = "../UploadFiles"; 
my $gTempPostDataFileName    = "PostData.txt";
my $gTempFlashOptFile        = "FlashOptions.txt";
my $gPropertyFile            = "Settings.prop";

# Others
my $gSafeFilenameCharacters  = "a-zA-Z0-9_.-"; 

# Javascript function names
my $gInvalidOperationAlarm   = "InvalidOperationAlarm";
my $gUploadFileComplete      = "UploadFileComplete";
my $gFwIframeInitJsFunc      = "InitUploadFw";

#----------
# Global Variables
#----------
my $gHttpQuery               = new CGI; 
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
}

sub ReadUrlGetParams {
  my $HttpData = $ENV{'QUERY_STRING'};
  my @pairs = split(/&/, $HttpData);  
  my $pair;
  my %UrlParams;
  my ($name, $value);
  
  foreach $pair (@pairs)
  {
    ($name, $value) = split(/=/, $pair);
#    $value =~ tr/+/ /;
#    $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
    $UrlParams{$name} = $value;
  }
  
  return %UrlParams;
}

sub ReadAndPrintHtmlText {
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

sub ValidateIpAddress {
  my $IpAddr = $_[0];
  
  if (!$IpAddr) {
    return FALSE;
  }
  #
  # Check ip format
  #
  if ($IpAddr =~ /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/) {
    return FALSE;
  }
  
  return TRUE;
}

sub SaveUploadFile {
  my ($FileDir, $ClientId) = @_;
  my $Filename = $gHttpQuery->param("FileToUpload");
  my ($name, $path, $extension);
  my $ToSaveFile;
  
  LogPf ("Original filename: $Filename");
  
  if (!$Filename) {
    LogPf ("Error! Uploaded file name doesn't exist!");
    return "Can't get uploaded file";
  }
  
  #
  # Parse filename and make sure that filename is valid
  #
  ($name, $path, $extension) = fileparse ($Filename, '\..*'); 
  $Filename = $name . $extension; 
  $Filename =~ tr/ /_/; 
  $Filename =~ s/[^$gSafeFilenameCharacters]//g;

  if ($Filename =~ /^([$gSafeFilenameCharacters]+)$/) {
#    $Filename = $1; 
  } else { 
    LogPf ("Invalid filename: $Filename");
    return "Invalid filename";
  }

#  LogPf ("Final filename: $Filename");
  
  #
  # Get client id or use the default filename
  #
  if ($ClientId) {
    $ToSaveFile = "$FileDir/$ClientId-$Filename";
  } else {
    $ToSaveFile = "$FileDir/$Filename";
  }
  LogPf ("Final filename: $ToSaveFile");
  
  #
  # Save uploaded file transform from client
  #
  if (CreateUploadedFile ($gHttpQuery->upload("FileToUpload"), $ToSaveFile)) {
    return "";
  } else {
    return "Create file failed";
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

    # record the timeout
    if ($response->code == HTTP::Status::HTTP_REQUEST_TIMEOUT) {
      LogPf ("Status Code: $response->code; $response->message");
    }
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
    if ($Reponse->code == HTTP::Status::HTTP_REQUEST_TIMEOUT) {
      LogPf ("Status Code: $Reponse->code; $Reponse->message");
    }
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
  my ($FileDir, $ClientId) = @_;
  my $Filename = $gHttpQuery->param("FileToUpload");
  my ($name, $path, $extension);
  my $ToSaveFile;
  
  LogPf ("Original filename: $Filename");
  
  if (!$Filename) {
    LogPf ("Error! Uploaded file name doesn't exist!");
#    print "<script type=\"text/javascript\">window.parent.FileUploadComplete('There was a problem uploading your file', true);</script>";
#    CallClientJsFunc ("There was a problem uploading your file", TRUE);
#    exit;
    return "Can't get uploaded file";
  }
  
  #
  # Parse filename and make sure that filename is valid
  #
  ($name, $path, $extension) = fileparse ($Filename, '\..*'); 
  $Filename = $name . $extension; 
  $Filename =~ tr/ /_/; 
  $Filename =~ s/[^$gSafeFilenameCharacters]//g;

  if ($Filename =~ /^([$gSafeFilenameCharacters]+)$/) {
#    $Filename = $1; 
  } else { 
#    die "Filename contains invalid characters"; 
#    die LogPf ("Client ID: $ClientId");
    LogPf ("Invalid filename: $Filename");
    return "Invalid filename";
#    print "Filename contains invalid characters"; 
#    print "<script type=\"text/javascript\">window.parent.FileUploadComplete('Filename contains invalid characters', true);</script>";
#    CallClientJsFunc ();
#    exit;
  }

#  LogPf ("Final filename: $Filename");
  
  #
  # Get client id or use the default filename
  #
  if ($ClientId) {
    $ToSaveFile = "$FileDir/$ClientId-$Filename";
  } else {
    $ToSaveFile = "$FileDir/$Filename";
  }
  LogPf ("Final filename: $ToSaveFile");
  
  #
  # Save uploaded file transform from client
  #
  if (CreateUploadedFile ($gHttpQuery->upload("FileToUpload"), $ToSaveFile)) {
    return "";
  } else {
    return "Create file failed";
  }
}

#
# Don't use this function, an error occurs
#
sub SavePostData {
  my ($FileDir, $ClientId) = @_;
  my $HttpData = "";

  #
  # Can't use read (STDIN, $HttpData, $ENV{'CONTENT_LENGTH'});
  # Error would occur
  # Must use $gHttpQuery->param("param_name") to get data separatly
  #  
  DebugPf ("Save post data...", __LINE__);
  read (STDIN, $HttpData, $ENV{'CONTENT_LENGTH'});
  DebugPf ("HttpData: $HttpData", __LINE__);
  if (!open(FILE, ">$FileDir/$ClientId-$gTempPostDataFileName")) {
    #
    # the '\n' at the end of line means do not show the error line number and source code file name
    #
#    die "Can't not open logfile: $!\n";
    LogPf ("Can't open $FileDir/$gTempPostDataFileName");
    return FALSE;
  }
  
  print FILE $HttpData;

  close (FILE);
  
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
  my ($FileDir, $ClientId) = @_;
  my $FileName;
  my @CheckBoxOpt;
  my @FlashOpt;
  my $FlashAll;
  my $HasParam = FALSE;
  
  $FileName = "$FileDir/$ClientId-$gTempFlashOptFile";
  LogPf ("Flash options file: $FileName");
  if (!open(FILE, ">$FileName")) {
    #
    # the '\n' at the end of line means do not show the error line number and source code file name
    #
#    die "Can't not open logfile: $!\n";
    LogPf ("Can't open $FileName");
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

sub SaveSubmitSettingsEx () {
  my $ClientId = $gHttpQuery->param("FileUploadId");
  my $Result;
  
  LogPf ("Client ID: $ClientId");
  #
  # Read post data
  #
  $Result = SavePostData ($gUploadDir, $ClientId);
  if ($Result) {
    CallClientJsFunc ("UploadClientSettingsComplete", $Result, TRUE);
  }
  LogPf ("Result: $Result");
  
  CallClientJsFunc ("UploadClientSettingsComplete", "Ready to notify remote server", FALSE);
}

sub SaveTxtConfigFile () {
  my $ClientId = $gHttpQuery->param("FileUploadId");
  my $Result;
  
  LogPf ("Client ID: $ClientId");
  #
  # Save upload file
  #
  $Result = SaveUploadFile ($gUploadDir, $ClientId);
  if ($Result) {
    CallClientJsFunc ("UploadTxtConfigComplete", $Result, TRUE);
    return;
  }
  
  CallClientJsFunc ("UploadTxtConfigComplete", "Ready to notify remote server", FALSE);
}

sub ChangeRemoteServerScu {
  my $RemoteAddr = $_[0];
}

sub ChangeRemoteServerScuWithTxtConfig {
  my $RemoteAddr = $_[0];
}

sub UpdateSettingsProcess {
  my $UrlParamsRef = $_[0];
  my ($TargetIp, $TargetPort);
  my ($RemoteAddr, $SettingsType, $RemoteFile);
  
  $TargetIp = $UrlParamsRef->{'ip'};
  $TargetPort = $UrlParamsRef->{'port'};
  $RemoteAddr = $UrlParamsRef->{'radr'};
  $SettingsType = $UrlParamsRef->{'st'};
  $RemoteFile = $UrlParamsRef->{'rf'};
  
  if (!ValidateIpAddress ($RemoteId)) {
    LogPf ("Address format is not correct");
    CallClientJsFunc ($gInvalidOperationAlarm, "Address format is not correct", TRUE);
    return;
  }
  if ($SettingsType eq "sd") {
    #
    # Use submit data to update
    #
    ChangeRemoteServerScu ("$TargetIp:$TargetPort", $RemoteAddr, $RemoteFile);
  } elsif ($SettingsType eq "tc") {
    #
    # Use text configuration file to update
    #
    ChangeRemoteServerScuWithTxtConfig ("$TargetIp:$TargetPort", $RemoteAddr, $RemoteFile);
  } else {
    CallClientJsFunc ($gInvalidOperationAlarm, "Invalid parameter", TRUE);
  }
}

sub SaveSubmitSettings {
  my $UrlParamsRef = $_[0];
  my $ClientId;
  my $PostData;
  my @PostDataArray;
  my $Pair;
  my ($Key, $Val);
  my $FileName;

  $ClientId = $UrlParamsRef->{'cid'};
  if (!$ClientId) {
    CallClientJsFunc ($gInvalidOperationAlarm, "Invalid parameter", TRUE);
    return;
  }

  read (STDIN, $PostData, $ENV{'CONTENT_LENGTH'});
  $FileName = $ClientId . 
  if (!open (DLFILE, ">$gUploadDir/$FileName-$gPropertyFile")) {
    CallClientJsFunc ($gInvalidOperationAlarm, "Save submit settings failed", TRUE);
    return;
  } 

  @PostDataArray = split (/&/, $PostData);
  foreach $Pair (@PostDataArray) {
    print DLFILE $Pair;
  }

  close DLFILE;
  
  CallClientJsFunc ($gUploadFileComplete, "Save submit settings failed", TRUE);
}

sub MainProcess {
  my $UrlParamsRef = $_[0];
  my ($ServerFunc, $SettingsType);
  
  $ServerFunc = $UrlParamsRef->{'func'};
  LogPf ("Func=$ServerFunc");
  #
  # Dispatch functions
  #
  if ($ServerFunc eq "scs") {
    #
    # Submit client post data
    #
    SaveSubmitSettings ($UrlParamsRef);
  } elsif ($ServerFunc eq "utc") {
    #
    # Upload text configuration file
    #
    SaveTxtConfigFile ();
  } elsif (($ServerFunc eq "css") || ($ServerFunc eq "cst")) {
    #
    # Change target server scu settings
    #
    UpdateSettingsProcess ($UrlParamsRef);
  } else {
    CallClientJsFunc ($gInvalidOperationAlarm, "Do nothing", TRUE);
  }
}

sub Main {
  my ($ServerFunc, $SettingType);
  my %UrlParams;
  
  LogProcessStart ();
  
  %UrlParams = ReadUrlGetParams ();
  $ServerFunc = $UrlParams{'func'};
  $SettingType = $UrlParams{'st'};
  
  #
  # Check function
  #
  if (!$ServerFunc || !$SettingType) {
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

