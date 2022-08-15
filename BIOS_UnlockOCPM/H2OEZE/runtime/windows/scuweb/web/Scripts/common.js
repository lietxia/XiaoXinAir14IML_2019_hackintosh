jQuery.support.cors = true;

//------------------
// Global Constants
//------------------
var AUTO_CHECK_CONN_INTERVAL      = 12000; // 12 seconds
var CHECK_CONN_URL                = 'Actions/TestConn.cgi';
var CHECK_CONN_TIMEOUT            = 5000;
var TREE_TGT_NODE_COLOR           = "#6633CC";
var TREE_TGT_NODE_HOVER_COLOR     = "#6633CC";


//------------------
// Global variables
//------------------
var gIsConnectionClosed = false;


//------------------
// Functions
//------------------

function ParseTxtNewLineToHtmlBr (TxtStr) {
  if (TxtStr.match ('\n')) {
    return TxtStr.replace (/\n/g, '<br />');
  }

  return TxtStr;
}

function FillNumberWithZero (Node) {
  if (parseInt (Node) > 9) {
    return Node.toString ();
  } else {
    return ("0" + Node.toString ());
  }
}

function hasClass(element, clz) {
  var clzs = element.className;

  if(!clzs) {
      return false;
  }
  if(clzs === clz) {
      return true;
  }
  return clzs.search('\\b' + clz + '\\b') !== -1;
}

function addClass(element, clz) {
  if(!hasClass(element, clz)) {
    if(element.className) {
        clz = ' ' + clz;
    }
    element.className += clz;
  }
}

function removeClass(element, clz) {
  element.className = element.className.replace(
    new RegExp('\\b' + clz + '\\b\\s*', 'g'), '');
}

function CheckConnection () {

  $.ajax({
    cache: false,
    url: CHECK_CONN_URL,
    async: false,
    timeout: CHECK_CONN_TIMEOUT,
    error: function(xhr) {
      if (gIsConnectionClosed == false) {
        alert ("Disconnected...");
        gIsConnectionClosed = true;
      }
    },
    success: function(response) {
      if (gIsConnectionClosed == true) {
        if (IsPopupWinWorking ()) {
          alert ("Reconnected! Reload to get latest information");
        } else {
          alert ("Reconnected!");
          //
          // Fetch document from server
          //
          window.location.reload (true);
        }
        gIsConnectionClosed = false;
      }
    }
  });

  return gIsConnectionClosed;
}

function AutoCheckConnection () {
  setInterval (CheckConnection, AUTO_CHECK_CONN_INTERVAL);
}

function PrintServerResult (AddrObj, RespStatus, IsSuccess) {
  var MsgObj = AddrObj.msgobj;
  var FontColor = (IsSuccess) ? "green" : "red";

//  MsgObj.append ("<span style='color: #000080'>[" + AddrObj.ip + ":" + AddrObj.port + "]</span> ");
//  MsgObj.append ("<span style='color: " + FontColor + "'>" + RespStatus + "</span><br />");
  MsgObj.html (MsgObj.html () + "<span style='color: #000080'>[" + AddrObj.ip + ":" + AddrObj.port + "]</span> ");
  MsgObj.html (MsgObj.html () + "<span style='color: " + FontColor + "'>" + RespStatus + "</span><br />");
}

//------------------
// Platform information
//------------------
function GetPlatformInfo (IsPureInfo, OpInfoCallback) {
  var InfoUrl = "../Actions/TestConn.cgi";

  if (IsPureInfo) {
    InfoUrl += "?t=1";
  }

  $.ajax({
    cache: false,
    url: InfoUrl,
    async: false,
    timeout: CHECK_CONN_TIMEOUT,
    complete: function (jqXHR, textStatus) {
      if (textStatus == "success") {
        var Data = $.parseJSON (jqXHR.responseText);

        OpInfoCallback (Data);
      }
    }
  });

}


//------------------
// Checksum
//------------------

