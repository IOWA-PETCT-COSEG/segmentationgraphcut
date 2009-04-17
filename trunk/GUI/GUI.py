#!coding: utf-8
import wx
import time
import thread
import win32api
import os, sys
import Image
import pickle

from visu import Visu

import psyco
psyco.full()


#TRACEBACK
import traceback
import sys
def Myexcepthook(type, value, tb):
        lines=traceback.format_exception(type, value, tb)
        print "\n".join(lines)
        wx.MessageBox("\n".join(lines), "Traceback Error")
sys.excepthook=Myexcepthook


#Résolution de l'écran
import ctypes
screen_width = ctypes.windll.user32.GetSystemMetrics(0)
screen_height= ctypes.windll.user32.GetSystemMetrics(1)

#IDs des boutons
ID_PLUS = 100
ID_MOINS = 101
ID_SELECT = 103
ID_APPLY = 105


class Principale(wx.Frame):
    def __init__(self, titre):
        wx.Frame.__init__(self, None, 1,
                          title = titre)
        
        self.imgORIG = None
        self.imgORIX = 0
        self.imgORIY = 0
        self.bmpRESU = None
        self.ratio = 100
        self.inc = 20
        
        self.taille_pinceau = 2
        self.background_points = set([])
        self.object_points = set([])
        self.liste_points = self.object_points
        
        self.all_points = set([])
        self.star_point = None

        

        #Bords        
        self.couleur_R, self.couleur_G, self.couleur_B = 255, 255, 0
        self.couleur_R1, self.couleur_G1, self.couleur_B1 = 0, 255, 255

        self.zone = "Object"

        self.bmp_dest = wx.Bitmap(r"Images\dest.bmp", wx.BITMAP_TYPE_BMP)
        self.bmp_source = wx.Bitmap(r"Images\source.bmp", wx.BITMAP_TYPE_BMP)
        
        self.frameicon = wx.Icon(r"Images\lena.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.frameicon)
        self.SetBackgroundColour(wx.WHITE)    
        
        #STATUSBAR
        self.barre = wx.StatusBar(self, 1)
        self.barre.SetFieldsCount(4)
        self.barre.SetStatusWidths([230, 150, 150, 100])
        self.SetStatusBar(self.barre)

        self.panel = wx.Panel(self, style = wx.RAISED_BORDER)
        self.panel.SetBackgroundColour((223,223,223))

        self.ButtonFuns = {
                           wx.ID_OPEN : self.OnOpen,
                           wx.ID_EXIT : self.OnExit,
                           wx.ID_UNDO : self.Retour,
                           ID_PLUS    : self.Plus,
                           ID_SELECT : self.OnClickSelect,
                           ID_APPLY : self.OnClickApply,
                           ID_MOINS   : self.Moins
                          }
        

        #BOUTONS
        self.boutons_visualisation = []
        self.boutons_selection = []
        self.boutons_algo = []

        self.sizer_boutons_selection = wx.FlexGridSizer(rows = 1, hgap=5)
        self.sizer_boutons_visualisation = wx.FlexGridSizer(rows = 1, hgap=5)
        self.sizer_boutons_apply = wx.FlexGridSizer(rows = 1, hgap=5)

        #Outils de visualisation
        self.AddSimpleTool(wx.ID_OPEN,
                           wx.Bitmap(r"Images\open.bmp", wx.BITMAP_TYPE_BMP),
                           "Ouvrir une image",
                           self.sizer_boutons_visualisation,
                           self.boutons_selection)
        self.AddSimpleTool(wx.ID_UNDO,
                           wx.Bitmap(r"Images\Origine.png", wx.BITMAP_TYPE_PNG),
                           "Rétablir l'image dans sa position d'origine",
                           self.sizer_boutons_visualisation,
                           self.boutons_visualisation)
        self.AddSimpleTool(ID_PLUS,
                           wx.Bitmap(r"Images\plus.gif", wx.BITMAP_TYPE_GIF),
                           "Augmenter le zoom de 20%",
                           self.sizer_boutons_visualisation,
                           self.boutons_visualisation)
        self.AddSimpleTool(ID_MOINS,
                           wx.Bitmap(r"Images\moins.gif", wx.BITMAP_TYPE_GIF),
                           "Diminuer le zoom de 20%",
                           self.sizer_boutons_visualisation,
                           self.boutons_visualisation)

##        #Outils de sélection
##        self.AddSimpleTool(ID_SELECT,
##                           wx.Bitmap(r"Images\cursor.gif", wx.BITMAP_TYPE_GIF),
##                           "Sélection de points",
##                           self.sizer_boutons_selection,
##                           self.boutons_selection)

        #Outils algorithmiques
        self.AddSimpleTool(ID_APPLY,
                           wx.Bitmap(r"Images\apply4.png", wx.BITMAP_TYPE_PNG),
                           "Apply algorithm",
                           self.sizer_boutons_apply,
                           self.boutons_selection)

        #SIZERS
        self.sizer_visualisation = wx.FlexGridSizer(cols = 1, vgap=5)
        self.text_visualisation = wx.StaticText(self.panel, -1, "Visualization tools")
        self.text_visualisation.SetFont(wx.Font(11, wx.ROMAN, wx.NORMAL, wx.NORMAL, underline = False))
        self.sizer_visualisation.Add(self.text_visualisation, flag= wx.ALIGN_CENTER)
        self.sizer_visualisation.Add(self.sizer_boutons_visualisation, flag= wx.ALIGN_CENTER)
        
        self.sizer_algo = wx.FlexGridSizer(cols = 1, vgap=5)
        self.text_algo = wx.StaticText(self.panel, -1, "Apply algorithm")
        self.text_algo.SetFont(wx.Font(11, wx.ROMAN, wx.NORMAL, wx.NORMAL, underline = False))
        self.sizer_algo.Add(self.text_algo, flag= wx.ALIGN_CENTER)
        self.sizer_algo.Add(self.sizer_boutons_apply, flag= wx.ALIGN_CENTER)


        #Espace pour afficher les paramètres de l'algo
        self.box = wx.StaticBox(self.panel, -1, "Outils de sélection")
        self.box.SetFont(wx.Font(10, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        self.sizer_params_box = wx.StaticBoxSizer(self.box, wx.VERTICAL)
        self.sizer_params = wx.FlexGridSizer(cols = 2, hgap=20)
        self.sizer_params_box.Add(self.sizer_params, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, border=10)


        #Espace pour afficher les paramètres de sélectrion de la zone
        self.sizer_zone = wx.GridSizer(cols = 1, vgap=0)



        #Sizer boutons
        self.sizer_boutons = wx.FlexGridSizer(rows=1, hgap = 70)
        self.sizer_boutons.Add(self.sizer_visualisation, 1, flag= wx.ALIGN_CENTER)
        #self.sizer_boutons.Add(self.sizer_selection, 1, flag= wx.ALIGN_CENTER)
        self.sizer_boutons.Add(self.sizer_params_box, 1, flag= wx.ALIGN_CENTER | wx.EXPAND)
        self.sizer_boutons.Add(self.sizer_zone, 1, flag= wx.ALIGN_CENTER | wx.EXPAND)
        self.sizer_boutons.Add(self.sizer_algo, 1, flag= wx.ALIGN_CENTER)
        
        #Sizer du panel
        self.sizer_panel = wx.FlexGridSizer(rows=1)
        self.sizer_panel.Add(self.sizer_boutons, 1, wx.ALL | wx.ALIGN_CENTER, border = 5)
        self.panel.SetSizer(self.sizer_panel)

        #Panneau pour afficher l'image
        self.panneau = Visu(self)
        self.panneau.SetMinSize((1000,500))
     
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, flag = wx.EXPAND)
        sizer.Add(self.panneau, 1,flag = wx.EXPAND)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_CLOSE, self.OnExit)
        #self.panel.Bind(wx.EVT_CHAR, self.OnShortcutPress)
        self.panneau.panel.Bind(wx.EVT_CHAR, self.OnCharPress)


        self.panneau.panel.Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick)
        self.panneau.panel.Bind(wx.EVT_RIGHT_UP, self.OnRemovePolygonPoint)
        
        self.panneau.panel.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)


        #Paramètres de l'algo
        self.box.Show()

        self.sizer_params1 = wx.FlexGridSizer(cols=2, vgap=2, hgap=1)
        self.sizer_params2 = wx.FlexGridSizer(cols=2, vgap=2, hgap=1)

        self.largeur_patch_picker = wx.TextCtrl(self.panel, -1, "20", size=(50, -1))
        self.largeur_patch_picker_text = wx.StaticText(self.panel, -1, u'\u03BB')
        self.largeur_patch_picker_text.SetFont(wx.Font(10, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        self.sizer_params1.Add(self.largeur_patch_picker_text, 1, flag=wx.ALIGN_LEFT|wx.RIGHT, border=10)
        self.sizer_params1.Add(self.largeur_patch_picker, 1, flag=wx.ALIGN_RIGHT)

        self.largeur_voisinage_picker = wx.TextCtrl(self.panel, -1, "", size=(50, -1))
        self.largeur_voisinage_picker_text = wx.StaticText(self.panel, -1, u'\u03C3')
        self.largeur_voisinage_picker_text.SetFont(wx.Font(10, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        self.sizer_params1.Add(self.largeur_voisinage_picker_text, 1, flag=wx.ALIGN_LEFT|wx.RIGHT, border=10)
        self.sizer_params1.Add(self.largeur_voisinage_picker, 1, flag=wx.ALIGN_RIGHT)

        self.texts = {}
        self.texts_inv = {}
        self.labels = [u"Boundary ballooning  \u03B2",
                       'Uniform ballooning     F',
                       'Force ballooning          F']

        self.distance_maxi_picker = wx.TextCtrl(self.panel, -1, "-10", size=(50, -1))
        self.distance_maxi_picker_text = wx.RadioButton(self.panel, -1, self.labels[0])
        self.distance_maxi_picker_text.SetValue(True)
        self.distance_maxi_picker_text.Bind(wx.EVT_RADIOBUTTON, self.OnRadio)
        self.distance_maxi_picker_text.SetFont(wx.Font(10, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        self.sizer_params2.Add(self.distance_maxi_picker_text, 1, flag=wx.ALIGN_LEFT)
        self.sizer_params2.Add(self.distance_maxi_picker, 1, flag=wx.ALIGN_RIGHT)
        self.selectedText = self.distance_maxi_picker
        self.texts[self.labels[0]] = self.distance_maxi_picker
        self.texts_inv[self.distance_maxi_picker] = self.labels[0]

        self.force_picker_uni = wx.TextCtrl(self.panel, -1, "0.1", size=(50, -1))
        self.force_picker_uni_text = wx.RadioButton(self.panel, -1, self.labels[1])
        self.force_picker_uni_text.Bind(wx.EVT_RADIOBUTTON, self.OnRadio)
        self.force_picker_uni_text.SetFont(wx.Font(10, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        self.sizer_params2.Add(self.force_picker_uni_text, 1, flag=wx.ALIGN_LEFT)
        self.sizer_params2.Add(self.force_picker_uni, 1, flag=wx.ALIGN_RIGHT)
        self.texts[self.labels[1]] = self.force_picker_uni
        self.texts_inv[self.force_picker_uni] = self.labels[1]

        self.force_picker = wx.TextCtrl(self.panel, -1, "5", size=(50, -1))
        self.force_picker_text = wx.RadioButton(self.panel, -1, self.labels[2])
        self.force_picker_text.Bind(wx.EVT_RADIOBUTTON, self.OnRadio)
        self.force_picker_text.SetFont(wx.Font(10, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        self.sizer_params2.Add(self.force_picker_text, 1, flag=wx.ALIGN_LEFT)
        self.sizer_params2.Add(self.force_picker, 1, flag=wx.ALIGN_RIGHT)
        self.texts[self.labels[2]] = self.force_picker
        self.texts_inv[self.force_picker] = self.labels[2]
        
        for text in self.texts.values():
            text.Enable(False)
        self.texts[self.labels[0]].Enable(True)
        
        self.border_background = wx.CheckBox(self.panel, -1, "")
        self.border_background.SetValue(True)
        self.border_background_text = wx.StaticText(self.panel, -1, "Border is back")
        self.border_background_text.SetFont(wx.Font(10, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        self.sizer_params1.Add(self.border_background_text, 1, flag=wx.RIGHT, border=7)
        self.sizer_params1.Add(self.border_background, 1)

        self.star_shape = wx.CheckBox(self.panel, -1, "")
        self.star_shape.SetValue(True)
        self.star_shape_text = wx.StaticText(self.panel, -1, "Star shape")
        self.star_shape_text.SetFont(wx.Font(10, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        self.sizer_params1.Add(self.star_shape_text, 1, flag=wx.RIGHT, border=7)
        self.sizer_params1.Add(self.star_shape, 1)
        
        
        self.sizer_params.Add(self.sizer_params1, 1, flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=0)
        self.sizer_params.Add(self.sizer_params2, 1, flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=0)

        self.box.SetLabel("Algo parameters")







        #Paramètres de sélection de zone
        sampleList = ['Object', 'Background']
        self.radio_box_zone = wx.RadioBox(self.panel, -1, "Current area", (-1, -1), wx.DefaultSize,
                                          sampleList, 2, wx.RA_VERTICAL)
        self.radio_box_zone.SetFont(wx.Font(10, wx.ROMAN, wx.NORMAL, wx.NORMAL))
        self.radio_box_zone.SetMinSize((120, -1))
        #self.radio_box_zone.Border = 10
        self.radio_box_zone.Bind(wx.EVT_RADIOBOX, self.OnClickRadioBox)
        self.sizer_zone.Add(self.radio_box_zone, 1, flag = wx.ALL | wx.EXPAND | wx.ALIGN_CENTER, border = 1)
        

        #Layout de la fenetre
        self.Fit()

        #Positionnement de la fenetre au centre de l'écran
        w, h = self.GetSize()
        self.SetPosition((int(screen_width/2-w/2)-78, 10))



    def OnRadio(self, event):
        if self.selectedText:
            self.selectedText.Enable(False)
        radioSelected = event.GetEventObject()
        text = self.texts[radioSelected.GetLabel()]
        text.Enable(True)
        self.selectedText = text



    def OnDoubleClick(self, evt):
        
        if self.star_point:
            self.show_error("Only one star point allowed")
            return
        
        #Ajout du point centre de l'étoile
        X = int(100.*evt.X/self.ratio)
        Y = int(100.*evt.Y/self.ratio)

        x1, x2 = max(X-self.taille_pinceau, 0), min(X+self.taille_pinceau+1, self.imgORIX)
        y1, y2 = max(Y-self.taille_pinceau, 0), min(Y+self.taille_pinceau+1, self.imgORIY)
        self.imgORIG.SetRGBRect(wx.Rect(x1, y1, x2-x1, y2-y1), 0, 0, 255)
        
        largeur = (self.imgORIX * self.ratio)/100
        hauteur = (self.imgORIY * self.ratio)/100
        self.bmpRESU = self.imgORIG.Scale(largeur, hauteur).ConvertToBitmap()
        self.panneau.Affiche(self.bmpRESU, self.ratio)
        
        if self.star_point:
            (X,Y) = self.star_point
            #Suppression du marqueur du point
            for x in range(max(X-2, 0), min(X+2+1, self.imgORIX)):
                for y in range(max(Y-2, 0), min(Y+2+1, self.imgORIY)):
                    self.imgORIG.SetRGB(x, y, self.imgORIGORIG.GetRed(x,y), self.imgORIGORIG.GetGreen(x,y), self.imgORIGORIG.GetBlue(x,y))
        
        self.star_point = (X,Y)
        self.liste_points.add((X,Y))                
        self.all_points.add((X,Y))



    def AddSimpleTool(self, id, bmp, tooltip, sizer, liste):
        """Ajouter un bouton"""
        button = wx.BitmapButton(self.panel, id, bmp)
        button.SetBackgroundColour('WHITE')
        button.Bind(wx.EVT_BUTTON, self.ButtonFuns[id])
        
        button.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterBitmapButton)
        button.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveBitmapButton)
        
        button.SetToolTipString( tooltip )
        sizer.Add(button, 1, wx.ALIGN_CENTER)
        liste.append(button)
        return button


    def OnClickRadioBox(self, evt):
        if evt.GetString() == "Object":
            self.zone = "Object"
            
            self.liste_points = self.object_points

            self.couleur_R, self.couleur_G, self.couleur_B = 255, 255, 0
            self.couleur_R1, self.couleur_G1, self.couleur_B1 = 0, 255, 255
        else:
            self.zone = "Background"
            
            self.liste_points = self.background_points

            self.couleur_R, self.couleur_G, self.couleur_B = 0, 255, 255
            self.couleur_R1, self.couleur_G1, self.couleur_B1 = 255, 255, 0




    def OnEnterBitmapButton(self, event):
        self.barre.SetStatusText(event.EventObject.GetToolTip().GetTip(), 0)
        
    def OnLeaveBitmapButton(self, event):
        self.barre.SetStatusText("", 0)
        

    def DefaultLeftClickBehaviour(self, evt):
        self.panneau.panel.SetFocus()

    def DefaultRightClickBehaviour(self, evt):
        self.panneau.panel.SetFocus()

    def write(self, s):
        f=open("log.txt", "a")
        f.write(str(s)+'\n')
        f.close()
        

    def OnLeftClick(self, evt):
        """Sélection de points"""
        if evt.LeftIsDown():
            X = int(100.*evt.X/self.ratio)
            Y = int(100.*evt.Y/self.ratio)

            x1, x2 = max(X-self.taille_pinceau, 0), min(X+self.taille_pinceau+1, self.imgORIX)
            y1, y2 = max(Y-self.taille_pinceau, 0), min(Y+self.taille_pinceau+1, self.imgORIY)
            self.imgORIG.SetRGBRect(wx.Rect(x1, y1, x2-x1, y2-y1), self.couleur_R, self.couleur_G, self.couleur_B)
            
            largeur = (self.imgORIX * self.ratio)/100
            hauteur = (self.imgORIY * self.ratio)/100
            self.bmpRESU = self.imgORIG.Scale(largeur, hauteur).ConvertToBitmap()
            self.panneau.Affiche(self.bmpRESU, self.ratio)
            
            self.liste_points.add((X,Y))                
            self.all_points.add((X,Y))

##            for x in range(x1, x2):
##                for y in range(y1, y2):
##                    self.bord.add((x,y))
##
##                    #Suppresssion des points dans l'autre bord                    
##                    #self.bord_autre.remove((x,y))
                    
                    
        evt.Skip()


    def OnRightClick(self, evt):
        """Désélection de points"""
        if evt.LeftIsDown():
            X = int(100.*evt.X/self.ratio)
            Y = int(100.*evt.Y/self.ratio)

            x1, x2 = max(X-self.taille_pinceau, 0), min(X+self.taille_pinceau+1, self.imgORIX)
            y1, y2 = max(Y-self.taille_pinceau, 0), min(Y+self.taille_pinceau+1, self.imgORIY)

            largeur = (self.imgORIX * self.ratio)/100
            hauteur = (self.imgORIY * self.ratio)/100
            self.bmpRESU = self.imgORIG.Scale(largeur, hauteur).ConvertToBitmap()
            self.panneau.Affiche(self.bmpRESU, self.ratio)

##            for x in range(x1, x2):
##                for y in range(y1, y2):
##                    self.imgORIG.SetRGB(x, y, self.imgORIGORIG.GetRed(x,y), self.imgORIGORIG.GetGreen(x,y), self.imgORIGORIG.GetBlue(x,y))
##                    self.bord.discard((x,y))

      

    def OnRemovePolygonPoint(self, evt):
        if self.imgORIG != None:

            X = int(100.*evt.X/self.ratio)
            Y = int(100.*evt.Y/self.ratio)


            ind_list = []
            for (x,y) in self.object_points:
                if abs(x-X)<3 and abs(y-Y)<3:
                    (X, Y) = (x, y)
                    ind_list.append(1)
                    break
            for (x,y) in self.background_points:
                if abs(x-X)<3 and abs(y-Y)<3:
                    (X, Y) = (x, y)
                    ind_list.append(2)
                    break
            if self.star_point:
                if abs(self.star_point[0]-X)<3 and abs(self.star_point[1]-Y)<3:
                    (X, Y) = self.star_point
                    ind_list.append(0)
            
            if not ind_list:
                #self.show_error("Click on a point to delete it!")
                return


            #Suppression du marqueur du point
            for x in range(max(X-2, 0), min(X+2+1, self.imgORIX)):
                for y in range(max(Y-2, 0), min(Y+2+1, self.imgORIY)):
                    self.imgORIG.SetRGB(x, y, self.imgORIGORIG.GetRed(x,y), self.imgORIGORIG.GetGreen(x,y), self.imgORIGORIG.GetBlue(x,y))


            #Suppression du point dans la liste
            if 1 in ind_list:
                self.object_points.remove((X,Y))
            if 2 in ind_list:
                self.background_points.remove((X,Y))
            if 0 in ind_list:
                self.star_point = []
            self.all_points.remove((X,Y))

            largeur = (self.imgORIX * self.ratio)/100
            hauteur = (self.imgORIY * self.ratio)/100
            self.bmpRESU = self.imgORIG.Scale(largeur, hauteur).ConvertToBitmap()
            self.panneau.Affiche(self.bmpRESU, self.ratio)


        

    def OnLeftUp(self, evt):
        #print "Up"
        if self.HasCapture():
            self.ReleaseMouse()

    def OnLeftDown(self, evt):
        #print "Down"
        self.CaptureMouse()
        #print "Fini down"


    def OnClickSelect(self, evt):
        if self.imgORIG != None:
            
            self.EnableAllSelectionButtons(False, evt.GetEventObject())

            self.panneau.panel.Unbind(wx.EVT_LEFT_DOWN)
            self.panneau.panel.Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick)

            self.panneau.panel.Unbind(wx.EVT_RIGHT_UP)



    def EnableAllSelectionButtons(self, bool, widget):
        for button in self.boutons_selection:
            if bool:
                if button == widget:
                    button.Enable()
                else:
                    button.Disable()
            else:
                if button != widget:
                    button.Enable()
                else:
                    button.Disable()


    def OnCharPress(self, evt):
        if evt.GetKeyCode() == 45:
            self.Moins(None)
        elif evt.GetKeyCode() == 43:
            self.Plus(None)
                  

    def Retour(self, evt):
        if self.imgORIG != None:
            self.ratio = 100
            self.bmpRESU = self.imgORIG.ConvertToBitmap()
            self.panneau.Affiche(self.bmpRESU, self.ratio)
            self.barre.SetStatusText("(%s, %s) %s %%"%(self.imgORIX,
                                                       self.imgORIY, self.ratio), 1)

    def Plus(self, evt):
        if self.imgORIG != None:
            self.ratio = self.ratio + self.inc
            largeur = (self.imgORIX * self.ratio)/100
            hauteur = (self.imgORIY * self.ratio)/100
            self.bmpRESU = self.imgORIG.Scale(largeur, hauteur).ConvertToBitmap()
            self.panneau.Affiche(self.bmpRESU, self.ratio)
            self.barre.SetStatusText("(%s, %s) %s %%"%(self.imgORIX,
                                                       self.imgORIY, self.ratio), 1)

    def Moins(self, evt):
        if self.ratio > self.inc and self.imgORIG != None:
            self.ratio = self.ratio - self.inc
            largeur = (self.imgORIX * self.ratio)/100
            hauteur = (self.imgORIY * self.ratio)/100
            self.bmpRESU = self.imgORIG.Scale(largeur, hauteur).ConvertToBitmap()
            self.panneau.Affiche(self.bmpRESU, self.ratio)
            self.barre.SetStatusText("(%s, %s) %s %%"%(self.imgORIX,
                                                       self.imgORIY, self.ratio), 1)

    def OnOpen(self, evt=None):      
        dlg = wx.FileDialog(self, "Choisissez l'image à ouvrir", os.getcwd()+"\\Samples", "voiture.jpg",
                            wildcard = "Image files (*.bmp; *.jpg; *.png; *.gif)|*.bmp;*.jpg;.png;.gif",
                            style = wx.OPEN)
        retour = dlg.ShowModal()
        chemin = dlg.GetPath()
        fichier = dlg.GetFilename()
        dlg.Destroy()
        
        if retour == wx.ID_OK and fichier != "":
            self.panneau.Efface()
            self.imgORIG = None
            self.imgORIX = 0
            self.imgORIY = 0
            self.bmpRESU = None
            self.ratio = 100
            self.taille_pinceau = 2
            
            self.background_points = set([])
            self.object_points = set([])
            self.all_points = set([])
            self.star_point = []
            self.liste_points = self.object_points
            
            self.radio_box_zone.SetStringSelection("Object")
            
            self.imgORIG = wx.Image(chemin, wx.BITMAP_TYPE_ANY)
            self.imgORIGORIG = self.imgORIG.Copy() #Sans les sélections
            
            self.imgORIX = self.imgORIG.GetWidth()
            self.imgORIY = self.imgORIG.GetHeight()
            self.bmpRESU = self.imgORIG.ConvertToBitmap()
            self.panneau.Affiche(self.bmpRESU, self.ratio)
            self.SetTitle("Segmentation by Graph-Cut [%s]"% fichier)
            self.barre.SetStatusText("(%s, %s) %s %%"%(self.imgORIX,
                                                       self.imgORIY, self.ratio), 1)
            


    def OnExit(self, evt=None):
        self.Destroy()
        wx.GetApp().ProcessIdle()
        sys.exit(0)




    def OnClickApply(self, evt):
        if self.imgORIG == None :
            self.show_error("No image", "Warning")
            return

        if not self.all_points:
            self.show_error("No seed point", "Warning")
            return
        
        if not self.star_point:
            self.show_error("No star point", "Warning")
            return

        self.final_image = self.imgORIGORIG.Copy()

        #Mask:
        #     - 1 : Points de l'objet
        #     - 0 : Points du fond
        im = Image.new('L', self.final_image.GetSize(), 255)
        for point in self.object_points:
            im.putpixel(point, 1)
        for point in self.background_points:
            im.putpixel(point, 0)
        im.putpixel(self.star_point, 2)
        im.save('mask.bmp')

        #SAUVEGARDE DE L'IMAGE
        self.final_image.SaveFile('image.bmp', wx.BITMAP_TYPE_BMP)

##        try:
##            self.lamb = float(self.largeur_patch_picker.GetLabel())
##            self.sigma = float(self.largeur_voisinage_picker.GetLabel())
##            self.beta = float(self.distance_maxi_picker.GetLabel())
##        except Exception, ex:
##            self.show_error("Please enters decimals\n"+str(Exception)+"  "+str(ex), "Error")

        self.lamb = self.largeur_patch_picker.GetLabel()
        self.sigma = self.largeur_voisinage_picker.GetLabel()
        
        self.force_type = str(self.labels.index(self.texts_inv[self.selectedText]))
        self.force = self.selectedText.GetLabel()
        
        
        ##GENERAL PARAMETERS
        #Border is back
        if self.border_background.GetValue():
            self.auto_background = "1"
        else:
            self.auto_background = "0"

        #Object has star shape
        if self.star_shape.GetValue():
            self.star = "1"
        else:
            self.star = "0"

        try:
            float(self.force)
        except ValueError:
            self.force = "-234.12"

        try:
            float(self.sigma)
        except ValueError:
            self.sigma = "0"
        
        print "Force type is", self.force_type, " value=", repr(self.force)

        #DEMARRAGE DE L'EXE
        """
        Paramètres envoyés:
            - Lambda
            - Sigma
            - Border is back
            - Type de la force
            - Paramètre force
        """
        
        path_exe = "graphcuts.exe"
        self.pid = os.spawnv(os.P_WAIT, path_exe, ['"'+os.getcwd()+'"',
                                                   self.lamb,
                                                   self.sigma,
                                                   self.auto_background,
                                                   self.star,
                                                   self.force_type,
                                                   self.force
                                                   ]
                             )

        os.startfile("results.bmp")




    def OnChangeZoomRatio(self, evt):
        self.ratio = self.taille_ratio_picker.GetValue()
        if self.imgORIG != None:
            largeur = (self.imgORIX * self.ratio)/100
            hauteur = (self.imgORIY * self.ratio)/100
            self.bmpRESU = self.imgORIG.Scale(largeur, hauteur).ConvertToBitmap()
            self.panneau.Affiche(self.bmpRESU, self.ratio)
            self.barre.SetStatusText("(%s, %s) %s %%"%(self.imgORIX,
                                                       self.imgORIY, self.ratio), 1)



    def show_error(self, message, titre = "Avertissement"):
        box = wx.MessageBox(message, titre, parent = self, style = wx.OK | wx.ICON_EXCLAMATION)









class GUIApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        fen = Principale("Segmentation by Graph-Cut")
        fen.Show(True)
        self.SetTopWindow(fen)
        fen.OnOpen()
        return True

app = GUIApp(False)
app.MainLoop()


