( Generation parameters: C:\Users\a\source\repos\inkscape-unicorn\src\testRectGenerator.py )
G21 (metric ftw)
G90 (absolute mode)
G0 F6000.00 (set speed for travel)

G28 ; Home all axes
G0 X52.00 Y14.00 Z95.00 (go to start point)
M0 Turn on laser to set the focus point
M106
M0 Set focus point of the laser
M107
M0 Put on the actual workpiece

G1 Z95.00
(TestRect with bottom left at [50.00, 0.00] and size 10.00x10.00, laser intensity at 255, countour only)
G1 X52.00 Y64.00 F6000.00
M106
G4 P20 (wait 20ms)
G1 X52.00 Y74.00 F70.00
G1 X62.00 Y74.00 F70.00
G1 X62.00 Y64.00 F70.00
G1 X52.00 Y64.00 F70.00
M107
G4 P20 (wait 20ms)

G1 Z94.00
(TestRect with bottom left at [50.00, 0.00] and size 10.00x10.00, laser intensity at 255, countour only)
M106
G4 P20 (wait 20ms)
G1 X52.00 Y74.00 F70.00
G1 X62.00 Y74.00 F70.00
G1 X62.00 Y64.00 F70.00
G1 X52.00 Y64.00 F70.00
M107
G4 P20 (wait 20ms)

G1 Z93.00
(TestRect with bottom left at [50.00, 0.00] and size 10.00x10.00, laser intensity at 255, countour only)
M106
G4 P20 (wait 20ms)
G1 X52.00 Y74.00 F70.00
G1 X62.00 Y74.00 F70.00
G1 X62.00 Y64.00 F70.00
G1 X52.00 Y64.00 F70.00
M107
G4 P20 (wait 20ms)

G1 Z92.00
(TestRect with bottom left at [50.00, 0.00] and size 10.00x10.00, laser intensity at 255, countour only)
M106
G4 P20 (wait 20ms)
G1 X52.00 Y74.00 F70.00
G1 X62.00 Y74.00 F70.00
G1 X62.00 Y64.00 F70.00
G1 X52.00 Y64.00 F70.00
M107
G4 P20 (wait 20ms)

G1 Z91.00
(TestRect with bottom left at [50.00, 0.00] and size 10.00x10.00, laser intensity at 255, countour only)
M106
G4 P20 (wait 20ms)
G1 X52.00 Y74.00 F70.00
G1 X62.00 Y74.00 F70.00
G1 X62.00 Y64.00 F70.00
G1 X52.00 Y64.00 F70.00
M107
G4 P20 (wait 20ms)

G1 Z90.00
(TestRect with bottom left at [50.00, 0.00] and size 10.00x10.00, laser intensity at 255, countour only)
M106
G4 P20 (wait 20ms)
G1 X52.00 Y74.00 F70.00
G1 X62.00 Y74.00 F70.00
G1 X62.00 Y64.00 F70.00
G1 X52.00 Y64.00 F70.00
M107
G4 P20 (wait 20ms)


(end of print job)
M107
G4 P20 (wait 20ms)
M300 S255 (turn off servo)
G0 F6000.00
G0 X52.00 Y14.00 Z95.00 (go to start point)
M18 (drives off)
