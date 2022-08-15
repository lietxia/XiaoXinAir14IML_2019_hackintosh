
var PROGRESS_INTERVAL = 500;
var PROGRESS_COLOR = '#000080';

var _divFrame;
var _divUploadMessage;
var _divUploadProgress;
var _ifrFile;

var _loopCounter = 1;
var _maxLoop = 10;
var _FileUploadProgressTimer;


function initFileUpload (ClientId, BtnCallback) {
  _divFrame = document.getElementById('UploadFrame');
  _divUploadMessage = document.getElementById('UploadMessage');
  _divUploadProgress = document.getElementById('UploadProgress');
  _ifrFile = document.getElementById('IfrFile');
  
  //
  // Set client id
  //
  var InputId = _ifrFile.contentWindow.document.getElementById('FileUploadId');
  if (ClientId && InputId && (InputId.value != ClientId)) {
    InputId.value = ClientId;
  }
  
  //
  // Set submit button
  //
  var btnUpload = _ifrFile.contentWindow.document.getElementById('FileUploadBtn');
  if (btnUpload) {
    btnUpload.onclick = BtnCallback;
  } else {
    //
    // Submit button is out of form
    //
//    alert ("Initializing upload page failed");
  }
}

function IsInputFileEmpty () {
  var UlFile = _ifrFile.contentWindow.document.getElementById('FileToUpload');
  
  if (UlFile.value.length == 0) {
    _divUploadMessage.innerHTML = '<span style=\"color:#ff0000\">Please specify the file.</span>';
    _divUploadMessage.style.display = '';
    UlFile.focus();
    return true;
  }
  
  return false;
}

function SetFileChecksum (ChecksumStr) {
  var UlChecksum = _ifrFile.contentWindow.document.getElementById('FileChecksum');
  
  if (ChecksumStr && UlChecksum) {
    UlChecksum.value = ChecksumStr;
  }
}

function GetUploadFileObj () {
  return _ifrFile.contentWindow.document.getElementById('FileToUpload');
}

function DoSubmitUploadForm (ActionUrl) {
  var Form;
  
  Form = _ifrFile.contentWindow.document.getElementById('FileUploadForm');
  //
  // After submit form, the action changed, we need to assign a new action.
  //
  if (ActionUrl) {
    Form.action = ActionUrl;
  }
  Form.submit();
}

function SetUploadMsgVisiblility (IsVisible) {
  if (IsVisible) {
    _divUploadMessage.style.display = '';
  } else {
    _divUploadMessage.style.display = 'none';
  }
}

function SetIFrameVisiblility (IsVisible) {
  if (IsVisible) {
    _divFrame.style.display = '';
  } else {
    _divFrame.style.display = 'none';
  }
}

function FileUploadBtnCallback (event) {
  var UlFile = _ifrFile.contentWindow.document.getElementById('FileToUpload');
  var Form;

  //Baisic validation for Photo
  _divUploadMessage.style.display = 'none';

  if (UlFile.value.length == 0) {
    _divUploadMessage.innerHTML = '<span style=\"color:#ff0000\">Please specify the file.</span>';
    _divUploadMessage.style.display = '';
    UlFile.focus();
    return;
  }

//  var regExp = /^(([a-zA-Z]:)|(\\{2}\w+)\$?)(\\(\w[\w].*))(txt|TXT)$/;
  //
  // Validate vice name only
  //
  var regExp = /([^\/]+\.(?:txt|TXT))/;

  if (!regExp.test(UlFile.value)) { //Somehow the expression does not work in Opera
    _divUploadMessage.innerHTML = '<span style=\"color:#ff0000\">Invalid file type. Only supports txt and TXT.</span>';
    _divUploadMessage.style.display = '';
    UlFile.focus();
    return;
  }

  //
  // Present uploading progress
  //
  beginFileUploadProgress();
  //
  // Submit
  //
  Form = _ifrFile.contentWindow.document.getElementById('FileUploadForm');
  Form.submit();
  _divFrame.style.display = 'none';
}

function beginFileUploadProgress () {
  _divUploadProgress.style.display = '';
  clearFileUploadProgress ();
  _FileUploadProgressTimer = setTimeout(updateFileUploadProgress, PROGRESS_INTERVAL);
}

function clearFileUploadProgress () {
  for (var i = 1; i <= _maxLoop; i++) {
      document.getElementById('tdProgress' + i).style.backgroundColor = 'transparent';
  }

  document.getElementById ('tdProgress1').style.backgroundColor = PROGRESS_COLOR;
  _loopCounter = 1;
}

function updateFileUploadProgress () {
  _loopCounter += 1;

  if (_loopCounter <= _maxLoop) {
    document.getElementById ('tdProgress' + _loopCounter).style.backgroundColor = PROGRESS_COLOR;
  } else {
    clearFileUploadProgress ();
  }

  if (_FileUploadProgressTimer) {
    clearTimeout (_FileUploadProgressTimer);
  }

  _FileUploadProgressTimer = setTimeout(updateFileUploadProgress, PROGRESS_INTERVAL);
}

function FileUploadComplete (message, isError) {

  clearFileUploadProgress ();

  if (_FileUploadProgressTimer) {
    clearTimeout (_FileUploadProgressTimer);
  }

  _divUploadProgress.style.display = 'none';
  _divUploadMessage.style.display = 'none';
  _divFrame.style.display = '';

  if (message.length) {
//    var color = (isError) ? '#ff0000' : '#008000';
    var color = (isError) ? 'red' : 'green';

    _divUploadMessage.innerHTML = '<span style=\"color:' + color + '\;font-weight:bold">' + message + '</span>';
    _divUploadMessage.style.display = '';

    /* After form submit, form of iframe would dispear, need to load 
       iframe again or an error occurs */
/*
    if (isError) {
      _ifrFile.contentWindow.document.getElementById('FileToUpload').focus();
    }
*/
  }
}

function AddNewObjToForm (NewObj) {
  NewObj.clone(true).insertAfter($("#IfrFile").contents().find("#HiddenOpts"));
}

function CloneAllOptions () {
  var OptNode = $("#IfrFile").contents().find("#HiddenOpts");
  
  OptNode.empty();
  OptNode.html ($("#PageOption").clone(true));
  OptNode.append ($("#PageUI").clone(true));
  OptNode.append ($("#PageRomList").clone(true));
}

function InitUploadFile () {
  initFileUpload (GetClientId (), FileUploadBtnCallback);
}

