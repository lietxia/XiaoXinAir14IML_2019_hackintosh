![2](Results/2.png)
![3](Results/3.png)

[中文](./readme.md)
ENGLISH

## Description:
* The behaviors involved in this passage may cause the computer to fail to start or even damage the motherboard. Please conduct the experiment after knowing the risks
* Do not overclock the memory!!!

## Purpose:
	Unlock the overclocking performance menu menu and items

## Tools:
* FPT H2OEZE SetupUtility_UnlockOCPM.ffs

## Reference:
* Original text from [Baidu Tieba](https://tieba.baidu.com/p/6118801225) 

## Steps:
1.Manually turn off bios lock and flash write protection to enable FPT tool to burn BIOS image.  

> [Hidden BIOS](https://user-images.githubusercontent.com/50404193/104993733-3b1b4280-5a5e-11eb-8916-a977c8b0d54c.jpg) -- Advanced  
> PCH-IO Configuration -- flash protection range registers -> disable  
> PCH-IO Configuration -- security configuration -- BIOS lock -> disable  

2.Use the FPT tool to export the current BIOS

> Run backup under the fpt14 tool as administrator  
> After running the command line window, the backup.fd file will be generated in the current directory

3.Replace the SetuUtility module with the H2OEZE tool

> Run the H2OEZE tool and selects the backup .fd file exported by fpt14 as administrator.    
> Components -- module -- replace module function on the left side of the window  
> Select module to replace on the right side of the window, scroll to the back to find the module of xxxxxxxxxxxxxxxxx (fvxx) (setuputility)  
> On the right side of the window, load module form.. select the setuputility.ffs supplied with the SetupUtility_UnlockOCPM, then apply.  
> Click Save as.., select the fpt14 directory, name it change.fd, and save it. 

4.Use the FPT tool to brush back the modified BIOS (DANGEROUS!!!)

> Run change.bat as administrator   
> A command line window will pop up, and it will exit automatically after running. Restart your PC and it is completed  
> If an error is reported, flash the backup.fd file previously backed up, and execute change.bat to restore BIOS, then give up or ask for further assistance.    

## Postscript:
I bought a 3200mhz 16g memory and found that it works at 2667 after replacing it.  
The first thing I thought of was that the second memory is low-frequency, and the borad adjust the frequency according to the frequency of on-board 4G memory.  
So I entered the BIOS and @#¥%*&, but failed to find the section , then I edited the BIOS and @#¥%, but it did not work either.  
I looked up the motherboard parameters again. The CPU memory control only supports 2666, WTF!!!