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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import resources_rc

class FeatureFinderPlugin:

	def __init__(self, iface):
		self.iface = iface

	def initGui(self):
		self.wdg = None

		self.action = QAction( QIcon( ":/plugins/ClosestFeatureFinder/icons/selection.png" ), "Closest Feature Finder Plugin", self.iface.mainWindow() )
		self.action.setCheckable(True)
		QObject.connect( self.action, SIGNAL( "triggered()" ), self.start )

		self.aboutAction = QAction("About", self.iface.mainWindow())
		QObject.connect( self.aboutAction, SIGNAL("triggered()"), self.about )

		self.iface.addToolBarIcon( self.action )
		self.iface.addPluginToMenu( "&Feature Finder Plugin", self.action )
		self.iface.addPluginToMenu( "&Feature Finder Plugin", self.aboutAction )

	def unload(self):
		self.iface.removeToolBarIcon( self.action )
		self.iface.removePluginMenu( "&Feature Finder Plugin", self.action )
		self.iface.removePluginMenu( "&Feature Finder Plugin", self.aboutAction )

		if self.wdg != None:
			self.wdg.stopCapture()
			QObject.disconnect( self.iface.mapCanvas(), SIGNAL( "mapToolSet(QgsMapTool *)" ), self.toolChanged)
			self.wdg = None

	def about(self):
		from DlgAbout import DlgAbout
		DlgAbout(self.iface.mainWindow()).exec_()

	def start(self):
		self.action.setChecked( True )
		if self.wdg == None:
			from closest_feature_finder import ClosestFeatureFinder
			self.wdg = ClosestFeatureFinder(self.iface)
			QObject.connect( self.iface.mapCanvas(), SIGNAL( "mapToolSet(QgsMapTool *)" ), self.toolChanged)

		if not self.wdg.isActive():
			self.wdg.startCapture()

	def toolChanged(self, tool):
		self.action.setChecked( self.wdg != None and self.wdg.isActive() )
		

