
var PROGRESS_INTERVAL = 500;
var PROGRESS_COLOR = '#000080';

var _divFrame;
var _divUploadMessage;
var _divUploadProgress;
var _ifrFile;

var _loopCounter = 1;
var _maxLoop = 10;
var _FileUploadProgressTimer;
var _baseFormAction;
var _FileUploadedCallback = null;

//function InitUploadFile () {
//  $("body").on ("onload", "#ifrFile", initFileUpload);
//}

function initFileUpload (ActionUrl, ClientId) {
  _divFrame = document.getElementById('UploadFrame');
  _divUploadMessage = document.getElementById('UploadMessage');
  _divUploadProgress = document.getElementById('UploadProgress');
  _ifrFile = document.getElementById('ifrFile');
//  _baseFormAction = _ifrFile.contentWindow.document.getElementById('FileUploadForm').action;
  _baseFormAction = ActionUrl;
  
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
  btnUpload.onclick = function(event) {
    var UlFile = _ifrFile.contentWindow.document.getElementById('FileToUpload');
    var Form;

    //Baisic validation for Photo
    _divUploadMessage.style.display = 'none';

    if (UlFile.value.length == 0) {
      _divUploadMessage.innerHTML = '<span style=\"color:#ff0000\">Please specify the file.</span>';
      _divUploadMessage.style.display = '';
//      document.getElementById('UpdateMethodForm').submit();
      UlFile.focus();
      return;
    }

    var regExp = /^(([a-zA-Z]:)|(\\{2}\w+)\$?)(\\(\w[\w].*))(.txt|.TXT)$/;

    if (!regExp.test(UlFile.value)) //Somehow the expression does not work in Opera
    {
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
    Form.action = _baseFormAction;
    Form.submit();
    _divFrame.style.display = 'none';
  }
}

function beginFileUploadProgress () {
    _divUploadProgress.style.display = '';
    clearFileUploadProgress ();
    _FileUploadProgressTimer = setTimeout(updateFileUploadProgress, PROGRESS_INTERVAL);
}

function clearFileUploadProgress () {
    for (var i = 1; i <= _maxLoop; i++)
    {
        document.getElementById('tdProgress' + i).style.backgroundColor = 'transparent';
    }

    document.getElementById ('tdProgress1').style.backgroundColor = PROGRESS_COLOR;
    _loopCounter = 1;
}

function updateFileUploadProgress () {
    _loopCounter += 1;

    if (_loopCounter <= _maxLoop)
    {
        document.getElementById ('tdProgress' + _loopCounter).style.backgroundColor = PROGRESS_COLOR;
    }
    else 
    {
        clearFileUploadProgress ();
    }

    if (_FileUploadProgressTimer)
    {
        clearTimeout (_FileUploadProgressTimer);
    }

    _FileUploadProgressTimer = setTimeout(updateFileUploadProgress, PROGRESS_INTERVAL);
}

function FileUploadComplete (message, isError) {
    if (_FileUploadedCallback) {
      _FileUploadedCallback (message, isError);
      _FileUploadedCallback = null;
      return;
    }

    clearFileUploadProgress ();

    if (_FileUploadProgressTimer) {
        clearTimeout (_FileUploadProgressTimer);
    }

    _divUploadProgress.style.display = 'none';
    _divUploadMessage.style.display = 'none';
    _divFrame.style.display = '';

    if (message.length) {
        var color = (isError) ? '#ff0000' : '#008000';

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
    document.getElementById('UpdateMethodForm').submit();
}

function FileUploadToSpecificServer (ServerUrl, Callback) {
  var Form = _ifrFile.contentWindow.document.getElementById('FileUploadForm');
  
  _FileUploadedCallback = Callback;
  Form.action = ServerUrl;
  Form.submit();
//  _divFrame.style.display = 'none';
}

function InitUploadFile (FileType, FunCB) {
  switch (FileType) {
  case 0:
    initFileUpload ("Actions/Upload.cgi", GetClientId ());
    break;
  case 1:
    if (FunCB) {
      FunCB();
    }
    initFileUpload ("Actions/FwUpdate.cgi", GetClientId ());
    break;
  default:
    break;
  }
}


