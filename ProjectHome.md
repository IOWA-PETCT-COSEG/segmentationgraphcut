# Graphcut Segmentation Project #


Implementation of the article
_Star Shape Prior for Graph-Cut Image Segmentation
Olga Veksler
University of Western Ontario
London, Canada_


## Abstract ##
The article deals with segmentation by Graph-Cut with using prior knowledge from the object. This algorithm uses a classic Graph-Cut method, but also imposes that the result object has a star shape. A star-shape surface is a surface which has the following property: for each point of the surface, the segment between this point and the center of the shape is totally inside the object. The class of such objects is huge. Here are some examples:

http://segmentationgraphcut.googlecode.com/svn/trunk/Results/star_shapes.JPG

Incorporating star shape prior to the Graph-Cut segmentation algorithm gives slightly better results than classical Graph-Cut segmentation, and requires the user clicking the center of the shape.


## Report ##
[Available here !](http://segmentationgraphcut.googlecode.com/files/Rapport.pdf)

## Presentation ##
[Available here !](http://segmentationgraphcut.googlecode.com/files/Soutenance.pdf)

## Example of result ##

http://segmentationgraphcut.googlecode.com/svn/trunk/Results/ours.JPG

## Binary release ##
http://segmentationgraphcut.googlecode.com/svn/trunk/Results/GUI_screenshot.JPG
### Instructions ###
  * Install Visual Studio 2008 libraries (vcredist\_x86.exe)
  * Launch GUI.exe
  * Double click to set star point
  * Click object/background points
  * Click "Apply algorithm"
  * The segmented image should pop-up. If not it is in the same folder under the name results.bmp

Controls:
  * Double click : set star center
  * Right click : remove point
  * Left click : set a point (object or background)

[Download here](http://segmentationgraphcut.googlecode.com/files/Graph-Cut%20Star%20Shape%20Prior%20Segmenter%201.1.7z)