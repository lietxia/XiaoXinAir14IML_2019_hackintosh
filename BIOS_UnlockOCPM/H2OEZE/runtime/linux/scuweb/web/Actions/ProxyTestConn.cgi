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
#
# Error would occur on RedHat, it maybe without full perl library
# 
use CGI qw(:standard);
use LWP::UserAgent;
#use HTTP::Status ();
#use HTTP::Status;


use constant TRUE            => 1;
use constant FALSE           => 0;

my $gHttpQuery               = new CGI; 

my $DateToday                = `date +"%m-%d-%y"`;
chomp ($DateToday);
my $gCgiLog                  = "../../logs/cgi_$DateToday.log";
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

sub GenErrorMsgStr {
  if ($#_ == 0) {
    return "{\"StatusCode\": \"500\", \"Response\": \"".$_[0]."\"}";
  } else {
    return "{\"StatusCode\": \"".$_[0]."\", \"Response\": \"".$_[1]."\"}";
  }
}

sub TestRemoteConn {
  my $ua = LWP::UserAgent->new;
  my $response;
  
  $ua->timeout($_[1]);
  $response = $ua->get("http://".$_[0]."/Actions/TestConn.cgi");

  if (!$response->is_error) {
#    return $response->decoded_content;
    LogPf ($response->content);
    return $response->content;
  } else {
#    printf "Status Code: %d; %s", $response->code, $response->message;

    # record the timeout
#    if ($response->code == HTTP::Status::HTTP_REQUEST_TIMEOUT) {
#      LogPf ("Status Code: $response->code; $response->message");
#    }
    return GenErrorMsgStr ($response->code, $response->message);
  }
}

sub Main {
  my $RemoteIp = $gHttpQuery->param("ip");
  my $RemotePort = $gHttpQuery->param("port");
  my $ServerFunc = $gHttpQuery->param("func");
  my $WhatTimeIsIt = `date +"%H:%M:%S"`;
  
  chomp ($WhatTimeIsIt);
  LogPf ("--- start at $WhatTimeIsIt ---");
  if (!$RemoteIp || !$ServerFunc) {
    LogPf ("Invalid parameters");
    return GenErrorMsgStr ("Invalid parameters");
  }
  
  if (!($RemoteIp =~ /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/)) {
    LogPf ("Address format is not correct");
    print GenErrorMsgStr ("Address format is not correct");
  }
  if ($ServerFunc eq "conn") {
    LogPf ("Address is $RemoteIp:$RemotePort, timeout is 2000");
    print TestRemoteConn ($RemoteIp.":".$RemotePort, 2000);
  }
  LogPf ("--- end ---");
}

#
# Content-type is application/json and ajax datatype is json, 
# when request server without this feature would return parseerror
# Content-type is text/html and ajax datatype is default(text/html),
# ajax need try-catch for $.parseJSON or it may cause error and 
# html layout frizon.
#
print "Content-type: application/json\n\n";
#print header('application/json');

Main ();

