* 2021-08-09 22:20
    * 添加USB鼠标OC界面支持
    * 删除 CPUFriend， itlwm 和 USBPorts
    * 修正 IntelBluetoothFirmware 的 MaxKernel 为 21.99.99
    * 添加 DebugEnhancer
    * 启用 Verbstub
    * 更新 itlwm 驱动

* 2021-08-07 07:44
    * 修正`Ctrl`+`Enter`不能设置默认系统的问题

* 2021-08-04 17:53
    * 支持macOS 12 Monterey Beta 蓝牙可用✅（已知问题：关机或重启后键盘⌨️失灵）
    * 更新opencore到0.7.2
    * 更新Clover到v5138

* 2021-06-11 20:41
    * 支持macOS 12 Monterey Beta（dw1820a Wi-Fi✅。dw1820a蓝牙⛔。Intel Wi-Fi✅。Intel蓝牙⛔。睡眠和唤醒✅。触摸板✅。HDMI✅。摄像头✅）
    
* 2021-06-10 08:20
    * opencore更新到0.7.0
    * 支持macOS 12 Monterey Beta（dw1820a Wi-Fi✅。dw1820a蓝牙⛔。Intel Wi-Fi⛔。Intel蓝牙⛔。睡眠和唤醒✅。触摸板正常✅） 
    * 更新几个kext

* 2021-04-14 11:13
    * 🆕 opencore更新到0.6.8 
    * 🆕 clover更新到r5133
    * 🆕 更新几个kext（不重要）

* 2021-02-18 11:25
    * OpenCore添加了图形界面，修改设置可以引导Windows
    * Clover更新到r5130，不再需要`DataHubDex.efi`
    * 重新修改`SSDT-BATX-Air14IML.aml`，让其显示电池剩余可用时间
    * 重新添加`SSDT-UIAC.aml`(它可能影响睡眠?)
    * YogaSMC更新到1.4.3，新版YogaSMC的`SSDT-ECRW.aml`发生了变化，做了更新。
  
* 2021-02-11 14:22
    * 删除clover的intel Wifi配置
    * 改回用`WhatEverGreen`来屏蔽mx250 `disable-external-gpu`

* 2021-02-10 12:00
    * 修复使用`YogaSMC`之后KP
    * 新增主题和开机音频

> 测试发现还是没声

* 2021-02-10 01:03
    * 添加`SSDT-NDGP_OFF-Air14IML.aml`用来屏蔽独立显卡
    * 触摸板`SSDT-TPAD-Air14IML.aml`改为GPIO中断模式，pin=`50`
    * 修正`SSDT-BATX-Air14IML.aml`，让其显示电池剩余可用时间
    * 更新`voodooi2c`到2.6.4
    * 删掉不再需要的`SSDT-XSPI.aml`,`SSDT-UIAC.aml`,`SMCSuperIO.kext`,`NoTouchID.kext`
    * 修正Clover不能引导BigSur的问题(需要选Preboot来引导bigSur)
    * 小幅改动`ALCPlugFix`的`install.command`和`uninstall.command`脚本

* 2021-02-05 08:20
    * 缩减itlwm和蓝牙固件，博通没有变化 

* 2021-02-03 22:23
    * 更新opencore到0.6.6-MOD (补丁只对macOS生效)，更新Clover到5129
    * opencore做了整合，默认配置同时用于DW1820A和原装intelAC9560网卡，你也可以选择你网卡的专版，例如把`config-dw1920.plist`改成`config.plist`即可。
    * 更新lilu,appleALC,WEG,vSMC,voodooPS2,博通网卡的kext到最新版
    * 修改或重命名为opencore官方的DSDT
        * `SSDT-EC` + `SSDT-USBX` => `SSDT-EC-USBX` 
        * `SSDT-SUBS` + `SSDT-MCHC` => `SSDT-SBUS-MCHC`
        * `SSDT-PNLF-CFL` => `SSDT-PNLFCFL`
        * `SSDT-PMCR` => `SSDT-PMC`
        * `SSDT-RTC_Y-AWAC_N` => `SSDT-AWAC`
    * 修改`SSDT-RMCF`为`不改变键位`(原先会交换option cmd)，并加上系统判断，在非macOS下不启用补丁，并改名为`SSDT-RMCF-Air14IML.aml`
    * 添加`RestrictEvents.kext`，他可以屏蔽一些可能造成错误的加载项。
    * 可选`YogaSMC`，因为在我电脑上有一些小问题，默认不启用。想启用就加载`YogaSMC.kext` `YogaSMCAlter.kext` `SSDT-RCSM` `SSDT-ECRW`

