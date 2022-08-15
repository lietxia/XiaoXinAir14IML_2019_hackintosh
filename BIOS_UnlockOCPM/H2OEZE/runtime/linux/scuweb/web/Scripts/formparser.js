
//------------------
// Global variables
//------------------

var EXP_STR_TRUE                = "true";
var EXP_STR_FALSE               = "false";
var EXP_STR_AND                 = "and"; // use "&" in html or xml will be changed to &amp;
var EXP_STR_NOT                 = "!";
var EXP_STR_OR                  = "|";
var EXP_STR_EQUAL               = "=";
var EXP_STR_SUPPRESSIF          = "sif";
var EXP_STR_GRAYOUTIF           = "gif";

var EXP_STR_SIF_TRUE_1          = EXP_STR_SUPPRESSIF + " " + EXP_STR_TRUE;
var EXP_STR_SIF_TRUE_2          = EXP_STR_SUPPRESSIF + " 1 1 " + EXP_STR_EQUAL;
var EXP_STR_GIF_TRUE_1          = EXP_STR_GRAYOUTIF + " " + EXP_STR_TRUE;
var EXP_STR_GIF_TRUE_2          = EXP_STR_GRAYOUTIF + " 1 1 " + EXP_STR_EQUAL;
var EXP_STR_ATTR_EXP            = "exp";
var EXP_STR_ATTR_FORMID         = "fid";
var EXP_STR_ATTR_CALLBACKID     = "cid";
var EXP_STR_ATTR_MINIMUM        = "min";
var EXP_STR_ATTR_MAXIMUM        = "max";
var EXP_STR_ATTR_STEP           = "step";
var EXP_STR_ATTR_DEFAULT        = "dft";
var EXP_STR_ATTR_CURRENT        = "crt";
var EXP_STR_ATTR_VALUE          = "val";
var EXP_STR_ATTR_CHAR_WIDTH     = "cwidth";


jQuery.fn.toggleOption = function( show ) {
  jQuery( this ).toggle( show );
  if( show ) {
    if( jQuery( this ).parent( 'span.toggleOption' ).length )
      jQuery( this ).unwrap( );
  } else {
    if( jQuery( this ).parent( 'span.toggleOption' ).length == 0 )
      jQuery( this ).wrap( '<span class="toggleOption" style="display: none;" />' );
  }
};

//------------------
// Functions
//------------------

function ValidateInputValue (InputObj) {
  var Value = parseInt (InputObj.val());
  var Mininum;
  var Maximum;
  var Step;
  var TextString;

  //
  // Password doesn't have min, max and step attributes
  //
  if ((InputObj.attr(EXP_STR_ATTR_MINIMUM) != undefined) || 
    (InputObj.attr(EXP_STR_ATTR_MAXIMUM) != undefined) ||
    (InputObj.attr(EXP_STR_ATTR_STEP) != undefined)) {
    return;
  }

  Mininum = parseInt (InputObj.attr(EXP_STR_ATTR_MINIMUM));
  Maximum = parseInt (InputObj.attr(EXP_STR_ATTR_MAXIMUM));
  Step = parseInt (InputObj.attr(EXP_STR_ATTR_STEP));
  TextString = InputObj.parent().siblings(".TitleField").text().toString();

  //
  // Obey the minimum and maximum rules
  //
  if (Value <= Mininum) {
    InputObj.val(Mininum);
  } else if (Value >= Maximum) {
    InputObj.val(Maximum);
  } else if (Step > 1) {
    //TODO: Check stepping
    if (((Value - Mininum) % Step) != 0) {
      //
      // Integer number
      //
      Value = Mininum + Step * parseInt ((Value - Mininum) / Step);
      InputObj.val(Value);
    }
  }
}

function ParseHelpString (HelpStr) {
  if (HelpStr.match ('\n')) {
    return HelpStr.replace (/\n/g, '<br />');
  }

  return HelpStr;
}

