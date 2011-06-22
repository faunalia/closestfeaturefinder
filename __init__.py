# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name			 	 : ClosestFeatureFinder
Description          : Select the feature closest to the clicked point
Date                 : 22/Oct/10 
copyright            : (C) 2010 by Giuseppe Sucameli (Faunalia)
email                : brush.tyler@gmail.com

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

def name():
	return "Closest Feature Finder"

def description():
	return "Select the closest feature"

def authorName():
	return "Giuseppe Sucameli (Faunalia)"

def icon():
	return "selection.png"

def version():
	return "0.5"

def qgisMinimumVersion():
	return "1.0"

def classFactory(iface):
	from feature_finder_plugin import FeatureFinderPlugin
	return FeatureFinderPlugin(iface)
