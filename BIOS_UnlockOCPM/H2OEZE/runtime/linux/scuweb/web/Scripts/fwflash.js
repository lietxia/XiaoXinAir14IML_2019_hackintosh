

//------------------
// Global static constants
//------------------
var FLASH_REMOTE_SERVER_WARNING    = "Depends on how many selected servers, " +
      "the process time may take a long time.<br /><br />" +
      "Please do <b>NOT</b> relaod this page."
var FLASH_SELF_SERVER_WARNING      = "It may take about 20 seconds, " +
      "please do <b>NOT</b> relaod this page."
var TIMEOUT_TEST                   = 5000;
var TIMEOUT_FLASH                  = 60000;

//------------------
// Global variables
//------------------
//
// Remote server list
//
var gRemoteServers = new Array();
//
// Upload file arguments
//
var gUploadFilesInfo = null;
var gIsSameRadioSelectTwice = false;
//
// Server information is an JSON object
//
var gThisServerInfo = null;
var gIsFlashRemoteServer = false;
var gLocalAddrObj = null;

//------------------
// Initilaizing
//------------------
/*
$.ajaxSetup ({
  //
  // Disable caching of AJAX responses or it may cause problem on IE
  //
  cache: false
});
*/
//------------------
// Functions
//------------------

function ReadLocalAddrNumber () {
  var ip = document.location.hostname;
  var port = document.location.port;

  if ((ip == "localhost") || (ip == "127.0.0.1")) {
    alert ("Host name can NOT be \"" + ip + "\"");
    return;
  }
  gLocalAddrObj = $.parseJSON ("{\"ip\": \"" + ip + "\", \"port\": \"" + port + "\"}");
}

function FwUploadBtnCallback (event) {
  SetUploadMsgVisiblility (false);

  CloneAllOptions ();
  //
  // Present uploading progress
  //
  SetPopupContent ("Uploading file...");
  EnableCtrlBtn (false);
//  beginFileUploadProgress ();
  EnablePopupProgress (true);
  //
  // Submit
  //
  DoSubmitUploadForm (null);
  SetIFrameVisiblility (false);
}

function UploadFirmware () {
  SetPopupContent ("Uploading firmware...");
  EnablePopupProgress (true);
  CloneAllOptions ();
  DoSubmitUploadForm (null);
}

function StorePlatformInfo () {
  GetPlatformInfo (true, function (Data) {
    $("#PlatformInfoSection").html (Data.ModelName + " ver " + Data.ModelVersion);
  });
  GetPlatformInfo (false, function (Data) {
    $("#PlatformInfoStr").html (Data.ModelName + "_" + Data.ModelVersion);
  });
}

function InitUploadFw () {
  initFileUpload (GetClientId (), DoFwFlash);
}

function SetInitPage () {
  $("#MenuList").find ("div.TreeNode[run='run']")
  .find (".SubMenu :first-child").css ("color", TREE_TGT_NODE_COLOR);
//  .find (".SubMenu :first-child").addClass ("TgtLinkColor");
}

function InitFlashPage () {
//  ReadLocalAddrNumber ();
  InitUploadFw ();
  StorePlatformInfo ();
  SetInitPage ();
}

function ListRomFile (FwName, OnlyMsg) {
  if (!OnlyMsg) {
  } else {
    $("#FileLinkRegion").html(FwName);
  }
  if (FwName == "bios.rom") {
    $("#BiosLink").html("<span><a href=\"RomFiles/" + FwName + "\">" + FwName + " ROM</a></span></br />");
  } else if (OnlyMsg) {
    $("#BiosLink").html(FwName);
  } else {
    $("#BiosLink").empty();
  }
  if (FwName == "cmos.rom") {
    $("#BiosLink").html("<span><a href=\"RomFiles/" + FwName + "\">" + FwName + " file</a></span></br />");
  } else if (OnlyMsg) {
    $("#CmosLink").html(FwName);
  } else {
    $("#CmosLink").empty();
  }
}

function FlashRemoteServerFwComplete (Msg, IsErr) {
  SetPopupContent (Msg);
}

function UploadFileAndDataComplete (Msg, IsErr) {
  var RespJsonObj;

  EnablePopupProgress (false);
  if (IsErr) {
    FileUploadComplete (Msg, IsErr);
    ClosePopup ();
    return;
  } else {
    RespJsonObj = $.parseJSON (Msg);
    FileUploadComplete (RespJsonObj.resp, IsErr);
  }

  gUploadFilesInfo = RespJsonObj;
  if (gRemoteServers.length == 0) {
    //
    // Flash self
    //
    FlashSelf (RespJsonObj);
  } else {
    //
    // Flash multi-server with input address, but test server first then flash
    //
    FlashRemoteServers ();
  }
}

