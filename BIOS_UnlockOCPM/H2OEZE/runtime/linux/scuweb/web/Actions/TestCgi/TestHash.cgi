#!/usr/bin/perl -w
use strict; 
#use CGI; 
#use CGI::Carp qw (fatalsToBrowser); 
use CGI qw( :standard );
use Switch;
use File::Basename; 
use LWP::UserAgent;
use HTTP::Request;

use constant TRUE            => 1;
use constant FALSE           => 0;


sub ReadHashData {
  my ($FlashOptHash, $ParamName) = @_;
  my $Value = $FlashOptHash->{$ParamName};
  
  if ($FlashOptHash->{$ParamName}) {
    return $FlashOptHash->{$ParamName};
  }
  
  return "";
}

sub PrintHash {
  my $TestHash = $_[0];
#  my %TestHash = \$TestHashPtr;
  
  print ReadHashData ($TestHash, "q1") . "\n";
  print ReadHashData ($TestHash, "q2") . "\n";
  print ReadHashData ($TestHash, "q3") . "\n";
  print ReadHashData ($TestHash, "q4") . "\n";
  print ReadHashData ($TestHash, "q5") . "\n";
  print "[PrintHash] Initialized hash: " . $TestHash . "\n";
}

sub CreatHash1 {
  #
  # Do NOT initialize hash with undef, but (). () is an empty hash.
  #
  my %TestHash = (); 

  $TestHash{"q1"} = "test1";
  $TestHash{"q2"} = "test2";
  $TestHash{"q3"} = "test3";
  $TestHash{"q4"} = "test4";
  
  print "Initialized hash: " . %TestHash . "\n";
  
  return %TestHash;
}

sub CreatHash {
  #
  # Do NOT initialize hash with undef, but (). () is an empty hash.
  #
  my $TestHash = {}; 

  $TestHash->{"q1"} = "test1";
  $TestHash->{"q2"} = "test2";
  $TestHash->{"q3"} = "test3";
  $TestHash->{"q4"} = "test4";
  
  print "[CreatHash] Initialized hash: " . $TestHash . "\n";
  
  return $TestHash;
}

sub Main1 {
  my %GHash = ();

  %GHash = CreatHash ();
  print "Initialized hash: " . %GHash . "\n";
  PrintHash (\%GHash);
}

sub Main {
  my $GHash;

  $GHash = CreatHash ();
  print "[Main] Initialized hash: " . $GHash . "\n";
  PrintHash ($GHash);
}

Main ();