* 2021-01-21 11:30
    * 更新Opencore分支，加入YogaSMC，itlwm更新至1.3.0_alpha精简版，更新voodooi2c

* 2021-01-16 22:06
    * 更新Clover分支。Clover v5.1 r5128

* 2021-01-06 18:30
    * 精简AirportItlwm，Big Sur和Catalina共5M（但只能使用AC9560网卡）
    * 可能加快了AC 9560网卡的开机
    * AIO版本在博通和Intel网卡中都适用
    
* 2021-01-06 16:00
    * 更新kext，更新opencore到0.6.5
    * 新版whatEverGreen.kext需要增加启动参数`-igfxblr`才能正常运行
    * 新增`SSDT-BATS-Air14IML.aml`能多显示一些电池信息(并没有什么用)

* 2021-1-2 16:17
    * 整合Intel网卡和博通网卡驱动，修复itlwm在Big Sur无log

* 2020-12-27 23:00
    * 更新voodooI2C.kext voodooI2CHID.text

* 2020-12-26 10:00
    * 更新opencore到0.6.4
    * kext更新
    * 新版voodooPS2取消了option 和 command键的交换，所以修改了`SSDT-RMCF.aml`启用option 和 command键的交换。
* 2020-11-13 20:05
    * 暂时放弃Clover支线的更新。OC版本能同时正常用于10.15.X（推荐10.15.7）和big Sur11.0.1
    * OpenCore更新到0.6.3，各类kext更新到最新。
    * 这个EFI是针对网卡换成DW1820A的，如果是原装intel网卡，用这个EFI网卡不能驱动，需要改一下，过一阵找人改一个。

> win1010525 发布的AIO版本通用
> 自从2021-01-16开始，Clover已经重新更新了

* 2020-08-07 10:15
    * OpenCore更新到0.6.0，Clover更新到r5120。
    * 因为AppleAlc更新，所以删除FakePCIID_Intel_HDMI_Audio.kext和FakePCIID.kext
    * 机型换成MacBookPro13 2020(和之前没什么区别)
    * kext更新到最新版
* 2020-06-13 16:38 
    * 更新opencore成0.5.9官方正式版。更新clover到v5.0 r5119。更新kexts。
* 2020-05-06 21:36 
    * SSDT-OCPublic-Merge.aml 合并 SSDT-EC.aml、SSDT-RTC0.aml、SSDT-USBX.aml、SSDT-ALS0.aml、SSDT-MCHC.aml 更新 kexts 更新opencore和clover，机型改为MacBook Air2020 ，删掉 CPUFriend.kext、CPUFriendDataProvider.kext
* 2020-04-11 08:39 
    * 修正了无法静音的bug，更新kext
    * 更新clover到5019 更新了lilu等等kext……
    * 没看到什么可观的变化，可以无视这个更新
* 2020-03-26 11:05 
    * 更新触摸板驱动，多指更加灵敏，更新kext到最新版，
    * OC换成魔改版，开机节目更加美观，clover升级到最最新版
* 2020-03-10 14:00 
    * 修复了FN+F11 FN+F12调亮度的功能,更新了kext
* 2020-02-21 21:00 
    * 小更新，如果进不去系统，进备用efi引导，进去后打开命令行输入 `sudo nvram -c` 清除了nvram后这个efi能进去
* 2020-02-21 00:00 
    * 更新所有kext到最新
* 2020-02-24 14:00 
    * 大部分都正常了,加了openCore版
