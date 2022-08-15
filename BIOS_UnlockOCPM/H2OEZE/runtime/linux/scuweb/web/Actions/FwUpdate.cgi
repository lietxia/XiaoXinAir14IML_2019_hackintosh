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

use CGI; 
use CGI qw( :standard );
use File::Basename; 
use IO::File;

#----------
# Global settings
#----------
$CGI::POST_MAX = 1024 * 5000;  # 5MB (The maximun size of uploading file)

#----------
# Global static strings
#----------
my $DateToday = `date +"%m-%d-%y"`;
chomp ($DateToday);
my $gCgiLog                  = "../../logs/cgi_$DateToday.log";
my $gFlashBin                = "../../bin/flashit.sh -i ";
my $gFlashLog                = "../../logs/Flash.log";
my $gSafeFilenameCharacters  = "a-zA-Z0-9_.-"; 
my $gUploadDir               = "../UploadFiles"; 

#----------
# Global variables
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

#----------
# Functions
#----------
sub LogBasicInfo {
  LogPf ("Upload firmware file start...");
  `pwd 1>>$gCgiLog`;
  `whoami 1>>$gCgiLog`;
}

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

  return $HttpData;
}

sub SaveFlashFile {
  my $Fd = $_[0];
  my $ToSaveFile = $_[1];
  
  open (FLASHFILE, ">$ToSaveFile") or die "$!"; 
  binmode FLASHFILE; 

  while (<$Fd>) { 
    print FLASHFILE; 
  } 

  close FLASHFILE;
}

sub ExecFlashProcess {
  my $FileType = $_[0];
  my $ToSaveFile = $_[1];
  my $Result;
  
  #print "Updating settings and generating text file...";
  LogPf ("Flashing $FileType file...");
  `$gGenScuTxtBin $ToSaveFile 1>>$gUpdateScuLog`;
  
  $Result = ($? >> 8);
  if ($Result != "0") {
    return 1;
  }
  
  return 0;
}

sub ParseOptions {
#  $gHttpQuery
}

sub CallClientJsFunc {

#print <<END_HTML;
#  <form id="FileUploadForm" action="Actions/Upload.cgi" method="post" enctype="multipart/form-data" style="background-color: #dcdcdc;">
#    <input id="FileToUpload" type="file" size="30" name="FileToUpload" />
#    <button id="FileUploadBtn">Upload</button>
#  </form>
#END_HTML
}

#---
# Main process
#---
sub Main {
  my $Filename;
  my $ClientId = "";
  my ($name, $path, $extension);
  my $ToSaveFile;
  my $Result;

  LogBasicInfo ();
  ParseOptions ();
  #
  # Save file
  #
  $Filename = $gHttpQuery->param("FileToUpload");
  if (!$Filename) { 
    LogPf ("Error! File name doesn't exist!");
    print "<script type=\"text/javascript\">window.parent.FileFlashComplete('There was a problem uploading your file', true);</script>";
    CallClientJsFunc ();
    exit; 
  }
  
  if ($gHttpQuery->param("FileUploadId")) {
    $ClientId = $gHttpQuery->param("FileUploadId");
  }
  
  LogPf ("Client ID: $ClientId");
  LogPf ("Original filename: $Filename");
  
  #
  # Parse filename and make sure that filename is valid
  #
  ($name, $path, $extension) = fileparse ( $Filename, '\..*' ); 
  $Filename = $name . $extension; 
  $Filename =~ tr/ /_/; 
  $Filename =~ s/[^$gSafeFilenameCharacters]//g;

  if ($Filename =~ /^([$gSafeFilenameCharacters]+)$/) { 
    $Filename = $1; 
  } else { 
    die "Filename contains invalid characters"; 
#    print "Filename contains invalid characters"; 
#    print "<script type=\"text/javascript\">window.parent.FileFlashComplete('Filename contains invalid characters', true);</script>";
#    CallClientJsFunc ();
#    exit;
  }

  LogPf ("Final filename: $Filename");
  
  #
  # Get client id or use the default filename
  #
  if ($ClientId && ($ClientId != "")) {
    $ToSaveFile = "$gUploadDir/$ClientId-$Filename";
  } else {
    $ToSaveFile = "$gUploadDir/$Filename";
  }
  
  #
  # Save uploaded file transform from client
  #
  SaveUploadedFile ($gHttpQuery->upload("FileToUpload"), $ToSaveFile);
    
  #
  # Uploaded file as a input to generate property file for updating scu settings
  #
#  $Result = ExecFlashProcess ($ToSaveFile);
  if ($Result) {
    print "<script type=\"text/javascript\">window.parent.FileFlashComplete('Update process failed!', true);</script>";
    CallClientJsFunc ();
    exit;
  }
  #
  # Print the upload form html 
  #
  CallClientJsFunc ();
  
  exit;
}

#################################
# Process start here....
#################################

#
# This statement is necessary to be display on browser
#
#print "Content-type: text/html\n\n";
print $gHttpQuery->header (); 
Main ();