//
// It's a application of HTML5 API and jquery may not support this feature
//
function GenLocalFileChecksum (
  TargetObj, ProgressCallback, SuccessCallback, ErrorCallback, CompleteCallback) {

  if (!TargetObj) {
    alert ("Error! Empty target ID!");
    return;
  }

//  var FileObj = document.getElementById (TargetId).files[0];
  var FileObj = TargetObj.files[0];
  var Reader = new FileReader ();

  // Set event handler
  // onloadstart 	ProgressEvent 	When the read starts.
  // onprogress 	ProgressEvent 	While reading (and decoding) blob, and reporting partial Blob data (progess.loaded/progress.total)
  // onabort 	    ProgressEvent 	When the read has been aborted. For instance, by invoking the abort() method.
  // onerror 	    ProgressEvent 	When the read has failed (see errors).
  // onload 	    ProgressEvent 	When the read has successfully completed.
  // onloadend 	  ProgressEvent 	When the request has completed (either in success or failure).   Reader.onprogress = function (evt) {
  //
  if (ProgressCallback) {
    Reader.onprogress = function (evt) {
      if (evt.lengthComputable) {
        var per = Math.round ((evt.loaded * 100) / evt.total) ;

        ProgressCallback (per);
      }
    };
  }
  if (SuccessCallback && ErrorCallback) {
    Reader.onload = function (evt) {
      try {
        var Md5Str = calcMD5 (evt.target.result);

        SuccessCallback (Md5Str);
      } catch (e) {
        ErrorCallback (e.message);
      }
    };
  }
  if (ErrorCallback) {
    Reader.onerror = function (evt) {
      ErrorCallback ("Read file failed");
    };
  }
  if (CompleteCallback) {
    Reader.onloadend = CompleteCallback;
  }

  //
  // Do read file
  //
  Reader.readAsBinaryString (FileObj);
}

function ReadAjaxHttpData (HttpUrl) {
  var RtnData = null;

  $.ajax({
    cache: false,
    url: HttpUrl,
    async: false,
//    dataType: "json",
    success: function (data, textStatus, jqXHR) {
      RtnData = data;
    }
  });

  return RtnData;
}

function SendAjaxHttpData (HttpUrl, PostData) {
  var RtnData = null;

  $.ajax({
    cache: false,
    url: HttpUrl,
    async: false,
    type: "POST",
    data: PostData,
    dataType: "json",
    complete: function (jqXHR, textStatus) {
      if (textStatus == "success") {
        RtnData = $.parseJSON (jqXHR.responseText);
      } else if (textStatus == "parsererror") {
        RtnData = jqXHR.responseText;
      } else {
        alert (textStatus);
      }
    }
  });

  return RtnData;
}

function SavePostDataToTempFile (FileName) {
  var ScuData;
  var ServerAddrsData;
  var PostData;
  var ClientId;
  var RtnInfo;
  var UrlLink;

  ClientId = GetClientId ();

  $('#DataForm').find(':input').removeAttr("disabled");
  ScuData = $('#DataForm').serialize();
  ServerAddrsData = $('#RemoteCtrlForm').serialize();

  PostData = "1::" + ClientId + "::" + ScuData + "::" + ServerAddrsData;

  if (FileName) {
    UrlLink = "../Actions/SaveClientData.cgi?fn=" + FileName;
  } else {
    UrlLink = "../Actions/SaveClientData.cgi";
  }
  RtnInfo = SendAjaxHttpData (UrlLink, PostData, 60);

  return RtnInfo;
}

function LoadPostDataFromTempFile (FileName) {
  var PostData;
  var ServerInfo;
  var CookieName;
  var ClientId;
  var UrlLink;

  ClientId = GetClientId ();
  PostData = "2::" + ClientId;
  if (FileName) {
    UrlLink = "../Actions/SaveClientData.cgi?fn=" + FileName;
  } else {
    UrlLink = "../Actions/SaveClientData.cgi";
  }
  PostData = SendAjaxHttpData (UrlLink, PostData, 60);

  return PostData;
}

$("input[func='out']").click (function () {
  var ThisNode = $(this);

  window.location = ThisNode.attr ("id") + ".html";
});
