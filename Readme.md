# Instructions to use binary release #

Follow these steps:
  * Install Visual Studio 2008 libraries (vcredist\_x86.exe)
  * Launch GUI.exe
  * Double click to set star point (it is a blue point)
  * Click object/background points
  * Click "Apply algorithm"
  * The segmented image should pop-up. If not it is in the same folder under the name results.bmp

Controls:
  * Double click : set star center
  * Right click : remove point
  * Left click : set a point (object or background)

DLLs requirements for GUI.exe:
  * OLEAUT32.dll - C:\WINDOWS\system32\OLEAUT32.dll
  * USER32.dll - C:\WINDOWS\system32\USER32.dll
  * SHELL32.dll - C:\WINDOWS\system32\SHELL32.dll
  * KERNEL32.dll - C:\WINDOWS\system32\KERNEL32.dll
  * comdlg32.dll - C:\WINDOWS\system32\comdlg32.dll
  * WSOCK32.dll - C:\WINDOWS\system32\WSOCK32.dll
  * COMCTL32.dll - C:\WINDOWS\system32\COMCTL32.dll
  * ADVAPI32.dll - C:\WINDOWS\system32\ADVAPI32.dll
  * MSVCP71.dll - c:\python25\lib\site-packages\wx-2.8-msw-unicode\wx\MSVCP71.dll          (from [WxPython ](http://www.wxpython.org/download.php#binaries))
  * GDI32.dll - C:\WINDOWS\system32\GDI32.dll
  * WINMM.dll - C:\WINDOWS\system32\WINMM.dll
  * VERSION.dll - C:\WINDOWS\system32\VERSION.dll
  * ole32.dll - C:\WINDOWS\system32\ole32.dll
  * gdiplus.dll - c:\python25\lib\site-packages\wx-2.8-msw-unicode\wx\gdiplus.dll         (from [WxPython ](http://www.wxpython.org/download.php#binaries))
  * RPCRT4.dll - C:\WINDOWS\system32\RPCRT4.dll