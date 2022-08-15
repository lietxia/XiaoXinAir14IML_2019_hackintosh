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

#my $FileGenTime = `stat -c %Z ../BiosSetupInfo.xml`;
my $FileGenTime = `stat -c %Z ../setup.html`;
chomp ($FileGenTime);
print $FileGenTime;
