# Lenovo XiaoXin Air-14 2019IML
![air14iml-sur](img/air14iml-mon.jpg)
Screenshot app:/capXDR 
Model：Lenovo-Air14IML (made by lietxia)  
QQ group number：1032311345

[中文](./README.md)  
ENGLISH  

|      Info        |  Status  |                    Details                     |
| :--------------: | :------: | :--------------------------------------------: |
| Computer model💻 |   ✅    |         Lenovo XiaoXin Air14 IML 2019          |
|     System🌌     |   ✅    |         Catalina/Big Sur/Monterey/Ventura      |
|      CPU🎛️       |   ✅    |        Intel Core i5-10210U / i7-10510U        |
|  Motherboard🎛️   |   ✅    |               Lenovo LNVNB161216               |
|  Fingerprint🖐️   |   ⛔    |         Fingerprint is unable to work          |
|      GPU👾       |   ⛔    |         Nvidia GeForce MX250 ( 2 GB )          |
|      IGPU👾      |   ✅    |                 Intel UHD 620                  |
|     Memory💳     |   ✅    | Internal 4GB 2666 + Changeable 8GB 2666 memory |
|     Disks💽      |   ✅    |              See Benchmarks/Disks              |
|     Screen🖥️     |   ✅    |    AUO353D/LGD05EC ( 14-inches ) 1920x1080     |
|   Audio Card🔊   |   ✅    |                Conexant CX8070                 |
|    Wireless🌐    |   ✅    |  Intel Wireless-AC 9560 / Dell Wireless 1820A  |
|   Bluetooth🦷    |   ✅    |   DW1820A works, AC9560 is not that perfect    |
| SD card reader🗂️ |   ✅    |  O2 Micro SD card reader (probably different)  |
|    TrackPad🖐️    |   ✅    |         Works in GPIO mode with Pin=50         |
|      HDMI📺      |   ✅    |    able to output 4k@30fps, same as windows    |
|     Camera🎦     |   ✅    |      it's pretty easy to drive USB camera      |
|     Sleep😴      |   ✅    |             Support native sleep.              |
```
A way to solve keyboard broken when reboot from macOS Monterey:
Press F2 to enter BIOS -> BOOT
boot mode = leguacy support
boot priority = Leguacy First
```
## Current Status：
* System🌌：Catalina 10.15.7 / Big Sur 11.6 / Monterey 12.5 / Ventura 13.0 ( Not recommended to use Monterey / Ventura )
* Disks🖴：If you are using Samsung PM981A, please consider to change.
* Audio Card🔊：Success with layout-id 15, no plosive [Headsets_with_Microphone](https://github.com/lietxia/XiaoXinAir14IML_2019_hackintosh/releases/tag/0.0.1)

## Related model
* [XiaoXin Pro13 (i5-10210U / i7-10710U)](https://github.com/daliansky/XiaoXinPro-13-hackintosh)
* [XiaoXin13 IML](https://github.com/sun19970908/XiaoXin13IML_2020_hackintosh)
* [XiaoXin Air13 IWL (i5-8265U / i7-8565U)](https://github.com/daliansky/Lenovo-Air13-IWL-Hackintosh)
* [XiaoXin Air15 IKBR (i5-8265U)](https://github.com/czy1024/XiaoXin-Air15-IKBR-2018-EFI)
* [XiaoXin Air14 (i5-1035G1)](http://bbs.pcbeta.com/viewthread-1873103-1-1.html)
* [XiaoXin Air14 (i7-1065G7)](http://bbs.pcbeta.com/viewthread-1878378-1-1.html)
* [XiaoXin Air15 (i5-1035G1)](http://bbs.pcbeta.com/viewthread-1874022-1-1.html)
* [XiaoXin Air15 (i5-10210U)](http://bbs.pcbeta.com/viewthread-1859586-1-1.html)
* [Lenovo-Ideapad-S540-15IML (i5-10210U)](https://github.com/3ig/IdeaPad-S540-15IML-hackintosh)
* [Lenovo-Ideapad-S540-15IML (i5-10210U)](https://github.com/ayush5harma/IdeaPad-S540-Hackintosh)
* [Lenovo-Ideapad-S540-15IWL (i5-8265U)](https://github.com/IvanAleksandrov94/Lenovo-s340-s540-Big-Sur-OpenCore-i5-8265u)
* [Lenovo-Ideapad-S540-14IML (i5-10210U)](https://github.com/marianopela/Lenovo-Ideapad-S540-14IML-Hackintosh)
* [Lenovo-Ideapad-S540-14IWL (i5-8265U)](https://github.com/Hasodikis/Lenovo-Ideapad-s540-14IWL---Hackintosh)

## BIOS 
https://newsupport.lenovo.com.cn/driveDownloads_detail.html?driveId=78312
<details>
<summary>Details</summary>
2021/07/23 BIOS Version: CKEC17WW http://newdriverdl.lenovo.com.cn/newlenovo/alldriversupload/83713/BIOS-CKCN17WW.exe <br />
2021/01/18 BIOS Version: CKCN16WW http://newdriverdl.lenovo.com.cn/newlenovo/alldriversupload/78312/BIOS-CKCN16WW.exe <br />
2020/07/24 BIOS Version: CKCN15WW http://newdriverdl.lenovo.com.cn/newlenovo/alldriversupload/73409/BIOS-CKCN15WW.exe <br />
2020/06/22 BIOS Version: CKCN14WW http://newdriverdl.lenovo.com.cn/newlenovo/alldriversupload/72386/BIOS-CKCN14WW.exe <br />
2019/12/16 BIOS Version: CKCN12WW http://newdriverdl.lenovo.com.cn/newlenovo/alldriversupload/67169/BIOS-CKCN12WW.exe <br />
2019/08/08 BIOS Version: CKCN11WW http://newdriverdl.lenovo.com.cn/newlenovo/alldriversupload/60449/BIOS-CKCN11WW.exe <br />
</details>

## Microcode
https://newsupport.lenovo.com.cn/driveDownloads_detail.html?driveId=77695
<details>
<summary>Details</summary>
2021/07/23 Version: CKME05WW http://newdriverdl.lenovo.com.cn/newlenovo/alldriversupload/83714/FW-CKME05WW.exe <br />
2020/12/17 Version: CKME03WW http://newdriverdl.lenovo.com.cn/newlenovo/alldriversupload/77695/FW-CKME03WW.exe <br />
2020/06/23 Version: CKME02WW http://newdriverdl.lenovo.com.cn/newlenovo/alldriversupload/72429/ME-CKME02WW.exe <br />
2019/12/16 Version: CKME01WW http://newdriverdl.lenovo.com.cn/newlenovo/alldriversupload/67174/FW-CKME01WW.exe <br />
</details>

## Changelog
* 2022-06-12 20:30
    * Reopen AvoidRuntimeDefrag
    * Opencore updated to 0.8.2dev
    * Update kexts

* See [changelog-en.md](changelog-en.md) for the history of changes

## [Installation](https://www.bilibili.com/video/BV1C64y1q7r1/)
1. If you are using OpenCore, Please use BIOS except for 1.0.2  (1.0.2 you need to turn off the Hyper-Threading to use OC.)
2. Change BIOS settings
      * https://github.com/lietxia/XiaoXinAir14IML_2019_hackintosh/wiki/bios
3. Change DVMT and CFG Lock.
4. Download [balenaEtcher](https://www.balena.io/etcher/), use it to flash [2022-01-14-XiaoXinAir14IML-3in1-installerV6.dmg](https://pan.baidu.com/s/1pUuVZ_A3r1fxP_36RgR6oQ)(Password：gt57)  
5. Boot the Second EFI partition and choose the system you want to install.

## Advice
* [Prevent intermittent hackintosh disconnections Thanks @Unstoppablesss] Modify System Preferences/Eneragy Saver/Power Adapter/Put hard disk to sleep when possible(modify to off)  
* Because current hibernate cannot wake up normally, in order to avoid affecting sleep, use  the terminal to turn off hibernate `sudo pmset -a hibernatemode 0`

> XiaoXin AIR14-2019 i5-10210u QQ group number: 1032311345  

### YogaSMC： `Experimental`
* Normal: Fan three modes switch, microphone mute, flight mode, F10 switch screen, touchpad switch hint, keyboard backlight, Fn function key switch.
* Abnormal: the camera has a hint, but it can't be turned off, the lock function can't be used, FN + Q can't work, the keyboard backlight will be displayed incorrectly when the power is plugged in, and the battery temperature can't be read out.

### Trackpad
Use this way if rebuilding the cache touchpad still does not work:
https://github.com/lietxia/XiaoXinAir14IML_2019_hackintosh/releases/tag/2020.04.05

### Synchronize bluetooth link keys from macOS to windows
https://github.com/lietxia/BT-LinkkeySync

### Big Sur hidpi

    bash -c "$(curl -fsSL https://raw.githubusercontent.com/xzhih/one-key-hidpi/dev/hidpi.sh)"

### Catalina hidpi

    bash -c "$(curl -fsSL https://raw.githubusercontent.com/xzhih/one-key-hidpi/master/hidpi.sh)"
    
### DW1820A Windows 10 driver
https://www.dell.com/support/home/zh-cn/drivers/driversdetails?driverid=98wfd

### Change DVMT and CFG Lock
* You must unlock `CFG Lock` , otherwise, you can't use both OpenCore and Clover。 
* We recommend to change `DVMT` into 64M, there's no damage to your computer. 

#### Recommend: get into hidden BIOS  
You need to disable`onekeybattery`in the BIOS to enter hidden bios.  

- The way to enter hidden BIOS
  - Press following buttons with your computer closed.
    - `F4` → `4` → `R` → `F` → `V`
    - `F5` → `5` → `T` → `G` → `B`
    - `F6` → `6` → `Y` → `H` → `N`
  - Power on → Press F2, speed up if failed.
- Change the following settings.
  - `Advanced` → `Power & Performance` → `CPU - Power Management Control` → `CPU Lock Configuration` → `CFG Lock` → `Disabled`
  - `Advanced` → `System Agent (SA) Configuration` → `Graphics Configuration` → `DVMT Pre-Allocated` → `64M`

#### Backup solution: change in Windows
Refer to https://github.com/lietxia/XiaoXinAir14IML_2019_hackintosh/wiki/DVMT  
`DVMT`：  

* Area : `SaSetup`
* Offset : `0x107`
* `01` to `02`

`CFG LOCK`：  

* Area : `CpuSetup`  
* Offset : `0x3E`  
* `01` to `00`

### The audio card isn't working.
Switching from win to mac will cause the audio card fail to syart. At this time, you need to turn it off and turn it on again, and the audio card will recover  
Consultation got the answer: win restart is warm boot, will skip hardware detection, directly restart into mac will have problems  

* Suggestion: switch from win to mac, do not restart, shut down first, and then turn on
* Restart from mac won't cause this.


## How to make it better?
* PrintScreen can't be used under mac. I map it to F13 and you can change the shortcut key of screenshot to F13
* Turn on HiDPI (see HiDPI part)

## SSDT
| SSDTs              | Info                                   | Necessary | Recommended | Optional |
| ------------------ | -------------------------------------- | --------- | ----------- | -------- |
| SSDT-SBUS-MCHC     | Fake BUS0, DVL0, MCHC device           |           | √           |          |
| SSDT-EC-USBX       | Fake EC device, USB Power Patch        | √         |             |          |
| SSDT-TPAD-Air14IML | I2C Trachpad patch (AIR14IML only)     | √         |             |          |
| SSDT-DMAC          | Fake DMA controller                    |           |             | √        |
| SSDT-GPRW          | Anti immediate wakeup: 0D/6D           | √         |             |          |
| SSDT-PMC           | Fake PMC device                        |           | √           |          |
| SSDT-HPTE          | Disable HPET patch                     |           |             | √        |
| SSDT-PNLFCFL       | Coffee Lake PNLF patch                 | √         |             |          |
| SSDT-PR00          | X86 CPU Power Management (Enable XCPM) | √         |             |          |
| SSDT-RMCF-Air14IML | PS2 key mapping patch                  | √         |             |          |
| SSDT-UIAC          | Custom USB                             |           | √           |          |
| SSDT-BATX-Air14IML | Battery extra info                     |           |             | √        |
| SSDT-AWAC          | “Fake” RTC timer                       |           | √           |          |
| SSDT-ECRW          | YogaSMC EC accessibility               |           |             | √        |

## Kexts
| Kexts                       | Info                   | Necessary | Optional |
| --------------------------- | ---------------------- | --------- | -------- |
| AirportBrcmFixup.kext       | DW1820A Wi-Fi          |           | √        |
| AppleALC.kext               | HDMI & Audio           | √         |          |
| BluetoolFixup.kext          | Fix Monterey Bluetooth |           | √        |
| BrcmBluetoothInjector.kext  | DW1820A bluetooth      |           | √        |
| BrcmFirmwareData.kext       | DW1820A bluetooth      |           | √        |
| BrcmPatchRAM3.kext          | DW1820A bluetooth      |           | √        |
| Lilu.kext                   | Kernel extension       | √         |          |
| SMCBatteryManager.kext      | SMC battery            | √         |          |
| SMCProcessor.kext           | SMC-processor          | √         |          |
| VirtualSMC.kext             | SMC(important)         | √         |          |
| VoodooI2C.kext              | Trackpad core          | √         |          |
| VoodooI2CHID.kext           | HID trackpad           | √         |          |
| VoodooPS2Controller.kext    | Keyboard driver        | √         |          |
| WhateverGreen.kext          | IGPU driver            | √         |          |
| DebugEnhancer.kext          | Fix msgbuf             |           | √        |
| IntelBluetoothFirmware.kext | AC9560 Bluetooth       |           | √        |
| IntelBluetoothInjector.kext | AC9560 Bluetooth       |           | √        |
| AirportItlwm-Sur.kext       | AC9560 Wi-Fi Big Sur   |           | √        |
| AirportItlwm-Cata.kext      | AC9560 Wi-Fi Catalina  |           | √        |
| AirportItlwm-Monterey.kext  | AC9560 Wi-Fi Monterey  |           | √        |
| YogaSMC.kext                | YogaSMC                |           | √        |
| YogaSMCAlter.kext           | YogaSMC                |           | √        |
| RestrictEvents.kext         | Shield system daemons  |           | √        |
| NVMeFix.kext                | improve nvme SSD       |           | √        |
| VerbStub.kext               | Microphone             |           | √        |

## Credits
- [Acidanthera](https://github.com/acidanthera) for [OpenCore](https://github.com/acidanthera/OpenCorePkg) and [other kexts](https://github.com/acidanthera).
- [Apple](https://www.apple.com) for [macOS](https://www.apple.com/macos).
- [lietxia](https://github.com/lietxia) for the whole EFI.
- [zxystd](https://github.com/zxystd) for developing [itlwm](https://github.com/OpenIntelWireless/itlwm).
- [Bat.bat](https://github.com/williambj1) for developing [IntelBluetoothFirmware](https://github.com/OpenIntelWireless/IntelBluetoothFirmware) and [HeliPort](https://github.com/OpenIntelWireless/HeliPort).
- [alexandred](https://github.com/alexandred) for developing [VoodooI2C](https://github.com/VoodooI2C/VoodooI2C).
- [athlonreg](https://github.com/athlonreg/) for developing [ALCPlugFix](https://github.com/athlonreg/AppleALC-ALCPlugFix) to fix microphone switch issue.
- [win1010525](https://github.com/win1010525) for translating English readme and add AIO version EFI.
- [sun19970908](https://github.com/sun19970908) for providing codec, modify ALCPlugFix and test CPUFriend.
- [stevezhengshiqi](https://github.com/stevezhengshiqi) for [one-key-cpufriend](https://github.com/stevezhengshiqi/one-key-cpufriend)
