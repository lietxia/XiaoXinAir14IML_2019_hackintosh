
//------------------
// Initilaizing
//------------------

//------------------
// Global variables
//------------------
var gIndexServerList = new Array();
var gAjaxTimeout = 5 * 1000;
var gIsOnlyOneServerToScan = false;
var gIsStopScanning = false;

//------------------
// Functions
//------------------
function AddExtendedServerAddrParams (AddrList, PassParams) {
  //
  // bsm: BIOS settings migration
  // rfu: Remote firmware update
  //
  gIndexServerList.push ({
    ip: AddrList.ip,
    port: AddrList.port,
    func: PassParams
  });
}

function GotoTargetPage (TargetObj) {
  var PageName;

  if (!gIsOnlyOneServerToScan) {
    return;
  }
  if (TargetObj[0].func == "bsm") {
    PageName = "BiosSetupInfo.xml";
  } else if (TargetObj[0].func == "rfu") {
    PageName = "flash.html";
  } else {
    return;
  }
  //
  // If there is only one server need to scan, test and redirect to its page
  //
  $(window.location).attr ("href", "http://" + TargetObj[0].ip + ":" + TargetObj[0].port + "/" + PageName);
}

function ScanRemoteServer (FormObj, Func) {
  var OtherNode = $("#ScanResult .RemoteStatus:first").siblings(".RemoteStatus");

  PopupLoading ("Parsing addresses...", false);

  if (OtherNode.length > 0) {
    OtherNode.remove();
  }

  if (gIndexServerList.length > 0) {
    gIndexServerList.splice(0, gIndexServerList.length);
  }
  if (!ParseServerAddr (FormObj.find(".ServerIp"), FormObj.find(".ServerPort"),
    AddExtendedServerAddrParams, Func)) {

    $("#RemoteIpForm .ParsedInfo").html("Ivalid ip/port!");

    ClosePopup ();
    return;
  }
  //
  // If there is only one server need to scan, set it to redirect after test.
  //
  gIsStopScanning = false;

  if (gIndexServerList.length == 1) {
    gIsOnlyOneServerToScan = true;
  }
  SetStopBtnAndContent ("Testing remote server...", function () {
    EnableCtrlBtn (false);
    SetPopupContent ("Stop scanning...");
    gIsStopScanning = true;
  });
//  SetPopupContent ("Testing remote server...");

  TestServerOneByOne ();
}

function PrintScanResult (AddrObj, RespStatus, IsSuccess) {
  var ResultNode = $("#ScanResult").find(".RemoteStatus").last();
  var NextNode;
  var TargetUrl;
  var PageName;
  var Address = AddrObj[0].ip + ":" + AddrObj[0].port;

  ResultNode.clone(true).insertAfter(ResultNode);
  NextNode = ResultNode.next();
  if (IsSuccess) {
    if (AddrObj[0].func == "bsm") {
      TargetUrl = "http://" + Address + "/BiosSetupInfo.xml";
    } else if (AddrObj[0].func == "rfu") {
      TargetUrl = "http://" + Address + "/flash.html";
    } else {
      TargetUrl = "http://" + Address;
    }
    NextNode.find(".SR_Addr").html (
      "[<a href=\"" + TargetUrl + "\" target=\"_blank\">" + Address + "</a>] "
    );
    NextNode.find(".SR_Status").html (
      "<span style='color: green'>" + RespStatus +  "</span>" +
      "<span class=\"SepPipe\">|</span>" +
      "<a href=\"" + TargetUrl + "\">Go!</a>" +
      "<span class=\"SepPipe\">|</span>" +
      "<a href=\"" + TargetUrl + "\" target=\"_blank\">Open in a new window</a>"
    );
  } else {
    NextNode.find(".SR_Addr").html ("[" + Address + "] ");
    NextNode.find(".SR_Status").html ("<span style='color: red'>" + RespStatus +  "</span>");
  }
}

