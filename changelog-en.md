* 2021-11-09 23:00
    * Support for macOS Monterey 12.1
    * Opencore updated to 0.7.6

* 2021-08-04 17:53
    * Support for macOS Monterey 12.0.1 
    * Opencore updated to 0.7.5
    * Clover updated to v5141 

* 2021-08-09 22:20
    * Add USB mouse support
    * Show pointer
    * Delete CPUFriend, itlwm and USBPorts
    * Change IntelBluetoothFirmware MaxKernel to 21.99.99
    * Add DebugEnhancer.
    * Enable Verbstub
    * Update itlwm driver

* 2021-08-07 07:44
    * Fix `Ctrl`+`Enter` can't set the default system

* 2021-08-04 17:53
    * Support for macOS 12 Monterey Beta. Bluetooth✅（Known Issues:Keyboard malfunction after shutdown or reboot.）
    * Opencore updated to 0.7.2
    * Clover updated to v5138
 
* 2021-06-11 20:42
    * Support for macOS 12 Monterey Beta (dw1820a Wi-Fi ✅. dw1820a Bluetooth ⛔. Intel Wi-Fi ✅. Intel Bluetooth ⛔. Sleep and wake up ✅. Touchpad ✅. HDMI✅. Camera✅) 
    
* 2021-06-10 08:20
    * Opencore updated to 0.7.0
    * Support for macOS 12 Monterey Beta (dw1820a Wi-Fi ✅. dw1820a Bluetooth ⛔. Intel Wi-Fi ⛔. Intel Bluetooth ⛔. Sleep and wake up ✅. Touchpad normal ✅) 
    * Updated some kext

* 2021-04-14 11:13
    * 🆕 Opencore updated to 0.6.8 
    * 🆕 Clover updated to r5133
    * 🆕 Updated some kext (not important)

* 2021-02-18 11:25
    * OpenCore added GUI, It is now possible to boot Windows
    * Clover updated to r5130, no longer need `DataHubDex.efi`
    * Re-modified `SSDT-BATX-Air14IML.aml` to show battery remaining available time
    * Re-add `SSDT-UIAC.aml` (it may affect sleep?)
    * YogaSMC updated to 1.4.3, Synchronized update of `SSDT-ECRW.aml` .

* 2021-02-11 14:22
    * Remove clover intel Wifi configuration
    * Change back to use `WhatEverGreen` to disable mx250 `disable-external-gpu`

* 2021-02-10 01:03
    * Add `SSDT-NDGP_OFF-Air14IML.aml` to block the Nvdia graphics card
    * Touchpad `SSDT-TPAD-Air14IML.aml` changed to GPIO mode, pin=`50`
    * Fixed `SSDT-BATX-Air14IML.aml` to show battery remaining available time
    * Update `voodooi2c` to version 2.6.4
    * Remove `SSDT-XSPI.aml`, `SSDT-UIAC.aml`, `SMCSuperIO.kext`, `NoTouchID.kext` which are no longer needed
    * Fix the problem that Clover can't boot BigSur (need to choose Preboot to boot bigSur)
    * Minor changes to `install.command` and `uninstall.command` scripts of `ALCPlugFix`.

* 2021-02-05 08:20
    * Reduce itlwm size, no changes for DW1820A.
 
* 2021-02-03 22:23
    * Update OpenCore to 0.6.6-MOD (ssdts only apply on macOS), update Clover to 5129.
    * Combine opencore branches. Default config can both used on DW1820A and intelAC9560, you can use a specialized version as well, for example, change`config-dw1920.plist` into `config.plist`.
    * Update lilu,appleALC,WEG,vSMC,voodooPS2,brcm kexts.
    * Modify or rename to OpenCore's offical DSDT.
        * `SSDT-EC` + `SSDT-USBX` => `SSDT-EC-USBX` 
        * `SSDT-SUBS` + `SSDT-MCHC` => `SSDT-SBUS-MCHC`
        * `SSDT-PNLF-CFL` => `SSDT-PNLFCFL`
        * `SSDT-PMCR` => `SSDT-PMC`
        * `SSDT-RTC_Y-AWAC_N` => `SSDT-AWAC`
    * Change `SSDT-RMCF` into `not switching key position`(it would change option and cmd before), and add system judgment, it won't load on systems except macOS, and change name into `SSDT-RMCF-Air14IML.aml`.
    * Add`RestrictEvents.kext`,it can block some add-ins that may cause error.
    * Optional `YogaSMC`, Because there are some small problems on my computer, it is not enabled by default. If you want to load, please load`YogaSMC.kext` `YogaSMCAlter.kext` `SSDT-RCSM` `SSDT-ECRW` together.

