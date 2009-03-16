#!coding: utf-8
import wx, time


#TRACEBACK
import traceback
import sys
def Myexcepthook(type, value, tb):
        lines=traceback.format_exception(type, value, tb)
        f=open('log.txt', 'a')
        f.write("\n".join(lines))
        f.close()
        print "\n".join(lines)
sys.excepthook=Myexcepthook


class Visu(wx.ScrolledWindow):
    def __init__(self, conteneur):
        wx.ScrolledWindow.__init__(self, parent = conteneur, style=wx.SUNKEN_BORDER)

        self.parent = conteneur
        self.bmp = None
        self.image = self
        self.ratio = 100
        self.panel = wx.Panel(self)

        self.cursor_normal = wx.CursorFromImage(wx.Image(r"Images\normal.cur"))
        self.cursor_take = wx.CursorFromImage(wx.Image(r"Images\take.ani"))

        self.InitBuffer()        

        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)
        self.panel.Bind(wx.EVT_MOTION, self.OnMouseMove)
        
        self.SetVirtualSize((1000, 1000))


    def InitBuffer(self):
        size = self.GetClientSize()
        self.buffer = wx.EmptyBitmap(size.width, size.height)
        

    def Affiche(self, bmp, ratio):
        self.SetVirtualSize(wx.Size(bmp.GetWidth(), bmp.GetHeight()))
        self.panel.SetSize(wx.Size(bmp.GetWidth(), bmp.GetHeight()))
        
        self.SetScrollRate((10*ratio)/100, (10*ratio)/100)
        if bmp != None:
            posX, posY = self.GetViewStart()
            self.Scroll(posX, posY)
        else:
            posX, posY = (0, 0)

        self.buffer = bmp
        
        # draw the image
        dc = wx.BufferedDC(wx.ClientDC(self.panel), self.buffer)
        """
        if ratio != self.ratio:
            self.dc.Clear()
            self.dc.DrawBitmap(self.buffer, 0, 0, False)
        """
        self.ratio = ratio      


    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self.panel, self.buffer)


    def Efface(self):
        self.bmp = None
        self.SetScrollRate(0, 0)

        self.buffer = wx.EmptyBitmap(0, 0)
        dc = wx.BufferedDC(wx.ClientDC(self.panel), self.buffer)
        
        #self.dc.Clear()
        

    def OnMouseMove(self, evt):
        X = int(100.*evt.X/self.parent.ratio)
        Y = int(100.*evt.Y/self.parent.ratio)

        if X>=self.parent.imgORIG.GetWidth() or Y>=self.parent.imgORIG.GetHeight():
            return

        self.parent.barre.SetStatusText("(%d,%d)"%(X, Y), 2)
        self.parent.barre.SetStatusText("(%d,%d,%d)"%(self.parent.imgORIG.GetRed(X, Y),
                                                      self.parent.imgORIG.GetGreen(X, Y),
                                                      self.parent.imgORIG.GetBlue(X, Y)),
                                        3)

        take = False
        for (x,y) in self.parent.all_points:
            if abs(x-X)<3 and abs(y-Y)<3:
                self.SetCursor( self.cursor_take )
                take = True
                break
        
        if take:
            self.SetCursor( self.cursor_take )
        else:
            self.SetCursor( self.cursor_normal )
            
