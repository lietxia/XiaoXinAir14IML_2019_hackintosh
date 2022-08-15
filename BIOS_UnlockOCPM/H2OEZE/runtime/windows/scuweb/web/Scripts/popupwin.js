

var POPUP_WIN_BTN_OK         = 1
var POPUP_WIN_BTN_STOP       = 2
var POPUP_WIN_BTN_YES        = 3
var POPUP_WIN_BTN_NO         = 4


//------------------
// Functions
//------------------
function PopupLoading (Msg, ShowStopBtn) {
  $("#PopupWin").css("display", "");
  $("#PopupTitle").html("Loading...");
  $("#LoadingImg").css("display", "");
  $("#PopupCont").html(Msg);
  $("#ProgressBar").css("display", "none");
  $("#PopupCtrl button").css("display", "none");
  if (ShowStopBtn) {
    $("#PopupCtrl").css("display", "");
    $("#PopupCtrl button[name='stop']").css("display", "");
  } else {
    $("#PopupCtrl").css("display", "none");
  }
}

function PopupInfo (Title, Msg) {
  $("#PopupWin").css("display", "");
  $("#PopupTitle").html(Title);
  $("#LoadingImg").css("display", "none");
  if (Msg) {
    $("#PopupCont").html (Msg);
  } else {
    $("#PopupCont").html (Title);
//    $("#PopupCont").empty ();
  }
  $("#PopupCtrl button").css("display", "none");
}

function ClosePopup () {
  $("#PopupWin").css("display", "none");
}

function IsPopupWinWorking () {
  var IsWorking = false;

  try {
    IsWorking = $("#PopupWin").is (':visible');
  } catch (e) {
    IsWorking = false;
  }

  return IsWorking;
}

function SetPopupTitle (Msg) {
  $("#PopupTitle").html (Msg);
}

function SetPopupContent (Msg) {
  $("#PopupCont").html (Msg);
}

function SetOkBtnAndContent (Msg, CfmBtnCallback) {
  var BtnOk = $("#PopupCtrl button[name='ok']");

  $("#LoadingImg").css("display", "none");
  $("#PopupCont").html(Msg);
  $("#PopupCtrl").css("display", "");
  BtnOk.css("display", "").unbind("click").click(CfmBtnCallback);
  BtnOk.siblings().css("display", "none");
}

function SetCtrlButtons (BtnType, BtnCallBack) {
  var PopupCtrl = $("#PopupCtrl");
  var BtnObj;

  PopupCtrl.css("display", "");

  switch (BtnType) {
  case POPUP_WIN_BTN_OK:
    BtnObj = PopupCtrl.find ("button[name='ok']");
    BtnObj.siblings().css("display", "none");
    BtnObj.css("display", "");
    BtnObj.unbind("click");
    BtnObj.click (BtnCallBack);
    break;

  case POPUP_WIN_BTN_STOP:
    BtnObj = PopupCtrl.find ("button[name='stop']");
    BtnObj.siblings().css("display", "none");
    BtnObj.css("display", "");
    BtnObj.unbind("click");
    BtnObj.click (BtnCallBack);
    break;

  case POPUP_WIN_BTN_YES:
    BtnObj = PopupCtrl.find ("button[name='yes']");
    BtnObj.siblings("button[name='ok']").css("display", "none");
    BtnObj.siblings("button[name='stop']").css("display", "none");
    BtnObj.css("display", "");
    BtnObj.unbind("click");
    BtnObj.click (BtnCallBack);
    break;

  case POPUP_WIN_BTN_NO:
    BtnObj = PopupCtrl.find ("button[name='no']");
    BtnObj.css("display", "");
    BtnObj.unbind("click");
    BtnObj.click (BtnCallBack);
    break;
  }
}

function EnableCtrlBtn (IsTrue) {
  if (IsTrue) {
    $("#PopupCtrl").css("display", "");
  } else {
    $("#PopupCtrl").css("display", "none");
  }
}

/* Pop-up window ver1.0 with close button */
function SetCloseBtnAndContent (Msg, CloseBtnCallback) {
  $("#LoadingImg").css("display", "none");
  $("#PopupCont").html(Msg);
  $("#PopupCloseBtn").css("display", "").unbind("click").click(CloseBtnCallback);
}

function SetYesNoBtnAndContent (Msg, YesBtnCallback, NoBtnCallback) {
  var PopupCtrl = $("#PopupCtrl");
  var BtnObj;

  if (Msg) {
    $("#PopupCont").html(Msg);
  }
  PopupCtrl.find ("button").css ("display", "none");
  PopupCtrl.css("display", "");

  BtnObj = PopupCtrl.find ("button[name='yes']");
  BtnObj.css("display", "");
  BtnObj.unbind("click");
  BtnObj.click (YesBtnCallback);

  BtnObj = PopupCtrl.find ("button[name='no']");
  BtnObj.css("display", "");
  BtnObj.unbind("click");
  BtnObj.click (NoBtnCallback);
}

function SetStopBtnAndContent (Msg, StopBtnCallback) {
  var PopupCtrl = $("#PopupCtrl");
  var StopBtn;

  if (Msg) {
    $("#PopupCont").html(Msg);
  }
  PopupCtrl.find ("button").css ("display", "none");
  PopupCtrl.css("display", "");

  StopBtn = PopupCtrl.find ("button[name='stop']");
  StopBtn.css("display", "");
  StopBtn.unbind("click");
  StopBtn.click (StopBtnCallback);
}

/*
 * version 1.1
 */
var POPUP_PROGRESS_INTERVAL = 500;
var POPUP_PROGRESS_COLOR = "#000080";
var POPUP_MAX_LOOP = 10;

var gPopupProgressLoopCount = 1;
var gPopupProgressTimer;

function ClearPopupProgress () {
  for (var i = 1; i <= POPUP_MAX_LOOP; i++) {
    if (i != 1) {
      $("#tdPopupProgress" + i).css ("background-color", "transparent");
    } else {
      $("#tdPopupProgress" + i).css ("background-color", POPUP_PROGRESS_COLOR);
    }
  }
  gPopupProgressLoopCount = 1;
}

function RunPopupProgress () {
  gPopupProgressLoopCount += 1;

  if (gPopupProgressLoopCount <= POPUP_MAX_LOOP) {
    $("#tdPopupProgress" + gPopupProgressLoopCount).css ("background-color", POPUP_PROGRESS_COLOR);
  } else {
    ClearPopupProgress ();
  }

  if (gPopupProgressTimer) {
    clearTimeout (gPopupProgressTimer);
  }

  gPopupProgressTimer = setTimeout (RunPopupProgress, POPUP_PROGRESS_INTERVAL);
}

function EnablePopupProgress (Enable) {
  if (Enable) {
    $("#LoadingImg").css ("display", "none");
    $("#ProgressBar").css ("display", "");
    ClearPopupProgress ();
    gPopupProgressTimer = setTimeout (RunPopupProgress, POPUP_PROGRESS_INTERVAL);
  } else {
    $("#ProgressBar").css ("display", "none");
    ClearPopupProgress ();
    if (gPopupProgressTimer) {
      clearTimeout (gPopupProgressTimer);
    }
  }
}