//
// Parse single condiction like:
// 1=12 32=1,3,4 |
// 1 1 = 3=3 and 7=4 and
// true
//
function ParseExpCondiction (NodeValueArray, Idx, Condictions, ReadOnceObjList) {
  var Pattern;
  var CdnIdx, ValIdx;
  var Result = false;
  var NodeValue = {val: ""};
  var InputNode;
  var ValueList;
  var ResultStack = new Array();
  var ResultLength = ResultStack.length;

  if (Condictions.length == 0) {
    //
    // No condictions, maybe only "sif" or "gif"
    //
    return false;
  }
  for (CdnIdx = 0; CdnIdx < Condictions.length; CdnIdx++) {
    NodeValue.val = "";
    if ((Condictions[CdnIdx].length > 2) && (Condictions[CdnIdx].match ("="))) {
      if (Condictions[CdnIdx][0] == "=") {
        //
        // This coundl be wrong condiction like: =;sif
        //
        alert ("Error: it may parse wrong condiction");
        ResultStack.push (true);
        continue;
      }
      //
      // Read pattern condiction like: e9=5 or 0x45=0x55
      //                               ID=Val    ID=ID
      //
      Pattern = Condictions[CdnIdx].split ("=");

      if (Pattern[0].match ("0x")) {
        if (!GetTwoObjectValue (NodeValueArray, ReadOnceObjList, Pattern, ResultStack)) {
          ResultStack.push (true);
        }
        continue
      }

      if (!GetObjectValue (NodeValueArray, ReadOnceObjList, Pattern[0], NodeValue)) {
        ResultStack.push (true);
        continue;
      }
      //
      // Id and value list: e9=1,2,3,9,0
      //
      ValueList = Pattern[1].split (",");
      if (ValueList.length > 1) {
        ResultLength = ResultStack.length;
        ResultStack.push (false);
        for (ValIdx = 0; ValIdx < ValueList.length; ValIdx++) {
          if (NodeValue.val == ValueList[ValIdx]) {
            ResultStack[ResultStack.length - 1] = true;
            break;
          }
        }
      } else if (NodeValue.val == Pattern[1]) {
        ResultStack.push (true);
      } else {
        ResultStack.push (false);
      }
    } else if (Condictions[CdnIdx] == EXP_STR_AND) {
      if (ResultStack[ResultStack.length - 2] && ResultStack[ResultStack.length - 1]) {
        ResultStack.push (true);
      } else {
        ResultStack.push (false);
      }
      ResultStack.splice (ResultStack.length - 3, 2);
    } else if (Condictions[CdnIdx] == EXP_STR_OR) {
      if (ResultStack[ResultStack.length - 2] || ResultStack[ResultStack.length - 1]) {
        ResultStack.push (true);
      } else {
        ResultStack.push (false);
      }
      ResultStack.splice (ResultStack.length - 3, 2);
    } else if (Condictions[CdnIdx] == EXP_STR_NOT) {
      if (ResultStack[ResultStack.length - 1] == true) {
        ResultStack[ResultStack.length - 1] = false;
      } else {
        ResultStack[ResultStack.length - 1] = true;
      }
    } else if (Condictions[CdnIdx] == EXP_STR_EQUAL) {
      if (ResultStack[ResultStack.length - 2] == ResultStack[ResultStack.length - 1]) {
        ResultStack.push (true);
      } else {
        ResultStack.push (false);
      }
      ResultStack.splice (ResultStack.length - 3, 2);
    } else if (Condictions[CdnIdx] == EXP_STR_TRUE) {
      ResultStack.push (true);
    } else if (Condictions[CdnIdx] == EXP_STR_FALSE) {
      ResultStack.push (false);
    } else {
      //
      // TODO: Add more expressions
      //
//      alert ("Can't parse this kind of expression now");
    }
  } // End of for loop (Condictions)

  if (ResultStack.length == 1) {
    Result = ResultStack[0];
    ResultStack.splice (0, 1);
  } else {
    //
    // NOTE: It could be the error that some opcode doesn't implement
    //
//    alert ("Parsing expression failed (" + ResultStack.length + ")");
  }

  return Result;
}

function SearchAllFormsToGetObjVal (CallbackId, NodeValue) {
  var InputNode;
  //
  // Search all forms to find item with input callbackid
  //
  InputNode = $('div.FormFrame :input[' + EXP_STR_ATTR_CALLBACKID + '="' + CallbackId + '"]');
  //
  // Search this form to find item with input callbackid
  //
  // InputNode = Rows.find (':input[' + EXP_STR_ATTR_CALLBACKID + '="' + CallbackId + '"]');
  if (InputNode.length <= 0) {
    //
    // Can't find matched node to compare value
    //
    return false;
  }
  NodeValue.val = InputNode.val();

  return true;
}

