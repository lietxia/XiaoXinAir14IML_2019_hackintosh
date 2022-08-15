//
// InputIpObj and InputPortObj are the input objects of ip address and 
// port number, it is used to nodify user to know if format is valid.
//
// Server is a list of all ranged ip addresses
//
// Usage: 
// ParseServerAddr (FormObj.find(".ServerIp"), FormObj.find(".ServerPort"), 
//   AddExtendedServerAddrParams, AddictionalParams)
//
//

//
// Sample of AddExtendedServerAddrParams
//
/*
function AddExtendedServerAddrParams (AddrList, PassParams) {
  //
  // AddrList is a array
  // bsm: BIOS settings migration
  // rfu: Remote firmware update
  //
  gIndexServerList.push ({
    ip: AddrList.ip, 
    port: AddrList.port, 
    func: PassParams
  });
}
*/

//------------------
// Global variables
//------------------
var gIsInputPureAddress = false;

//------------------
// Functions
//------------------
function InitIpParser () {
  gIsInputPureAddress = false;
}

function ParseServerAddr (InputIpObj, InputPortObj, ExtendedParamsFunc, PassParams) {
  var IpStr = InputIpObj.val();
  var PortStr = InputPortObj.val();
  var PortNum = parseInt(PortStr);
  var IpNum;
  var SeperateStr = IpStr.split (".");
  var Idx, SubIdx, RangeIdx, One, Two, Three, Four;
  var IpList = new Array();
  var ParseIpStr = "";
  var SeperateSubIp;
  var SeperateRangeIp;
  var MinIdx, MaxIndx;
  var OneStr, TwoStr, ThreeStr, FourStr;
  var Str;
  var IsPureIp = false;

  //
  // Only ip (255.255.255.255)
  //
  var IpFormat = /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/;

  if (IpStr.match(IpFormat)) {
    IsPureIp = true;
  }
  if (SeperateStr.length != 4) {
    if (InputIpObj) {
      InputIpObj.css("background-color", "#FF3333");
    }
    if (InputPortObj) {
      InputPortObj.css("background-color", "#FF3333");
    }
//    alert ("Error: ip format is not correct");
    return false;
  }
  if (PortStr == "") {
    PortNum = 80;
  }
  if ((PortStr.match(/\./)) || (PortNum == NaN) || (PortNum <= 0) || (PortNum > 65535)) {
    if (InputIpObj) {
      InputIpObj.css("background-color", "#FFFFFF");
    }
    if (InputPortObj) {
      InputPortObj.css("background-color", "#FF3333");
    }
//    alert ("Error: port format is not correct");
    return false;
  }
  if (IsPureIp) {
    gIsInputPureAddress = true;
    ExtendedParamsFunc ({ip: IpStr, port: PortNum}, PassParams);
    return true;
  } else {
    gIsInputPureAddress = false;
  }
  //
  // Ip or Ip range only
  // 192.168.0.1
  // 192.168.[3-254].[1-10]
  // 192.168.[4,6,55].[69,99]
  // 192.168.[7,10-15].[33-40,99,101-120]
  //
  for (Idx = 0; Idx < 4; Idx++) {
    if (SeperateStr[Idx].match(/\[/) && SeperateStr[Idx].match(/\]/)) {
      //
      // Range
      //
      Str = SeperateStr[Idx].replace ("[", "");
      Str = Str.replace ("]", "");
      SeperateSubIp = Str.split (",");
      for (SubIdx = 0; SubIdx < SeperateSubIp.length; SubIdx++) {
        if (SeperateSubIp[SubIdx].match(/-/)) {
          SeperateRangeIp = SeperateSubIp[SubIdx].split("-");
          MinIdx = parseInt (SeperateRangeIp[0]);
          MaxIndx = parseInt (SeperateRangeIp[1]);
          if (((Idx == 0) && (MinIdx == 0)) || 
            (MinIdx < 0) || (MinIdx >= 255) || 
            (MaxIndx < 0) || (MaxIndx >= 255) || 
            (MinIdx >= MaxIndx) || (IpNum == NaN)) {
            
            return false;
          }
          for (RangeIdx = MinIdx; RangeIdx <= MaxIndx; RangeIdx++) {
            if (ParseIpStr.length != 0) {
//              ParseIpStr += "-" + RangeIdx;
              ParseIpStr += "-" + RangeIdx;
            } else {
//              ParseIpStr += RangeIdx.toString();
              ParseIpStr += RangeIdx;
            }
          }
        } else {
          IpNum = parseInt (SeperateSubIp[SubIdx]);
          if (((Idx == 0) && (IpNum == 0)) || 
            (IpNum < 0) || (IpNum >= 255) || 
            (IpNum == NaN)) {
            
            return false;
          }
          if (ParseIpStr.length != 0) {
//            ParseIpStr += "-" + SeperateSubIp[SubIdx];
            ParseIpStr += "-" + IpNum;
          } else {
//            ParseIpStr += SeperateSubIp[SubIdx].toString();
            ParseIpStr += IpNum;
          }
        }
      }
      IpList.push(ParseIpStr);
      ParseIpStr = "";
    } else if (!SeperateStr[Idx].match(/\[/) && !SeperateStr[Idx].match(/\]/)) {
      //
      // Ip number only
      //
      IpNum = parseInt (SeperateStr[Idx]);
      if (((Idx == 0) && (IpNum == 0)) || (IpNum < 0) || (IpNum >= 255) || ((Idx == 3) && (IpNum == 0))) {
        return false;
      }
      IpList.push(SeperateStr[Idx]);
    } else {
//      alert ("IP expression error");
      return false;
    }
  }
  
  OneStr = IpList[0].split("-");
  TwoStr = IpList[1].split("-");
  ThreeStr = IpList[2].split("-");
  FourStr = IpList[3].split("-");
  for (One = 0; One < OneStr.length; One++) {
    for (Two = 0; Two < TwoStr.length; Two++) {
      for (Three = 0; Three < ThreeStr.length; Three++) {
        for (Four = 0; Four < FourStr.length; Four++) {
          ExtendedParamsFunc ({
            ip: OneStr[One] + "." + TwoStr[Two] + "." + ThreeStr[Three] + "." + FourStr[Four], 
            port: PortNum
          }, PassParams);
        }
      }
    }
  }
  
  return true;
}

