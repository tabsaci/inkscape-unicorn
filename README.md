MakerBot Unicorn G-Code Output for Inkscape
===========================================

Notice
------

This is an Inkscape extension that allows you to save your Inkscape drawings as
G-Code files suitable for engraving with the [Creality Laser Engraver Module](https://www.creality.shop/products/creality-3d-printer-laser-engraver-module-for-ender-series).

**Users who use this extension to generate G-Code do so at their own risk.**

Author: [tabsaci](https://github.com/tabsaci)

Original Author: [Marty McGuire](https://github.com/martymcguire)

Website: [http://github.com/tabsaci/inkscape-unicorn](http://github.com/tabsaci/inkscape-unicorn)

Credits
=======

* Marty McGuire pulled this all together into an Inkscape extension.
* [Inkscape](http://www.inkscape.org/) is an awesome open source vector graphics app.

Install
=======

Copy the contents of `src/` to your Inkscape `extensions/` folder.

Typical locations include:

* OS X - `/Applications/Inkscape.app/Contents/Resources/extensions`
* Linux - `/usr/share/inkscape/extensions`
* Windows - `C:\Program Files\Inkscape\share\inkscape\extensions` >> You can use the src/deploy.py script as well

Usage
=====

* Convert all text to paths:
	* Select all text objects.
	* Choose **Path | Object to Path**.
* Save as G-Code:
	* **File | Save a Copy**.
	* Select **Laser engraver G-Code (\*.gcode)**.
	* Save your file.
* Preview
	* You can preview the G-Code in any slicer (I use Cura to check)
* Print!
	* Just execute the G-Code on your printer