function FlashSelf (RespJsonObj) {
  //
  // NOTE: FwFlash.cgi return a text/html content-type but it's json text string
  //
  PopupLoading (FLASH_SELF_SERVER_WARNING, false);
  //
  // Timeout can NOT be too short, flash process need 10~20 seconds.
  //
  $.ajax({
    cache: false,
    url: "Actions/FwFlash.cgi?func=fsf&fn=" + RespJsonObj.fn +
      "&pd=" + RespJsonObj.pd + "&ft=" + RespJsonObj.ft + "&cs=" + RespJsonObj.cs,
    timeout: 60000,
    complete: function (jqXHR, textStatus) {
      var MsgNode = $("#UploadMessage");
      var MsgStr;
      var IsErr = true;
      var FontColor;

      if (textStatus == "success") {
        var JsonObj;

        try {
          JsonObj = $.parseJSON (jqXHR.responseText);
          MsgStr = JsonObj.resp;
          if (JsonObj.iserr == "false") {
            IsErr = false;
          }
        } catch (e) {
          MsgStr = jqXHR.responseText;
        }
      } else {
        MsgStr = textStatus;
      }
      FontColor = (IsErr) ? "red" : "green";
      MsgNode.html('<span style="color: ' + FontColor + ';">' + MsgStr + '</span>');
      SetOkBtnAndContent ("Flash firmware complete: " + MsgStr, ClosePopup);
    }
  });
}

function FlashRemoteServers () {
//  SetPopupContent (FLASH_REMOTE_SERVER_WARNING);
  PopupLoading (FLASH_REMOTE_SERVER_WARNING, null);
  //
  // Test one and flash one
  //
  setTimeout (TestServerOneByOne, 20);
}

function FlashFwOneByOne () {
  //
  // NOTE: ProxyFwScuProcess.cgi return a text/html content-type and
  // it runs a javascript named FlashRemoteServerFwComplete.
  // This FlashRemoteServerFwComplete javascript contains a json text string
  // from ProxyFwScuProcess.cgi.
  //
  var ProxyUrl;
  var HostPort;

  if (gRemoteServers.length <= 0) {
    ClosePopup ();
    return;
  }
  if (document.location.port != "") {
    HostPort = document.location.port;
  } else {
    HostPort = "80";
  }
  //
  // Timeout can NOT be too short, flash process need 10~20 seconds.
  //
  ProxyUrl = "Actions/ProxyFwScuProcess.cgi?ip=" + gRemoteServers[0].ip +
    "&port=" + gRemoteServers[0].port + "&func=ffw&fn=" + gUploadFilesInfo.fn +
    "&pd=" + gUploadFilesInfo.pd + "&ft=" + gUploadFilesInfo.ft +
    "&id=" + GetClientId () + "&hport=" + HostPort + "&cs=" + gUploadFilesInfo.cs;

  $.ajax({
    cache: false,
    url: ProxyUrl,
    complete: function (jqXHR, textStatus) {
      var ThisServer = gRemoteServers.splice (0, 1);

      if (textStatus == "success") {
        var JsonObj;

        try {
          JsonObj = $.parseJSON (jqXHR.responseText);
          if (JsonObj.iserr == "false") {
            PrintTestServerResult (ThisServer[0],
              JsonObj.resp + "<br />",
              true);
          } else {
            PrintTestServerResult (ThisServer[0],
              JsonObj.resp,
              false);
          }
        } catch (e) {
          PrintTestServerResult (ThisServer[0],
            "Parse response error",
            false);
        }
      } else {
        ThisServer[0].msgobj.append (textStatus + "<br />");
      }
      if (gRemoteServers.length > 0) {
        SetPopupContent (ThisServer[0].ip + ":" + ThisServer[0].port + " is " +
          textStatus + "<br /><br />" + FLASH_REMOTE_SERVER_WARNING);
        setTimeout (TestServerOneByOne, 20);
      } else {
        SetOkBtnAndContent ("Flash process is complete", ClosePopup);
      }
    }
  });
}

function AddServerToList (AddrObj, PassParams) {
  gRemoteServers.push ({
    ip: AddrObj.ip,
    port: AddrObj.port,
    msgobj: PassParams
  });
}

