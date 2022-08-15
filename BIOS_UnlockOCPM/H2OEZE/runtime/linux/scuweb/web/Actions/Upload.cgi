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
use File::Basename; 

#----------
# Global settings
#----------
$CGI::POST_MAX = 1024 * 5000;  # 5MB (The maximun size of uploading file)

#----------
# Global static strings
#----------
my $gCgiLog                  = "../../logs/cgi.log";
my $gGenScuTxtBin            = "../../bin/GenScuTxt -i ";
my $gUpdateScuLog            = "../../logs/UpdateXml.log";
my $gGenScuXmlLog            = "../../logs/GenXml.log";
my $gGenScuXmlBin            = "../../bin/GenScuConfig -x ../BiosSetupInfo.xml -t ../Scu.txt";
my $gScuPropFile             = "ScuSettings.prop";
my $gSafeFilenameCharacters  = "a-zA-Z0-9_.-"; 
my $gUploadDir               = "../ScuFiles"; 

#----------
# Global variables
#----------
my $gHttpQuery               = new CGI; 


#----------
# Functions
#----------
sub LogBasicInfo {
  `echo "Upload text configuration starts..." 1>$gCgiLog`;
  `pwd 1>>$gCgiLog`;
  `whoami 1>>$gCgiLog`;
}

sub SaveUploadedFile {
  my $Fd = $_[0];
  my $ToSaveFile = $_[1];
  
  open (UPLOADFILE, ">$ToSaveFile") or die "$!"; 
  binmode UPLOADFILE; 

  while (<$Fd>) { 
    print UPLOADFILE; 
  } 

  close UPLOADFILE;
}

sub ExecUpdateProcess {
  my $ToSaveFile = $_[0];
  my $Result;
  
  #print "Updating settings and generating text file...";
  `echo "Updating settings and generating text file..." 1>>$gUpdateScuLog`;
  `$gGenScuTxtBin $ToSaveFile 1>>$gUpdateScuLog`;
  
  $Result = `echo $?`;
  if ($Result != "0") {
#    print "<" + "script " + "type=\"text/javascript\">window.parent.FileUploadComplete('Update process failed!', true);" + "<" + "/script" + ">";
    return 1;
  }
  
  return 0;
}

sub ExecGenFileProcess {
  my $Result;

  #print "Generating xml file...";
  `echo "Generating xml file..." 1>>$gUpdateScuLog`;
  `$gGenScuXmlBin 1>$gGenScuXmlLog`;

  $Result = `echo $?`;
  `echo "Process finished, status code is $Result" 1>>$gUpdateScuLog`;
  
  if ($Result == "0") {
    return 0;
#    print "<script type=\"text/javascript\">window.parent.FileUploadComplete('Update settings with text configuration is success!', false);</script>";
  } else {
    return 1;
#    print "<script type=\"text/javascript\">window.parent.FileUploadComplete('Generate xml failed', true);</script>";
  #  print "<br />Xml file generating failed!";
  }
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
  #my $ToSaveFile = "/var/local/insyde/scu_utility/web/ScuFiles/Scu.txt";
  my $ToSaveFile;
  my $Result;

  LogBasicInfo ();
  $Filename = $gHttpQuery->param("FileToUpload");
  if (!$Filename) {
    `echo "Error! Uploaded file name doesn't exist!" 1>>$gCgiLog`;
#    print "There was a problem uploading your file."; 
    print "<script type=\"text/javascript\">window.parent.FileUploadComplete('There was a problem uploading your file', true);</script>";
    CallClientJsFunc ();
    exit;
  }
  
  if ($gHttpQuery->param("FileUploadId")) {
    $ClientId = $gHttpQuery->param("FileUploadId");
  }
  
  `echo "Client ID: $ClientId" 1>>$gCgiLog`;
  `echo "Original filename: $Filename" 1>>$gCgiLog`;
  
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
#    print "<script type=\"text/javascript\">window.parent.FileUploadComplete('Filename contains invalid characters', true);</script>";
#    CallClientJsFunc ();
#    exit;
  }

  `echo "Final filename: $Filename" 1>>$gCgiLog`;
  
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
  # Property file exists means update process is running
  #
  if ( -e $gScuPropFile) {
    `echo "$gScuPropFile file exists, system is updating!"`;
#    print "System is updating! Please try again later...";
    print "<script type=\"text/javascript\">window.parent.FileUploadComplete('System is updating! Please try again later...', true);</script>";
    CallClientJsFunc ();
    exit;
  }
  
  #
  # Uploaded file as a input to generate property file for updating scu settings
  #
  $Result = ExecUpdateProcess ($ToSaveFile);
  if ($Result) {
    print "<script type=\"text/javascript\">window.parent.FileUploadComplete('Update process failed!', true);</script>";
    CallClientJsFunc ();
    exit;
  }
  #
  # Generate the new relative files for html
  #
  $Result = ExecGenFileProcess ();
  if ($Result == 0) {
    print "<script type=\"text/javascript\">window.parent.FileUploadComplete('Update settings with text configuration is success!', false);</script>";
  } else {
    print "<script type=\"text/javascript\">window.parent.FileUploadComplete('Generate xml failed', true);</script>";
  }
  #
  # Delete property file
  #
  if ( -e $gScuPropFile) {
    `rm -f $gScuPropFile`;
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