* 2021-01-21 11:30
    * Update Opencore branch, add YogaSMC, itlwm updated to 1.3.0_alpha, update VoodooI2C.

* 2021-01-16 22:06
    * Update Clover to Clover v5.1 r5128.

* 2021-01-06 18:30
    * Compact AirportItlwm, Big Sur and Catalina are 5MB in total.(But AC9560 only)
    * It may speed up the startup of AC 9560.
    * AIO version is suitable for Broadcom and Intel network card.

* 2021-01-06 16:00
    * Update kexts, update opencore to 0.6.5.
    * New version of whatEverGreen.kext needs to add boot-arg`-igfxblr`to run normally.
    * New`SSDT-BATS-Air14IML.aml`can display more battery info.

* 2021-1-2 16:17
    * Integrate Intel network card and Broadcom network card driver, repair itlwm no log in Big Sur.

* 2020-12-27 23:00
    * Update voodooI2C.kext, voodooI2CHID.text

* 2020-12-26 10:00
    * Update OpenCore to 0.6.4
    * Update Kexts.
    * New version of VoodooPS2 cancels the exchange of option and command keys, so add`SSDT-RMCF.aml`to enable the exchange of option and command keys.

* 2020-11-13 20:05
    * Temporarily abandon the clover branch update. OC branch can be used for 10.15.X (recommended 10.15.7) and Big Sur 11.0.1 at the same time.
    * Update to OpenCore 0.6.3, update kexts.
    * This EFI is for DW1820a. If it's AC9560, it can't be driven by this EFI. It needs to be changed. I'll find someone to change it.

> win1010525 have made an AIO version to drive AC9560.  
> Clover branch have re-updated since 2021-01-16.

* 2020-08-07 10:15
    * Update OpenCore to 0.6.0, Clover to r512.
    * Because of AppleALC’s update, delete FakePCIID_Intel_HDMI_Audio.kext and FakePCIID.kext
    * Change SMBIOS to MacBook Pro 13 2020.
    * Update kexts.

* 2020-06-13 16:38 
    * Update Opencore to 0.5.9. Update Clover to v5.0 r5119. Update kexts.

* 2020-05-06 21:36 
    * Combine SSDT-EC.aml, SSDT-RTC0.aml, SSDT-USBX.aml, SSDT-ALS0.aml, SSDT-MCHC.aml into SSDT-OCPublic-Merge.aml
    * Update kexts, Opencore and clover, change SMBIOS model into MacBook Air 2020, delete CPUFriend.kext and CPUFriendDataProvider.kext

* 2020-04-11 08:39 
    * Fix the bug of unable to mute, update kexts.
    * Update Clover to 5019. Update kexts.
    * No significant changes. You can ignore this update.

* 2020-03-26 11:05 
    * Update trackpad driver, more sensitive multi finger touch, update kexts.
    * Change OC into Mod version, it includes a GUI picker, update Clover.

* 2020-03-10 14:00 
    * Fix FN+F11 FN+F12 brightness adjustment, update kext.

* 2020-02-21 21:00 
    * Small update. If you can't boot into the system, enter with your original EFI. After entering, open the Terminal and enter `sudo nvram -c`. After clearing NVRAM, this EFI can enter.

* 2020-02-21 00:00 
    * Update kexts.

* 2020-02-24 14:00 
    * Most of the functions are normal, add the OpenCore version.