function PrintTestServerResult (AddrObj, RespStatus, IsSuccess) {
//  var StatusNode = $("#SettingContent .StateMsg");
  var StatusNode = AddrObj.msgobj;

  StatusNode.append ("[" + AddrObj.ip + ":" + AddrObj.port + "] ");
  if (IsSuccess) {
//    StatusNode.append ("<span style='color: green'>" + RespStatus + "</span>");
    StatusNode.html (StatusNode.html () + "<span style='color: green'>" + RespStatus + "</span>");
  } else {
//    StatusNode.append ("<span style='color: red'>" + RespStatus + "</span><br />");
    StatusNode.html (StatusNode.html () + "<span style='color: red'>" + RespStatus + "</span><br />");
  }
}

function TestServerOneByOne () {
  var UrlStr;

  if (gRemoteServers.length <= 0) {
    ClosePopup ();
    return;
  }
  UrlStr = "Actions/ProxyTestConn.cgi?ip=" + gRemoteServers[0].ip +
    "&port=" + gRemoteServers[0].port + "&func=conn";
/*
  if (document.domain != gRemoteServers[0].ip) {
    UrlStr = "Actions/ProxyTestConn.cgi?ip=" + gRemoteServers[0].ip +
      "&port=" + gRemoteServers[0].port + "&func=conn";
  } else {
    UrlStr = "Actions/TestConn.cgi";
  }
*/

  $.ajax({
    cache: false,
    url: UrlStr,
    timeout: TIMEOUT_TEST,
    async: true,
    dataType: "json",
    complete: function (jqXHR, textStatus) {
      var ThisObj = gRemoteServers[0];

      $("#UploadMessage").html ("").css ("display", "none");

      if (textStatus == "success") {
        var Data = $.parseJSON (jqXHR.responseText);

        if (!Data) {
          PrintTestServerResult (ThisObj,
            "Server exists but doesn't support this feature",
            false);
        } else if (!Data.StatusCode) {
          //
          // Only flash same platform
          //
          if ((gThisServerInfo.ModelName == Data.ModelName) &&
            (gThisServerInfo.ModelVersion == Data.ModelVersion)) {

            if (gIsFlashRemoteServer) {
              //
              // Same platform! Do flash firmware
              //
              setTimeout (FlashFwOneByOne, 20);
              return;
            }

            PrintTestServerResult (ThisObj,
              "Same platform<br />",
              true);

          } else {
            PrintTestServerResult (ThisObj,
              Data.ModelName + ":" + Data.ModelVersion + " (Different Platform)",
              false);
          }
        } else {
          PrintTestServerResult (ThisObj,
            Data.StatusCode + ":" + Data.Response,
            false);
        }
      } else {
        if (textStatus == "parsererror") {
          //
          // This is a web server but not support this feature
          //
          PrintTestServerResult (ThisObj,
            "Server exists but doesn't support this feature",
            false);
        } else if (jqXHR.statusText != "OK") {
          //
          // Some unknown error
          //
          PrintTestServerResult (ThisObj,
            jqXHR.status + ":" + jqXHR.statusText,
            false);
        } else {
          //
          // error, timeout
          //
          PrintTestServerResult (ThisObj,
            textStatus,
            false);
        }
      }
      gRemoteServers.splice (0, 1);
      if (gRemoteServers.length > 0) {
        setTimeout (TestServerOneByOne, 20);
      } else {
        ClosePopup ();
      }
    }
  }); // End of Ajax
}

function InitGlobalObjects () {
  gUploadFilesInfo = null;
  //
  // Server information is an JSON object
  //
  if (!gThisServerInfo) {
    gThisServerInfo = GetServerInfo ();
    if (!gThisServerInfo) {
      return false;
    }
  }
  if (gRemoteServers.length > 0) {
    gRemoteServers.splice (0, gRemoteServers.length);
  }

  return true;
}

function ParseAddrAndResetMsgObj (AddrObj, ErrCtrlCallback) {
  var IpObj, PortObj, MsgObj;

  IpObj = AddrObj.find(".ServerIp");
  IpObj.css("background-color", "#ffffff");

  PortObj = AddrObj.find(".ServerPort");
  PortObj.css("background-color", "#ffffff");

  MsgObj = AddrObj.find(".StateMsg");
  MsgObj.empty().css("display", "").height("auto");

  if (ParseServerAddr (IpObj, PortObj, AddServerToList, MsgObj) == false) {
    if (ErrCtrlCallback) {
      ErrCtrlCallback ();
    }
    return false;
  }
  return true;
}