function TestServerOneByOne () {
  var UrlStr;

  if (gIndexServerList.length <= 0) {
    ClosePopup ();
    return;
  }
//  if (document.domain != gIndexServerList[0].ip) {

    UrlStr = "Actions/ProxyTestConn.cgi?ip=" + gIndexServerList[0].ip +
      "&port=" + gIndexServerList[0].port + "&func=conn";
//  UrlStr = "" + gIndexServerList[0].ip + ":" + gIndexServerList[0].port + "/test.html";
//  UrlStr = "http://172.18.4.69:80/Actions/TestConn.cgi";
//  UrlStr = "test.html";
//  } else {
//    UrlStr = "Actions/TestConn.cgi";
//  }

  $.ajax({
    url: UrlStr,
    cache: false,
    timeout: gAjaxTimeout,
    //
    // Cross-domain use jsonp as dataType and it's not a really
    // ajax (it doesn't use XmlHttpRequest), so there is no synchronize way to
    // request data.
    //
    async: true,
    dataType: "json",
    complete: function (jqXHR, textStatus) {
      var ThisObj = gIndexServerList.splice (0, 1);

      if (textStatus == "success") {
        var Data = $.parseJSON (jqXHR.responseText);

        if (!Data.StatusCode) {
          //
          // PrintScanResult won't run if GotoTargetPage decides
          // to redirect page.
          //
          GotoTargetPage (ThisObj);
          PrintScanResult (ThisObj, Data.ModelName + ":" + Data.ModelVersion, true);

        } else {
          PrintScanResult (ThisObj, Data.StatusCode + ":" + Data.Response, false);
        }
      } else if (textStatus == "parsererror") {
        //
        // This is a web server but not support this feature
        //
        PrintScanResult (ThisObj, "Server exists but doesn't support this feature", false);
      } else if (jqXHR.statusText != "OK") {
        //
        // Some unknown error
        //
        PrintScanResult (ThisObj, jqXHR.status + ":" + jqXHR.statusText, false);
      } else {
        //
        // error, timeout
        //
        PrintScanResult (ThisObj, textStatus, false);
      }
      if (gIndexServerList.length > 0) {
        if (!gIsStopScanning) {
          setTimeout (TestServerOneByOne, 20);
        } else {
          gIndexServerList.splice(0, gIndexServerList.length);
          ClosePopup ();
        }
      } else {
        ClosePopup ();
      }
    }
  }); // End of Ajax

}

//------
// Binding functions
//------
/*
$("#MainContent .FuncBtn").click (function () {
  var PageName = $(this).attr("page");
  var FunName = $(this).attr("func");

  if (PageName && FunName) {
    $("#MainFrame .ContPage").filter (":visible").css("display", "none");
    $("#" + PageName).css("display", "inline-block");
    $("#ScanBtn").attr("func", FunName);

    if (FunName == "bsm") {
      $("#FunTitle").html ("BIOS Settings Migration");
    } else if (FunName == "rfu") {
      $("#FunTitle").html ("Remote Insyde H2O Firmware Update");
    }
  }
});
*/

function ToggleCnt () {
  var TargetNode = $("#ScanServer");

  if (TargetNode.is (":visible")) {
    $("#ManagementTool a").css ("color", "");
    TargetNode.css ("display", "none");
    $("#MainContent").css ("display", "inline-block");
  } else {
    $("#ManagementTool a").css ("color", "#000000");
    $("#MainContent").css ("display", "none");
    TargetNode.css ("display", "inline-block");
  }
}

$("#ManagementTool").click (ToggleCnt);
$("#IdxCloseMngBtn").click (ToggleCnt);

$("#IndexBackBtn").click (function () {
  var StatusObj;
  var StatusLeng;
  var Idx = 1;

  $(this).parents (".ContPage").css ("display", "none");
  $("#MainContent").css ("display", "inline-block");

  //
  // Clear all input value and status string
  //
  $("input").val("");
  StatusObj = $("#ScanResult").find (".RemoteStatus");
  StatusLeng = StatusObj.length;

  StatusObj.first().find (".SR_Addr").empty ();
  StatusObj.first().find (".SR_Status").empty ();
  for (; Idx < StatusLeng; Idx++) {
    $(StatusObj[Idx]).remove();
  }
});

$("#ScanBtn").click (function () {
  var FunName = $(this).attr("func");

  $("#RemoteIpForm input").css("background-color", "");

  ScanRemoteServer ($("#RemoteIpForm"), FunName);
});

$("#MenuList a").click (function () {
  var ThisNode = $(this);
  var TargetPage;

  if (ThisNode.attr ("id").split ("Tab").length < 2) {
    return;
  }
  TargetPage = $("#" + ThisNode.attr ("id").split ("Tab")[0]);

  if (TargetPage.length > 0) {
    if (TargetPage.is (":visible")) {
      TargetPage.toggle ();
      $("span#MainContent").css ("display", "inline-block");
    } else {
      $("span#MainContent").toggle ();
      TargetPage.css ("display", "inline-block");
    }
  }
});

$("input#MngTool").click (function () {
  var ThisNode = $(this);

  if (!ThisNode.is (":checked")) {
    $("span#ScanServer").css ("display", "none");
    $("span#MainContent").css ("display", "inline-block");
  }
});


