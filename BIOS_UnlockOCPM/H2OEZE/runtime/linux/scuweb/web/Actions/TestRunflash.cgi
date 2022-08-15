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

print "Content-type: text/html\n\n";

chdir "../../bin/FlashTool/";
#`./flashit_s.sh ../../web/UploadFiles/285k8fXYpR-bios.rom -all  -n 1>/dev/null 2>&1>/dev/null`;
#my $Result = `echo \$?`;
my $Result = system ("./flashit_s.sh ../../web/UploadFiles/285k8fXYpR-bios.rom -all  -n 1>/dev/null 2>&1>/dev/null");
#my $Data = `./flashit_s.sh ../../web/UploadFiles/285k8fXYpR-bios.rom -all  -n 1>/dev/null 2>&1>/dev/null`;
#print `echo ${?}`;
=head
my $Result = `echo $?`;
print "Result is: $Result<br />\n";
chomp ($Result);
print "Print again: $Result\n";
#print "System error $ERRNO";
=cut
print "Result is: $Result<br />\n";
chomp ($Result);
print "Print again: $Result\n";