function RequestFwFileOperation (FwUrl, ToAppendObj, CompleteCallback) {
  //
  // Timeout can NOT be too short, flash process need 10~20 seconds.
  //
  $.ajax({
    cache: false,
    url: FwUrl,
//    async: false,
    timeout: 40000,
    error: function(xhr) {
      alert ("error");
    },
    success: function(data, textStatus, jqXHR) {
      var JsonObj;
      var MsgObj;

      try {
        JsonObj = $.parseJSON (data);
      } catch (e) {
        PopupInfo ("Backup", null);
        SetOkBtnAndContent (jqXHR.responseText, ClosePopup);
        return;
      }

      if (JsonObj.type == "b") {
        MsgObj = $("#BiosLink");
      } else if (JsonObj.type == "c") {
        MsgObj = $("#CmosLink");
      } else {
        return;
      }
      if (JsonObj.resp == "") {
        MsgObj.html (JsonObj.link);
      } else {
        MsgObj.html (JsonObj.resp);
      }
//      $(ToAppendObj).html(response);
    },
    complete: function (jqXHR, textStatus) {
      if (textStatus != "parsererror") {
        ClosePopup ();
      } else {
        PopupInfo ("Backup", null);
        SetOkBtnAndContent (jqXHR.responseText, ClosePopup);
      }
/*
      if (CompleteCallback) {
        CompleteCallback (jqXHR, textStatus);
      }
*/
    }
  });
}

function InitRomFileLink () {
  RequestFwFileOperation ("../Actions/FwFlash.cgi?func=chk&dl=b",
    $("#FileDlCtrl .GenFileLink")[0], null);
  RequestFwFileOperation ("../Actions/FwFlash.cgi?func=chk&dl=c",
    $("#FileDlCtrl .GenFileLink")[1], null);
//  RequestFwFileOperation ("../Actions/FwFlash.cgi?func=chk&dl=gv",
//    $("#FileDlCtrl .GenFileLink")[2], null);
}

function AdjustMsgBoxHeight (MsgObj, BaseNum) {
  var Count;

  Count = gRemoteServers.length - BaseNum;
  if (Count > 5) {
    MsgObj.height(parseInt (MsgObj.css("font-size").replace("px", "")) * 6);
  } else {
    MsgObj.height("auto");
  }

  return Count;
}

function GenFileChecksum (ProgCallback, SuccessCallback, ErrorCallback) {

  FileObj = GetUploadFileObj ();
  GenLocalFileChecksum (
    FileObj,
    ProgCallback,
    SuccessCallback,
    ErrorCallback,
    null
  );
}

function DoFwFlash () {
  var FinishAct;
  var MsgStr = "";

  if (IsInputFileEmpty ()) {
    PopupInfo ("Flash firmware", null);
    SetOkBtnAndContent ("Choose a file to upload!", ClosePopup);
    return;
  }

  FinishAct = $("#PageUI input[name='FinishAct']:checked").val();
  if (FinishAct == "-r") {
    MsgStr = "After flashing firmware, system will <b>REBOOT</b> immediatly!<br />";
  } else if (FinishAct == "-s") {
    MsgStr = "After flashed firmware, system will <b>SHUTDOWN</b> immediatly!<br />";
  } else if (FinishAct == "-n") {
    MsgStr = "After flashed firmware, system do won't reboot or shutdown!<br />";
  }
  PopupInfo ("Flash firmware", MsgStr + "Are you sure to flash firmware?");

  SetYesNoBtnAndContent (null,
    function () {
      SetPopupContent ("Preparing data...");
      EnableCtrlBtn (false);
      GenFileChecksum (
        function (Percentage) {
        },
        function (ChecksumStr) {
          SetFileChecksum (ChecksumStr);
          FwUploadBtnCallback ();
        },
        function (ErrorStr) {
          SetOkBtnAndContent (ErrorStr, ClosePopup);
        }
      );
    }, ClosePopup
  );
}

function DoMultiFwFlash () {
  var ServersAddrs = $("#SettingContent .ServersAddr");
  var Server, ServerIpObj, ServerPortObj, ServerMsgObj;
  var FileObj;
  var BaseNum = 0;
  var Idx;

  if (!InitGlobalObjects ()) {
    SetOkBtnAndContent ("Can't connect to server", ClosePopup);
    return;
  }

  SetPopupContent ("Parsing addresses...");
  //
  // Parse ip addresses
  //
  for (Idx = 0; Idx < ServersAddrs.length; Idx++) {
    Server = $(ServersAddrs[Idx]);
    ServerMsgObj = Server.find (".StateMsg");
    if (!ParseAddrAndResetMsgObj (Server, function () {
      ServerMsgObj.html("Invalid ip/port format<br />");
    })) {
      continue;
    }
    BaseNum += AdjustMsgBoxHeight (ServerMsgObj, BaseNum);
  } // End of for loop

  gIsFlashRemoteServer = true;

  UploadFirmware ();
}

