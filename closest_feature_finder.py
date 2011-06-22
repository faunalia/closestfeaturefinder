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

from qgis.core import *
from qgis.gui import *

class ClosestFeatureFinder(QWidget):

	def __init__(self, iface):
		QWidget.__init__(self, iface.mainWindow())
		self.iface = iface
		self.canvas = iface.mapCanvas()

		self.previousLayer = None
		self.index = None

		self.pointEmitter = ClosestFeatureFinder.PointEmitter(self.canvas)
		QObject.connect(self.pointEmitter, SIGNAL( "canvasClickedWithModifiers" ), self.onCanvasClicked)

	def isActive(self):
		return self.canvas.mapTool() == self.pointEmitter

	def startCapture(self):
		self.canvas.setMapTool(self.pointEmitter)

	def stopCapture(self):
		self.canvas.unsetMapTool(self.pointEmitter)

	def onCanvasClicked(self, point, button, modifiers):
		layer = self.iface.activeLayer()
		if layer == None or layer.type() != QgsMapLayer.VectorLayer:
			QMessageBox.warning( self, "Closest Feature Finder", "No vector layers selected" )
			return

		if button != Qt.LeftButton:
			return

		if not layer.hasGeometryType():
			QMessageBox.warning( self, "Closest Feature Finder", "The selected layer has either no or unknown geometry" )
			return			

		QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

		# get the point coordinates in the layer's CRS
		point = self.canvas.mapRenderer().mapToLayerCoordinates(layer, point)

		# retrieve all the layer's features
		layer.select([])

		if self.index == None or layer != self.previousLayer:
			# there's no previously created index or it's not the same layer,
			# then create the index
			self.index = QgsSpatialIndex()
			f = QgsFeature()
			while layer.nextFeature(f):
				self.index.insertFeature(f)

		# get the feature which has the closest bounding box using the spatial index
		nearest = self.index.nearestNeighbor( point, 1 )
		featureId = nearest[0] if len(nearest) > 0 else None

		closestFeature = QgsFeature()
		if featureId == None or layer.featureAtId(featureId, closestFeature, True, False) == False:
			closestFeature = None

		# if polygon, make a futher test
		if layer.geometryType() != QGis.Point and closestFeature != None:
			# find the furthest bounding box borders
			rect = closestFeature.geometry().boundingBox()

			dist_pX_rXmax = abs( point.x() - rect.xMaximum() )
			dist_pX_rXmin = abs( point.x() - rect.xMinimum() )
			if dist_pX_rXmax > dist_pX_rXmin:
				width = dist_pX_rXmax
			else:
				width = dist_pX_rXmin

			dist_pY_rYmax = abs( point.y() - rect.yMaximum() )
			dist_pY_rYmin = abs( point.y() - rect.yMinimum() )
			if dist_pY_rYmax > dist_pY_rYmin:
				height = dist_pY_rYmax
			else:
				height = dist_pY_rYmin

			# create the search rectangle
			rect = QgsRectangle()
			rect.setXMinimum( point.x() - width )
			rect.setXMaximum( point.x() + width )
			rect.setYMinimum( point.y() - height )
			rect.setYMaximum( point.y() + height )

			# retrieve all geometries into the search rectangle			
			layer.select([], rect, True, True)

			# find the nearest feature
			minDist = -1
			featureId = None
			point = QgsGeometry.fromPoint(point)

			f = QgsFeature()
			while layer.nextFeature(f):
				geom = f.geometry()
				distance = geom.distance(point)
				if minDist < 0 or distance < minDist:
					minDist = distance
					featureId = f.id()

			# get the closest feature
			closestFeature = QgsFeature()
			if featureId == None or layer.featureAtId(featureId, closestFeature, True, False) == False:
				closestFeature = None

		self.previousLayer = layer

		if closestFeature == None:
			# no feature found
			QMessageBox.warning(self, "Closest Feature Finder Plugin", QString.fromUtf8( "No features found." ) )

		else:
			# select the feature according to the pressed key modifiers

			if modifiers & Qt.ControlModifier and modifiers & Qt.ShiftModifier:
				# both ctrl and shift modifiers are pressed, 
				# invert selection of closest feature
				if layer.selectedFeaturesIds().count( closestFeature.id() ) > 0:
					layer.deselect( closestFeature.id() )
				else:
					layer.select( closestFeature.id() )

			elif modifiers & Qt.ControlModifier:
				# add the feature to the selected ones
				layer.select( closestFeature.id() )

			elif modifiers & Qt.ShiftModifier:
				# remove the feature from the selected ones
				layer.deselect( closestFeature.id() )

			else:
				# no modifiers pressed, select this feature only
				layer.removeSelection( False )
				layer.select( closestFeature.id() )

		QApplication.restoreOverrideCursor()


	class PointEmitter(QgsMapToolEmitPoint):

		def __init__(self, canvas):
			QgsMapToolEmitPoint.__init__(self, canvas)
			self.canvas = canvas

		def canvasPressEvent(self, mouseEvent):
			point = self.toMapCoordinates( mouseEvent.pos() )

			self.emit( SIGNAL( "canvasClickedWithModifiers" ), point, mouseEvent.button(), mouseEvent.modifiers() )

