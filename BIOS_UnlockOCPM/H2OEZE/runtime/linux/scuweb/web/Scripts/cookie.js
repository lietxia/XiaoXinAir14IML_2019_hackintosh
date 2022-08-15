
//------------------
// Global variables
//------------------
var gCookieNameInitialString           = "insyde_";
var gModuleActionPath                  = "../actions/";

//------------------
// Initilaizing
//------------------

//------------------
// Functions
//------------------

function GenRandomId (IdLen) {
  var Index = 0;
  var IdStr = "";
  var RandomNumber;
  
  if (IdLen <= 0) {
    IdLen = 8;
  }

  while(Index < IdLen){
    RandomNumber = (Math.floor((Math.random() * 100)) % 94) + 33;
    if ((RandomNumber >=33) && (RandomNumber <=47)) {
      continue; 
    }
    if ((RandomNumber >=58) && (RandomNumber <=64)) {
      continue; 
    }
    if ((RandomNumber >=91) && (RandomNumber <=96)) {
      continue; 
    }
    if ((RandomNumber >=123) && (RandomNumber <=126)) {
      continue; 
    }
    IdStr += String.fromCharCode(RandomNumber);
    Index++;
  }
  
  return IdStr;
}

function IsCookieExist (CookieName) {
  var CookiesArray = document.cookie.split(";");
  var Cookie;
  var Idx;
  
  for (Idx in CookiesArray) {
    Cookie = CookiesArray[Idx].split("=");
    if (Cookie[0] == CookieName) {
      return true;
    }
  }
  
  return false;
}

//
// The following functions is referened by 
// http://jquery-howto.blogspot.com/2010/09/jquery-cookies-getsetdelete-plugin.html
//
function SetCookie (CookieName, Value, ExprieDays) {
  var DateObj;
  var Expires;
  var CookieLength;

  if (ExprieDays) {
    DateObj = new Date();

    DateObj.setTime (DateObj.getTime() + (ExprieDays * 24 * 60 * 60 * 1000));
    Expires = "; expires=" + DateObj.toGMTString();
  } else {
    Expires = "";
  }
  if (document.cookie != undefined) {
    CookieLength = document.cookie.length;
  } else {
    CookieLength = 0;
  }
  document.cookie = CookieName + "=" + escape (Value) + Expires;
  if (CookieLength == document.cookie.length) {
    return false;
  }
  
  return true;
}

function GetCookie (CookieName) {
  var NameEQ = CookieName + "=";
  var CookiesArray;
  var Cookie;
  var Idx;
  
  if ((document.cookie == undefined) || (document.cookie.length == 0)) {
    return null;
  }
  
  CookiesArray = document.cookie.split('; ');
  for(var Idx = 0; Idx < CookiesArray.length; Idx++) {
    Cookie = CookiesArray[Idx];
    while (Cookie.charAt(0) == ' ') {
      Cookie = Cookie.substring (1, Cookie.length);
    }
    if (Cookie.indexOf (NameEQ) == 0) {
      return unescape (Cookie.substring (NameEQ.length, Cookie.length));
    }
  }
  
  return null;
}

function RemoveCookie (CookieName) {
  SetCookie (CookieName, "", -1);
}

function SavePostDataInCookie () {
  var ScuData;
  var ServerAddrsData;
  var PostData;
  var ClientId;
  var RtnInfo;

  ClientId = GetClientId ();
  
  $('#DataForm').find(':input').removeAttr("disabled");
  ScuData = $('#DataForm').serialize();
  ServerAddrsData = $('#RemoteCtrlForm').serialize();
  
  PostData = "1::" + ClientId + "::" + ScuData + "::" + ServerAddrsData;

  RtnInfo = SendAjaxHttpData ("../Actions/SaveClientData.cgi", PostData, 60);
  
  return RtnInfo;
}

function LoadPostDataInCookie () {
  var PostData;
  var ServerInfo;
  var CookieName;
  var ClientId;

  ClientId = GetClientId ();
  PostData = "2::" + ClientId;
  PostData = SendAjaxHttpData ("../Actions/SaveClientData.cgi", PostData, 60);

  return PostData;
}

function LoadServerAddrInfoInCookie () {
  var ServerAddrsInfo;
  var ServerInfo;
  var CookieName;

  ServerInfo = ReadAjaxHttpData ("../Actions/TestConn.cgi");
  ServerInfo = $.parseJSON (ServerInfo);
  CookieName = GenCookieName (ServerInfo);
  ServerAddrsInfo = GetCookie (CookieName + "_ServerAddrs");

  return ServerAddrsInfo;
}