$("#RomProtectedList input[name='FlashRom']").click (function () {
  $("#FlashAll").attr("checked", false);
});

$("#FlashAll").click (function () {
  $("#RomProtectedList input[name='FlashRom']").attr("checked", false);
});

//
// Cancel 'checked' attribute when select same radio second time
// NOTE: FinishAct must have one option, it won't be canceled
//
$("input[type='radio']").mousedown (function () {
  if (gIsSameRadioSelectTwice) {
    gIsSameRadioSelectTwice = false;
    return;
  }
  if (($(this).attr ("checked")) && ($(this).attr ("name") != "FinishAct")) {
    gIsSameRadioSelectTwice = true;
  }
}).mouseout (function () {
  if (gIsSameRadioSelectTwice) {
    $(this).attr ("checked", false);
    gIsSameRadioSelectTwice = false;
  }
});

$("#MenuList .SubTreeNode").click (function () {
  var ThisNode = $(this);
  var PageName = $(this).attr("func");

  ThisNode.css("color", TREE_TGT_NODE_COLOR);
  ThisNode.siblings().css ("color", "");
//  ThisNode.addClass ("TgtLinkColor");
//  ThisNode.siblings ().removeClass ("TgtLinkColor");

  $("#MainContent .FormPage").filter (":visible").css("display", "none");
  $("#" + PageName).css("display", "");
});

$("#SendToServers").click (function () {
  var FinishAct;
  var MsgStr = "";

/*
  $("#IfrFile").contents().find("#FileToUpload").val ($("#PsudoInputRemoteFile").val ());
  $("#IfrFile").contents().find("#SelFileType").children().each(function(){
    if ($(this).val() == $("#PsudoSelRemoteType option:selected").val ()){
      $(this).attr ("selected", true);
    }
  });
*/
  if (IsInputFileEmpty ()) {
    PopupInfo ("Flash firmware", null);
    SetOkBtnAndContent ("Choose a file to upload!", ClosePopup);
    return;
  }

  FinishAct = $("#PageUI input[name='FinishAct']:checked").val();
  if (FinishAct == "-r") {
    MsgStr = "After flashing firmware, system will <b>REBOOT</b> immediatly!<br />";
  } else if (FinishAct == "-s") {
    MsgStr = "After flashed firmware, system will <b>SHUTDOWN</b> immediatly!<br />";
  } else if (FinishAct == "-n") {
    MsgStr = "After flashed firmware, system do won't reboot or shutdown!<br />";
  }
  PopupInfo ("Flash firmware", MsgStr + "Are you sure to flash firmware?");

  SetYesNoBtnAndContent (null,
    function () {
      SetPopupContent ("Preparing data...");
      EnableCtrlBtn (false);
      GenFileChecksum (
        function (Percentage) {
        },
        function (ChecksumStr) {
          SetFileChecksum (ChecksumStr);
          DoMultiFwFlash ();
        },
        function (ErrorStr) {
          SetYesNoBtnAndContent (ErrorStr, ClosePopup);
        }
      );
    }, ClosePopup
  );
});

$("#CleanAllInput").click (function () {
  var RowNodes = $("div.ServersAddr");
  var Idx;

  if (RowNodes.length > 0) {
    $(RowNodes[0]).find(".ServerIp").val("");
    $(RowNodes[0]).find(".ServerPort").val("");
    $(RowNodes[0]).find(".StatePass").css("display", "none");
    $(RowNodes[0]).find(".StateFail").css("display", "none");
    $(RowNodes[0]).find(".StateMsg").empty();

    for (Idx = 1; Idx < RowNodes.length; Idx++) {
      $(RowNodes[Idx]).remove();
    }
  }
  CloseLoadingInfo ();
});

