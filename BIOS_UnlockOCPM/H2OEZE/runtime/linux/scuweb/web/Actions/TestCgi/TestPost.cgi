#!/usr/bin/perl -w


use strict;
use warnings;


use CGI qw(:standard);
use LWP::UserAgent;
use HTTP::Status ();
use File::Basename;
use IO::File;

use constant TRUE            => 1;
use constant FALSE           => 0;

use constant HTTP_POST_DATA  => 1;
use constant HTTP_GET_DATA   => 0;

my $DateToday                = `date +"%m-%d-%y"`;
chomp ($DateToday);
my $gOperationLog            = "../../logs/operation_$DateToday.log";

my $gPlatformInfoFile        = "../PlatformInfo.txt";
my $gSafeFilenameCharacters  = "a-zA-Z0-9_.-"; 
my $gUploadDir               = "../UploadFiles"; 
my $gTempPostDataFileName    = "PostData.txt";
my $gInvalidOperationAlarm   = "InvalidOperationAlarm";
my $gPlatformInfoStr;
my $gVersionStr;
my %HttpGetArg;


sub DebugPf {
  my $msg = $_[0];
  `echo "[DBG-ProxyFwScuProcess] $msg" 1>>$gOperationLog`;
}

sub LogPF {
  my $msg = $_[0];
  `echo "[ProxyFwScuProcess] $msg" 1>>$gOperationLog`;
}

sub CreateUploadedFile {
  my $Fd = $_[0];
  my $ToSaveFile = $_[1];
  
  open (UPLOADFILE, ">$ToSaveFile") or return FALSE; 
  binmode UPLOADFILE; 

  while (<$Fd>) { 
    print UPLOADFILE; 
  } 

  close UPLOADFILE;
  
  return TRUE;
}

sub SaveUploadFile {
  my $FileDir = $_[0];
  my $ClientId = $_[1];
  my $Filename = $HttpGetArg{'FileToUpload'};
  my ($name, $path, $extension);
  my $ToSaveFile;
  
  
  if (!$Filename) {
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
  } else { 
    return "Invalid filename";
  }
  
  #
  # Get client id or use the default filename
  #
  if ($ClientId) {
    $ToSaveFile = "$FileDir/$ClientId-$Filename";
  } else {
    $ToSaveFile = "$FileDir/$Filename";
  }
  DebugPf ($ToSaveFile);
  
  #
  # Save uploaded file transform from client
  #
  if (CreateUploadedFile ($HttpGetArg{'FileToUpload'}, $ToSaveFile)) {
    return "";
  } else {
    return "Create file failed";
  }
}

sub SavePostData {
  my $FileDir = $_[0];
  my $ClientId = $_[1];
  my $HttpData = "";
  
  read (STDIN, $HttpData, $ENV{'CONTENT_LENGTH'});
  DebugPf ($HttpData);
  if (!open(FILE, ">$FileDir/$ClientId-$gTempPostDataFileName")) {
    return FALSE;
  }
  
  print FILE $HttpData;

  close (FILE);
  
  return TRUE;
}

sub ReadUrlGetParams {
  my $HttpData = $ENV{'QUERY_STRING'};
  my @pairs;  
  my $pair;
  my %UrlParams;
  my ($name, $value);
  
  if (!$HttpData) {
    DebugPf ("errrrr");
    return "";
  }
  @pairs = split(/&/, $HttpData); 
  foreach $pair (@pairs)
  {
    ($name, $value) = split(/=/, $pair);
#    $value =~ tr/+/ /;
#    $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
    $UrlParams{$name} = $value;
  }
  
  return %UrlParams;
}


print "Content-type: text/html\n\n";
#my $HttpData;
#read (STDIN, $HttpData, $ENV{'CONTENT_LENGTH'});
#print $HttpData;

DebugPf ("---------11111111----------");

#%HttpGetArg = ReadUrlGetParams ();
#if (%HttpGetArg) {
#  print $HttpGetArg{'func'};
#}

#SaveUploadFile ("../UploadFiles", "aa12345");
SavePostData ("../UploadFiles", "aa12345");

print "success";
DebugPf ("---------xxxxxxxx----------");