function RestoreServerAddrInfoToForm (FormObj, PostData) {
  var RowObjs = FormObj.find('.ServersAddr');
  var ServerDatas;
  var Data;
  var InputObj;
  var Pattern;
  var Idx, SubIdx;
  var Row;
  var NextRow;
  var DataAmount;
  var ServerDataRows;
  var NowRowAmount;
  var TotalRowAmount;
  
  if ((PostData == null) || (PostData.length == 0)) {
    return;
  }
  
  ServerDatas = unescape(PostData).split("&insydesettings=1");
  ServerDataRows = ServerDatas.length - 1;
  NowRowAmount = RowObjs.length;
  TotalRowAmount = (NowRowAmount > ServerDataRows) ? NowRowAmount: ServerDataRows;
  
  for (Idx = 0; Idx < TotalRowAmount; Idx++) {
    DataAmount = ServerDatas[Idx].split ("&");
    if ((ServerDataRows > NowRowAmount) && (Idx >= NowRowAmount)) {
      $(Row).clone(true).insertAfter($(Row));
      Row = $(Row).next();
    } else if ((NowRowAmount > ServerDataRows) && (Idx >= ServerDataRows)) {
      $(RowObjs[Idx]).remove();
      continue;
    } else {
      Row = RowObjs[Idx];
    }
    $(Row).find(".ServerReboot").removeAttr ("checked");
    $(Row).find(".ServerForceWrite").removeAttr ("checked");
    for (SubIdx = 0; SubIdx < DataAmount.length; SubIdx++) {
      Data = DataAmount[SubIdx].split ("=");
      if ((Data[0] == "isreboot") && (Data[1] == "on")) {
        $(Row).find(".ServerReboot").attr("checked", true);
      } else if ((Data[0] == "isforce") && (Data[1] == "on")) {
        $(Row).find(".ServerForceWrite").attr("checked", true);
      } else if (Data[0] == "serverfunc") {
        $(Row).find(".ServerFunc").val(Data[1]);
      } else if (Data[0] == "serverip") {
        $(Row).find(".ServerIp").val(Data[1]);
        $(Row).find(".ServerIp").css("background-color", "#ffffff");
      } else if (Data[0] == "serverport") {
        $(Row).find(".ServerPort").val(Data[1]);
        $(Row).find(".ServerPort").css("background-color", "#ffffff");
      }
    }
    $(Row).find(".StatePass, .StateFail").css("display", "none");
//    $(Row).find(".StateMsg").html("").css("display", "none");
    $(Row).find(".StateMsg").css("display", "none");
  }
}

function RestorePostDataToForm (FormObj, PostData) {
  var InputObjs = FormObj.find(':input');
  var DataPatterns = PostData.split("&");
  var InputObj;
  var Pattern;
  var Idx;
  var Options;
  
  for (Idx = 0; Idx < DataPatterns.length; Idx++) {
    Pattern = DataPatterns[Idx].split("=");
    if (Pattern[0].match ("BootOrder-") || 
      (Pattern[0] == "SNewPwd") ||
      (Pattern[0] == "SConfirmPwd") ||
      (Pattern[0] == "UNewPwd") ||
      (Pattern[0] == "UConfirmPwd") ||
      (Pattern[0] == "Month") ||
      (Pattern[0] == "Day") ||
      (Pattern[0] == "Year") ||
      (Pattern[0] == "Hour") ||
      (Pattern[0] == "Minute") ||
      (Pattern[0] == "Second")) {
      
      continue;
    }
    InputObj = $(":input[name='" + Pattern[0] + "']");
    if (InputObj.length <= 0) {
      continue;
    }
    if (InputObj.val() == Pattern[1]) {
      continue;
    }
    InputObj.val(Pattern[1]);
    InputObj.parents(".Row").attr("value", Pattern[1]);
  }
}

function GetServerInfo () {
  var ServerInfo;
  
  ServerInfo = ReadAjaxHttpData ("../Actions/TestConn.cgi");
  try {
    ServerInfo = $.parseJSON (ServerInfo);
  } catch (e) {
    alert ("Can't connect to server");
    ServerInfo = null;
  }
  
  return ServerInfo;
}

function GetClientId () {
  var ServerInfo;
  var CookieName;
  var ClientId;
  
  ServerInfo = GetServerInfo ();
  //
  // Get client id in cookie
  //
  CookieName = GenCookieName (ServerInfo);
  ClientId = GetCookie (CookieName);
  if (!ClientId) {
    ClientId = GenRandomId (10);
    SetCookie (CookieName, ClientId, 60);
  }
  
  return ClientId;
}

function GenClientId () {
  var ServerInfo;
  var CookieName;
  var ClientId;
  
  ServerInfo = GetServerInfo ();
  CookieName = GenCookieName (ServerInfo);
  ClientId = GenRandomId (10);
  SetCookie (CookieName, ClientId, 60);
  
  return ClientId;
}

function GenCookieName (ServerInfo) {
  return gCookieNameInitialString + ServerInfo.ModelName + "_" + ServerInfo.ModelVersion;
}




