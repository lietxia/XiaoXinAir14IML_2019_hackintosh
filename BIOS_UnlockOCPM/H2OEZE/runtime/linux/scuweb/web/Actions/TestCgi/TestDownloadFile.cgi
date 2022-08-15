#!/usr/bin/perl -w

#
# Error would occur on RedHat, it maybe without full perl library
# 
use CGI qw(:standard);
use LWP::UserAgent;
use HTTP::Request;

use constant TRUE            => 1;
use constant FALSE           => 0;

my $gPlatformInfoFile        = "../PlatformInfo.txt";
my $gOperationLog            = "../../logs/operation.log";
my $gPlatformInfoStr         = "";
my $gHttpQuery               = new CGI;

sub CreateUploadedFile {
  my $FileData = $_[0];
  my $ToSaveFile = $_[1];
  
#  open (UPLOADFILE, ">$ToSaveFile") or die "$!"; 
  open (UPLOADFILE, ">$ToSaveFile") or return FALSE; 
  binmode UPLOADFILE; 

  print UPLOADFILE $FileData; 

  close UPLOADFILE;
  
  return TRUE;
}

sub DownloadFile {
#  $FilePath = "http://172.18.4.51:8089/UploadFiles/ByP2cWfglP-FlashOptions.txt";
  $FilePath = "http://172.18.4.51:8089/UploadFiles/ByP2cWfglP-Bios.rom";

  my $agent = LWP::UserAgent->new(env_proxy => 1,keep_alive => 1, timeout => 30);
#  my $header = HTTP::Request->new(GET => $FilePath);
#  my $request = HTTP::Request->new('GET', $FilePath, $header);
#  my $response = $agent->request($request); 
  my $response = $agent->get($FilePath); 
  
  if ($response->is_success) {
#    print $response->content;
    CreateUploadedFile ($response->content, "../UploadFiles/bios.rom");
  }
}

print "Content-type: text/html\n\n";

DownloadFile ();

print "Done";
