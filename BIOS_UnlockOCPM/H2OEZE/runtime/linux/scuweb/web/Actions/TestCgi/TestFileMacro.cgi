#!/usr/bin/perl -w

sub DebugPf {
  my $msg = $_[0];
  my @LocalFileNameArray = split (/\//, __FILE__);
  my $DebugTitle = $LocalFileNameArray[$#LocalFileNameArray] . "-" . __LINE__;
  
  print "[DBG-$DebugTitle] $msg\n";
}

sub LogPf {
  my $msg = $_[0];
  my @LocalFileNameArray = split (/\//, __FILE__);
  my $DebugTitle = $LocalFileNameArray[$#LocalFileNameArray];
  
  print "[$DebugTitle] $msg\n";
}

print "FILE: ". __FILE__. " Line: ". __LINE__. "\n";

DebugPf ("Test DebugPf");
LogPf ("Test LogPf");
