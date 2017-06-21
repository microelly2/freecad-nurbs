Die Nurbs Workbench ist eine Sammlung von Skripten zur Verwaltung von Freiformflächen und Kurven.


Links
=====


[Etwas Theorie von Autodesk Alias http://help.autodesk.com/](http://help.autodesk.com/view/ALIAS/2018/ENU/?guid=GUID-B0AAF7CA-FDBD-49FC-88BA-4F1609BC61CE)

[Nurbs Workbench Anwenderdokumentation http://freecadbuch.de](http://freecadbuch.de/doku.php?id=nurbs)

[Kurven und Flächen-Theorie: COMPUTER AIDED GEOMETRIC DESIGN
Thomas W. Sederberg]  (http://cagd.cs.byu.edu/~557/text/cagd.pdf)

Videos
======



[Sketcher::SketchObjectPython](https://www.youtube.com/watch?v=U31O5vW4UhI)(16.06.2017)

Aus einem Polygonzug-Sketch wird eine BSpline Kurve berechnet und daraus zwei Offset-Kurven

verwendete Klassen: Sketcher::SketchObjectPython, Part::Offset2D

[Video split a nurbs face into 4 segments and replace two of them](https://www.youtube.com/watch?v=bBAU5fpwwk8) (07.06.2017)

Die Oberfläche eines Schuhes wird in 4 Segmente zerlegt. Zwei Segmente (Spitze und Ferse) 
werden durch eigenständige Freiformflächen ersetzt, wobei die Übergänge G0 (Position) und G1 (Tangenten) kontinuierlich sind


verwendete Klassen: TangentFace, Seam, Segment

[A bspline volume from 2 sketches](https://youtu.be/kUbKHtEtus8) (01.06.2017)

Zum Erzeugen einer Schuhspitze oder eines Hecks wird aus ein paar gegebenen Sketcher-Bsplines eine Freiformfläche berechnet.
Ausgehend von einer Fläche wird eine zweite Fläche erzeugt, deren Kanten zueinander passen. 
Das gesamte Modell lässt sich wieder in einzelnem Segmente zerlegen. 

verwendete Klassen: Segment, TangentFace, Seam





 

 
