#====================================================
#        Cycle - calendar for women
#        Distributed under GNU Public License
# Original author: Oleg S. Gints
# Maintainer: Matt Molyneaux (moggers87+git@moggers87.co.uk)
# Home page: http://moggers.co.uk/cgit/cycle.git/about
#===================================================    
import os, sys, gettext
import locale

import wxversion 
wxversion.ensureMinimal('2.5.3')
import wx
import wx.html
import wx.lib.colourdb

from cal_year import *
from save_load import *
from dialogs import *
from set_dir import *

import gettext
import __builtin__
lang_find = False
if not '__WXMSW__' in wx.PlatformInfo:
    for lang_env_var in ('LANGUAGE', 'LC_ALL', 'LC_CTYPE', 'LANG'):
        if os.environ.has_key(lang_env_var):
            env_language = os.environ[lang_env_var]
            for s_lang in env_language.split(':'): # if set more languages
                os.environ[lang_env_var] = s_lang
                try:
                    dl = locale.getdefaultlocale()
                    lang = [dl[0][0:2]]
                    l = gettext.translation('cycle', msg_dir, lang)
                    if wx.USE_UNICODE:
                        __builtin__.__dict__['_'] = lambda s: l.ugettext(s)
                    else:
                        __builtin__.__dict__['_'] = lambda s: l.ugettext(s).encode(dl[1])
                    _('try decode this string')
                    lang_find = True
                    break #language was found
                except:
                    pass
        if lang_find:
            break
else: #for MS Windows
    try:
        dl = locale.getdefaultlocale()
        lang = [ dl[0][0:2] ]
        l = gettext.translation('cycle', msg_dir, lang)
        if wx.USE_UNICODE:
            __builtin__.__dict__['_'] = lambda s: l.ugettext(s)
        else:
            __builtin__.__dict__['_'] = lambda s: l.ugettext(s).encode(dl[1])
        _('try decode this string')
        lang_find = True
    except:
        pass

if not lang_find:
    __builtin__.__dict__['_'] = lambda s: s
    lang = [""]

class MyFrame(wx.Frame):
    """Main window"""
    def __init__(self, parent, ID, title):
        wx.Frame.__init__(self, parent, ID, title,
                       wx.DefaultPosition, wx.Size(800, 600))

        wx.Image_AddHandler(wx.PNGHandler())
        self.printer = wx.html.HtmlEasyPrinting()
        icon = wx.Icon(os.path.join(icons_dir, 'mini/cycle.xpm'), wx.BITMAP_TYPE_XPM)
        self.SetIcon(icon)

        Val.frame = self
        self.CreateStatusBar()
        self.MakeToolMenu()  # toolbar
        
        self.cal = Cal_Year(self)
        self.OnCurrent(self)
        wx.EVT_CLOSE(self, self.OnCloseWindow)

    def OnCloseWindow(self, event):
        Save_Cycle(cycle.name, cycle.passwd, cycle.file)
        self.Destroy()

    def TimeToQuit(self, event):
        self.Close(True)

    def MakeToolMenu(self):
        toolbar = self.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER)
        toolbar.SetToolBitmapSize(wx.Size(24, 24))

        SetToolPath(self, toolbar, 10, os.path.join(bitmaps_dir, 'dec.png'), _('Dec Year'))
        wx.EVT_TOOL(self, 10, self.OnDecYear)

        SetToolPath(self, toolbar, 20, os.path.join(bitmaps_dir, 'curr.png'), _('Current Year'))
        wx.EVT_TOOL(self, 20, self.OnCurrent)

        SetToolPath(self, toolbar, 30, os.path.join(bitmaps_dir, 'inc.png'), _('Inc Year'))
        wx.EVT_TOOL(self, 30, self.OnIncYear)

        toolbar.SetToolSeparation(50)
        toolbar.AddSeparator()

        SetToolPath(self, toolbar, 40, os.path.join(bitmaps_dir, 'legend.png'), _('Legend'))
        wx.EVT_TOOL(self, 40, self.Legend)
        
        SetToolPath(self, toolbar, 45, os.path.join(bitmaps_dir, 'export.png'), _('Export to iCal'))
        wx.EVT_TOOL(self, 45, self.Export)
        
        SetToolPath(self, toolbar, 50, os.path.join(bitmaps_dir, 'set.png'), _('Settings'))
        wx.EVT_TOOL(self, 50, self.Settings)
        
        SetToolPath(self, toolbar, 55, os.path.join(bitmaps_dir, 'help.png'), _('Help'))
        wx.EVT_TOOL(self, 55, self.Info)

        SetToolPath(self, toolbar, 57, os.path.join(bitmaps_dir, 'print.png'), _('Print'))
        wx.EVT_TOOL(self, 57, self.test)

        toolbar.AddSeparator()

        SetToolPath(self, toolbar, 60, os.path.join(bitmaps_dir, 'exit.png'), _('Exit'))
        wx.EVT_TOOL(self, 60, self.TimeToQuit)

        toolbar.Realize()

    def test(self, event):
        rpt = report_year(self.cal.year)
        self.printer.PreviewText(rpt)
        #dlg = Colours_Dlg(self)
        #dlg.ShowModal()
        #dlg.Destroy()

    def Legend(self, event):
        dlg = Legend_Dlg(self)
        dlg.ShowModal()
        dlg.Destroy()

    def Export(self, event):
        dlg = wx.FileDialog(self, _("Export to iCal"),
                            style = wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            try:
                fileobj = file(dlg.GetPath(), "w")
                report_year_ical(self.cal.year, fileobj)
            except (IOError, OSError), err:
                wx.MessageDialog(
                    self, str(err), _("Unable to export"), style=wx.OK).ShowModal()
        
    def Settings(self, event):
        dlg = Settings_Dlg(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.cal.Set_Year(wx.DateTime_Today().GetYear())
        dlg.Destroy()

    def Info(self, event):
        global lang
        f_name = os.path.join(doc_dir, "README_" + lang[0] + ".html")
        if not os.path.isfile(f_name):
            f_name = os.path.join(doc_dir, "README.html")
        f = open(f_name, "r")
        msg = f.read()
        dlg = Help_Dlg(self, _('Help'), msg)
        dlg.ShowModal()

    # increment and decrement toolbar controls
    def OnIncYear(self, event):
        self.cal.Inc_Year()

    def OnDecYear(self, event):
        self.cal.Dec_Year()

    def OnCurrent(self, event):
        self.cal.Set_Year(wx.DateTime_Today().GetYear())

def SetToolPath(self, toolbar, id, bmp, title):
    global dir_path
    toolbar.AddSimpleTool(id, wx.Bitmap(os.path.join(dir_path, bmp), wx.BITMAP_TYPE_PNG),
                     title, title)

class MyApp(wx.App):
    """Show login screen, first login etc."""
    def OnInit(self):
        wx.lib.colourdb.updateColourDB()
        ret = first_login()
        if ret == 'bad_login':
            return True
        elif ret == 'not_first':
            dlg = Login_Dlg(None)
            if dlg.ShowModal() == wx.ID_CANCEL:
                dlg.Destroy()
                return True
            dlg.Destroy()
        self.frame_init()
        return True

    def frame_init(self):
        frame = MyFrame(None, -1, "")
        frame.Show(True)
        self.SetTopWindow(frame)

def main():
    """Entry point"""
    global dir_path
    dir_path = os.getcwd()
    locale.setlocale(locale.LC_ALL, "")
    app = MyApp(0)
    app.MainLoop()
    return 0

if __name__ == '__main__':
    main()
