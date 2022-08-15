// JavaScript Document

function GetHttpDoc (Doc) {
  var HttpDoc;

  if (document.implementation && document.implementation.createDocument) {
    HttpDoc = document.implementation.createDocument("", "", null);
    HttpDoc.async = false;
      
    try {
      //
      // Firefox, Mozilla, Opera, etc.
      //
      HttpDoc.loadXMLDoc(Doc);
    } catch (e) {
      //
      // Google chrome
      //
      try {
        var xmlhttp = new XMLHttpRequest();
        
        xmlhttp.open("GET", Doc, false);
        xmlhttp.send(null);
//          xmlhttp.send("");
//          xmlhttp.send();
        HttpDoc = xmlhttp.responseXML.documentElement;
      } catch (err) {
　　     alert (err);
      }
    }
  } else if (typeof window.ActiveXObject != 'undefined') {
    //
    // Internet Explorer
    //
    try {
      HttpDoc = new ActiveXObject('Msxml2.DOMDocument');
  　　 HttpDoc.async = false;
  　　 HttpDoc.load(Doc); 
　　 } catch (e) {
　　   alert (e);
　　 }
  }
  
  return HttpDoc;
}

function XsltTransform () {
  var isSuccess = true;
  var xml;
  var xslt;
  var outputDiv = document.getElementById("Output");
  var processor;
  var XmlDom;
  var serializer;
  var output;
  
  xml = GetHttpDoc ("BiosSetupInfo.xml");
  xslt = GetHttpDoc ("setup.xslt");

  if (document.implementation && document.implementation.createDocument) {
    processor = new XSLTProcessor();
    processor.importStylesheet(xslt);

    //
    // Method 1
    //
    XmlDom = processor.transformToFragment(xml, document);
    document.getElementById("Output").appendChild(XmlDom);

    //
    // Method 2
    //
//      XmlDom = processor.transformToDocument(xml);
//      serializer = new XMLSerializer(); 
//      output = serializer.serializeToString(XmlDom.documentElement);
//      outputDiv = document.getElementById("Output");
//      outputDiv.innerHTML = output;

  } else if (typeof window.ActiveXObject != 'undefined') {
  　outputDiv.innerHTML = xml.documentElement.transformNode(xslt); 
  } else {
    isSuccess = false;
  }
  
  return isSuccess;
}

