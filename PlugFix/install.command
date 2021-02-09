#!/bin/bash
cd $(dirname $BASH_SOURCE) || {
    echo Error getting script directory >&2
    exit 1
}

sudo chmod 755 ALCPlugFix
sudo chmod 755 hda-verb
sudo chmod 644 good.win.ALCPlugFix.plist

sudo cp -f ALCPlugFix /usr/local/bin
sudo cp -f hda-verb /usr/local/bin
sudo cp -f good.win.ALCPlugFix.plist /Library/LaunchAgents
sudo chown root:wheel /usr/local/bin/ALCPlugFix
sudo chown root:wheel /usr/local/bin/hda-verb
sudo chown root:wheel /Library/LaunchAgents/good.win.ALCPlugFix.plist
sudo launchctl load -w /Library/LaunchAgents/good.win.ALCPlugFix.plist
exit 0