function SearchOnceObjList (ReadOnceObjList, CallbackId, NodeValue) {
  var val = ReadOnceObjList[CallbackId];

  if (val == undefined) {
    return false;
  }
  NodeValue.val = val;

  return true;
}

function GetTwoObjectValue (NodeValueArray, ReadOnceObjList, Pattern, ResultStack) {
  var Id1 = 0, Id2 = 0;
  var Value1, Value2;
  var NodeValue = {val: ""};

  Id1 = Pattern[0].split ("0x")[1];
  Id2 = Pattern[1].split ("0x")[1];

  if (!GetObjectValue (NodeValueArray, ReadOnceObjList, Id1, NodeValue)) {
    return false;
  }
  Value1 = NodeValue.val;

  if (!GetObjectValue (NodeValueArray, ReadOnceObjList, Id2, NodeValue)) {
    return false;
  }
  Value2 = NodeValue.val;

  if (Value1 == Value2) {
    ResultStack.push (true);
  } else {
    ResultStack.push (false);
  }

  return true;
}

function GetValueFromNodeArray (NodesArray, CallbackId, RtnObj) {
  var Idx;

  for (Idx = 0; Idx < NodesArray.length; Idx++) {
    if (NodesArray[Idx].cid == 0) {
      continue;
    }
    if (NodesArray[Idx].cid == CallbackId) {
      RtnObj.val = NodesArray[Idx].val;
      return true;
    }
  }

  return false;
}

function GetObjectValue (NodesArray, ReadOnceObjList, CallbackId, NodeValue) {

  do {
    if (SearchOnceObjList (ReadOnceObjList, CallbackId, NodeValue)) {
      break;
    }
    if (GetValueFromNodeArray (NodesArray, CallbackId, NodeValue)) {
    // if (GetValueFromRows (Rows, CallbackId, NodeValue)) {
      ReadOnceObjList[CallbackId] = NodeValue.val;
      break;
    }
    if (SearchAllFormsToGetObjVal (CallbackId, NodeValue)) {
      ReadOnceObjList[CallbackId] = NodeValue.val;
      break;
    }
    return false;
  } while (0);

  return true;
}

function FetchInitRowInfo (FetchArray, RowList) {
  var Idx;
  var RowObj;

  for (Idx = 0; Idx < RowList.length; Idx++) {
    RowObj = $(RowList[Idx]);
    if (RowObj.attr("cid") != undefined) {
      FetchArray.push ({cid: RowObj.attr("cid"), val: RowObj.attr("value"), exps: RowObj.attr("exp")});
    } else {
      FetchArray.push ({cid: 0, val: 0, exps: RowObj.attr("exp")});
    }
  }
}

function GetRowInfoHash (Rows, Idx) {
  var RowObj;
  var RowHash;

  RowObj = $(Rows[Idx]);
  if (RowObj.attr("cid") != undefined) {
    RowHash = {cid: RowObj.attr("cid"), val: RowObj.attr("value"), exps: RowObj.attr("exp")};
  } else {
    RowHash = {cid: 0, val: 0, exps: RowObj.attr("exp")};
  }

  return RowHash;
}

function GetValueFromRows (Rows, CallbackId, RtnObj) {
  var Idx;
  var RowObj;

  RowObj = Rows.find ('[cid=' + CallbackId +']');
  if (RowObj.length > 0) {
    RtnObj.val = RowObj.val();
    return true;
  }

  return false;
}

function ParseExpression (OperationAry, NodeValueArray, RowIdx, ReadOnceObjList, ExprStr) {
  var Expsns;
  var ExpIdx;
  var IsSuppress = false;
  var IsGrayout = false;
  var DoOperation;
  var Condictions;

  Expsns = ExprStr.split (";");
  for (ExpIdx = 0; ExpIdx < Expsns.length; ExpIdx++) {
    if (OperationAry[0].suppress == true) {
      //
      // If this row is doing suppress, it's not nessasary to
      // parse other expressions
      // It happens after parsing suppressif (not "sif true" or "sif 1 1 =")
      //
      break;
    }
    if (OperationAry[0].grayout == true) {
      //
      // Same grayout-if is found, but it's already do grayout,
      // continue to parse next expression
      //
      continue;
    }
    if (Expsns[ExpIdx].match (EXP_STR_GIF_TRUE_1) ||
      Expsns[ExpIdx].match (EXP_STR_GIF_TRUE_2)) {
      OperationAry[0].grayout = true;
      continue;
    }
    Condictions = Expsns[ExpIdx].split (" ");
    DoOperation = Condictions.splice (0, 1);
    if (DoOperation == EXP_STR_SUPPRESSIF) {
      IsSuppress = true;
      IsGrayout = false;
    } else if (DoOperation == EXP_STR_GRAYOUTIF) {
      IsGrayout = true;
      IsSuppress = false;
    }
    Result = ParseExpCondiction (NodeValueArray, RowIdx, Condictions, ReadOnceObjList);
    if (Result == true) {
      if (IsSuppress) {
        OperationAry[0].suppress = true;
      } else if (IsGrayout) {
        OperationAry[0].grayout = true;
      }
    }
  } // End of for loop (Expressions)
}

