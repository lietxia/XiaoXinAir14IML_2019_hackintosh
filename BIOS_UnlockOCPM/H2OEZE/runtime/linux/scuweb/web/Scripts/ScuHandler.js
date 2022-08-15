pySaveScuData = function(FunNum, Data)
{
	w = Ti.UI.getCurrentWindow();
  if (0 == w.objEzh2oIf.GetChildWin())
    return w.objEzh2oIf.GenDefaultScuConfiguration(FunNum, Data)
  else
	  return w.objEzh2oIf.UpdateRuntimeBiosScuConfiguration(FunNum, Data);
}

pyExitScuCtrl = function(IsReboot)
{
	w = Ti.UI.getCurrentWindow();
	if (IsReboot)
		w.objEzh2oIf.Reboot();
	w.close();
}

function ShowParenet()
{
  w = Ti.UI.getCurrentWindow();
  p = w.getParent();
  p.show();
}

function DisableParent()
{
  w = Ti.UI.getCurrentWindow();
  p = w.getParent();
  p.hide();
  w.addEventListener('close', ShowParenet);
}