$("#SettingContent .FuncCtrl").click (function () {
  var ThisNode = $(this);
  var FuncIndex = parseInt (ThisNode.attr("func"));
  var RowNode = ThisNode.parents(".Row");
  var Count = 0;
  var ServerIpObj;
  var ServerPortObj;

  if (FuncIndex == 1) {
    var NextRow;
    //
    // Insert a row
    //
    RowNode.clone(true).insertAfter(RowNode);
    NextRow = RowNode.next();
    NextRow.find(".ServerIp").val("").css("background-color", "#ffffff");
    NextRow.find(".ServerPort").val("").css("background-color", "#ffffff");
    NextRow.find(".StatePass, .StateFail").css("display", "none");
    NextRow.find(".StateMsg").empty().height("auto").css("display", "none");
  } else if (FuncIndex == 2) {
    //
    // Remove this row
    //
    if (RowNode.siblings().length > 0) {
      RowNode.remove();
    }
  } else if (FuncIndex == 3) {
    //
    // Test connection
    //
    var Idx;
    var MsgNode = RowNode.find(".StateMsg");
    var ProcessTime, ProcessSec;
    var FontSize;

    SetPopupTitle ("Test remote server");
    PopupLoading ("<div style='text-align: center'>" +
      "Processing...<br />Please wait" +
      "</div>", false);

    if (!InitGlobalObjects ()) {
      SetOkBtnAndContent ("Can't connect to server", ClosePopup);
      return;
    }

    if (!ParseAddrAndResetMsgObj (RowNode, function () {
      SetOkBtnAndContent ("Format of ip/port is wrong", ClosePopup);
    })) {
      return;
    }
    //
    // Auto adjust status box size
    //
    FontSize = parseInt (MsgNode.css("font-size").replace("px", ""));
    if (gRemoteServers.length > 5) {
      MsgNode.height(FontSize * 6);
    } else {
      MsgNode.height("auto");
    }
    ProcessMin = parseInt ((gRemoteServers.length * (TIMEOUT_TEST / 1000)) / 60);
    ProcessSec = parseInt ((gRemoteServers.length * (TIMEOUT_TEST / 1000)) % 60);
    SetPopupContent ("<div style='text-align: center'>" +
      "Processing...<br />It's about " +  ProcessMin + ":" + ProcessSec +
      " to finish</div>");

    TestServerOneByOne ();
  }
});

$("#FlashLocal").click (function () {
/*
  var InpuFile = $("#PsudoInputLocalFile").val ();

  document.getElementById('IfrFile').contentWindow.document.getElementById('FileUploadId').value = InpuFile;
//  $("#IfrFile").contents().find("input:file").val (InpuFile);
//  $("#IfrFile").contents().find("#FileToUpload").val (InpuFile);
  $("#IfrFile").contents().find("#SelFileType").children().each(function() {
    if ($(this).val () == $("#PsudoSelLocalType option:selected").val ()) {
      $(this).attr ("selected", true);
    }
  });
*/
  DoFwFlash ();
});

$("fieldset .BackupCheckbox").click (function () {
  var TargetFile = $(this).attr ("func");
  var InputNode = $("#Backup" + TargetFile + "Name");
  var BtnNode = InputNode.next ();

  if ($(this).is (":checked")) {
    if (InputNode.val () == "") {
      InputNode.val ($("#PlatformInfoStr").html() + "_" + TargetFile + ".fd");
    }
    InputNode.removeAttr("disabled");
    BtnNode.removeAttr("disabled");

  } else {
    InputNode.attr ('disabled', true);
    BtnNode.attr ('disabled', true);
  }

});

$("fieldset .BackupBtn").click (function () {
  var ThisNode = $(this);
  var Target = ThisNode.attr("func");
  var FileNameNode = ThisNode.prev ();

  if (FileNameNode.val () == "") {
    PopupInfo ("Backup", null);
    SetOkBtnAndContent ("Please enter filename...", ClosePopup);
    return;
  }
  PopupLoading (FLASH_SELF_SERVER_WARNING, false);

  RequestFwFileOperation (
    "../Actions/FwFlash.cgi?func=gen&dl=" + Target + "&fn=" + FileNameNode.val (),
    ThisNode.parent ().next (),
    function (jqXHR, textStatus) {
      ClosePopup ();
    });
});

$("#MenuList .SubMenu a"). click (function () {
  var ThisForm = $("div.FormPage:visible");
  var ThisNode = $(this);
  var TargetForm;

  if (!ThisNode.is ("[id$='Section']")) {
    return;
  }

  TargetForm = $("#" + ThisNode.attr ("id").split ("Section")[0]);
  if (ThisForm.attr ("id") == TargetForm.attr ("id")) {
    return;
  }
  ThisForm.toggle ();
  TargetForm.toggle ();

});