function ControlFormRow (FormFrame) {
  var Rows;
  var Expsns;
  var Condictions;
  var IsSuppress = false;
  var IsGrayout = false;
  var DoSuppress = false;
  var DoGrayout = false;
  var RowNode, SubNode;
  var RowIdx, ExpIdx, SubIdx;
  var NodeValueArray = new Array (); // TODO: replace it by hashmap
  var SubNodeValArr = new Array (); // TODO: replace it by hashmap
  var RowInfo;
  var Result = false;
  var DoOperation;
  var ReadOnceObjList = new Object (); // or var map = {}; // This is a hash map
  var OperationAry = new Array ();

  OperationAry.push ({suppress: false, grayout: false});

  Rows = FormFrame.children('div.Row[' + EXP_STR_ATTR_EXP + ']');
  FetchInitRowInfo (NodeValueArray, Rows);
  if (NodeValueArray.length != Rows.length) {
    alert ("Error: different size between memory and rows");
    return;
  }

  for (RowIdx = 0; RowIdx < Rows.length; RowIdx++) {
    RowInfo = GetRowInfoHash (Rows, RowIdx);
    RowNode = $(Rows[RowIdx]);
    //
    // Check if this attribute is empty
    //
    if ((RowInfo.exps == "") || (RowInfo.exps == " ")) {
      //
      // Do-suppress if found break this loop to do suppress, it doesn't
      // need to parse other expression
      //
      continue;
    }
    if (RowInfo.exps.match (EXP_STR_SIF_TRUE_1) || RowInfo.exps.match (EXP_STR_SIF_TRUE_2)) {
      RowNode.css ("display", "none");
      //-[start-121225-IB10500006-add]
      //
      // All input tag with "sif true" expression must set to disable, or there are
      // dupicate item will make this item a wrong value when submit data
      //
      RowNode.find(':input').attr('disabled', true);
      RowNode.find(':input').addClass("NoSend");
      //-[end-121225-IB10500006-add]
      continue;
    }
    //
    // Start parsing expressions
    //
    OperationAry[0].suppress = false;
    OperationAry[0].grayout = false;
    ParseExpression (OperationAry, NodeValueArray, RowIdx, ReadOnceObjList, RowInfo.exps);

    if (OperationAry[0].suppress == true) {
      RowNode.css ("display", "none");
      continue;
    } else {
      RowNode.css ("display", "");
    }
    //
    // Because all :input objects are readonly when initializing
    // If expression has no gif or gif is false, set :input object is not readonly
    //
    SubNode = RowNode.find(':input');
    if (OperationAry[0].grayout == true) {
      SubNode.attr('disabled', true);
    } else {
      SubNode.removeAttr("disabled");
      // jQuery 1.9 use prop() not attr()
      SubNode = SubNode.find("option[exp!='']");
      if (SubNode.length > 0) {
        for (SubIdx = 0; SubIdx < SubNode.length; SubIdx++) {
          SubNodeValArr.push ({cid: 0, val: $(SubNode[SubIdx]).attr("value"), exps: $(SubNode[SubIdx]).attr("exp")});
          OperationAry[0].suppress = false;
          OperationAry[0].grayout = false;
          ParseExpression (OperationAry, SubNodeValArr, SubIdx, ReadOnceObjList, SubNodeValArr[SubIdx].exps);
          if (OperationAry[0].suppress) {
            $(SubNode[SubIdx]).toggleOption(false);
            // $(SubNode[SubIdx]).css("display", "none");
          } else {
            $(SubNode[SubIdx]).toggleOption(true);
            // $(SubNode[SubIdx]).css("display", "");
          }
        }
      }
    }
  } // End of for loop (All rows)
}
