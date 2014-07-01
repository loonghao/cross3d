##
#	\namespace	blur3d.api.softimage.softimagescene
#
#	\remarks	The SoftimageScene class provides the implementation of the AbstractScene class as it applies
#				to Softimage
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/04/11 
#

#------------------------------------------------------------------------------------------------------------------------

import time

from PyQt4.QtGui import QColor
from PyQt4.QtCore import QTimer
from pywintypes import com_error
from blurdev.decorators import stopwatch
from blur3d.api import application, dispatch
from blur3d import pendingdeprecation, constants
from PySoftimage import xsi, xsiFactory
from blur3d.api.abstract.abstractscene import AbstractScene
from win32com.client.dynamic import Dispatch as dynDispatch

class SoftimageScene(AbstractScene):

	_cache = {}

	def __init__(self):
		AbstractScene.__init__(self)
		self._timer = None
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def _importNativeModel(self, path, name='', referenced=False, resolution='', load=True, createFile=False):
		"""
			\remarks	implements the AbstractScene._importNativeModel to import and return a model in the scene
			\return		<PySoftimage.xsi.X3DObject> nativeObject || None
		"""
		if referenced:
			return xsi.SICreateRefModel(path, name, resolution, '', loaded, createFile)('Value')
		return xsi.ImportModel(path, '', '', '', name)('Value')
		
	def _removeNativeModels(self, models):
		"""
			\remarks	implements the AbstractScene._removeNativeModels to remove a native model in the scene. Addded by douglas
			\param		models [ <PySoftimage.xsi.Model>, ... ]
			\return		<bool> success
		"""
		undo = xsi.GetValue("preferences.General.undo")
		xsi.SetValue("preferences.General.undo", 0, "")
		self._removeNativeObjects(models)
		xsi.SetValue("preferences.General.undo", undo, "")
		return True
		
	def _setNativeSelection(self, selection):
		"""
			\remarks	implements the AbstractScene._setNativeSelection to select the inputed native objects in the scene
			\param		nativeObjects	<list> [ <PySoftimage.xsi.Object> nativeObject, .. ]
			\return		<bool> success
		"""
		if isinstance(selection, basestring):
			try:
				xsi.SelectObj(selection)
			except com_error:
				pass
			finally:
				return True
		else:
			xsiCollSelection = xsiFactory.CreateObject('XSI.Collection')
			xsiCollSelection.AddItems(selection)
			xsi.SelectObj(xsiCollSelection)
		return True
		
	def _addToNativeSelection(self, selection):
		"""
			\remarks	implements the AbstractScene._addToNativeSelection to select the inputed native objects in the scene
			\param		nativeObjects	<list> [ <PySoftimage.xsi.Object> nativeObject, .. ]
			\return		<bool> success
		"""
		if isinstance(selection, basestring):
			try:
				xsi.AddToSelection(selection)
			except com_error:
				pass
			finally:
				return True
		else:
			xsiCollSelection = xsiFactory.CreateObject('XSI.Collection')
			xsiCollSelection.AddItems(selection)
			xsi.AddToSelection(xsiCollSelection)
		
	def _nativeRootObject(self):
		"""
			\remarks	implements the AbstractScene._nativeRoot method to return the native root of the scene
			\return		<PySoftimage.xsi.X3DObject> nativeObject
		"""
		return xsi.ActiveSceneRoot

	def _removeNativeObjects(self, nativeObjects):
		"""
			\remarks	implements the AbstractScene._removeNativeObjects method to return the native root of the scene
			\return		<bool> success
		"""
		names = ["B:" + obj.FullName for obj in nativeObjects]
		xsi.DeleteObj(",".join(names))
		return True

	@pendingdeprecation
	def _nativeModels(self):
		"""
			\remarks	implements the AbstractScene._nativeModels method to return the native root of the scene
			\return		<PySoftimage.xsi.X3DObject> nativeObject
		"""
		models = []
		for obj in self._nativeObjects():
			if "model" in obj.Type.lower():
				models.append(obj)
		return models
	
	def _nativeObjects(self, getsFromSelection=False, wildcard=''):
		"""
			\remarks	implements the AbstractScene._nativeObjects method to return the native objects from the scene
			\return		<list> [ <PySoftimage.xsi.X3DObject> nativeObject, .. ] || None
		"""
		if getsFromSelection:
#			objects = xsiFactory.CreateObject( 'XSI.Collection' )
#			objects.AddItems( objects )
			if wildcard:
				import re
				expression = wildcard.replace('*', '.+').strip('.+')
				output = []
				for obj in xsi.Selection:
					if re.findall(expression, obj.FullName, flags=re.I):
						output.append(obj)
				return output
			else:
				objects = [ obj for obj in xsi.Selection ]
		else:
			root = self._nativeRootObject()
			objects = root.FindChildren(wildcard, '', '', True)
		return objects
		
	def _nativeSelection(self, wildcard=''):
		return self._nativeObjects(getsFromSelection=True, wildcard=wildcard)
	
	def _findNativeObject(self, name='', uniqueId=0):
		"""
			\remarks	implements AbstractScene._findNativeObject method to looks up a native object based on the inputed name
			\param		name <string>
			\return		<PySoftimage.xsi.X3DObject> nativeObject || None
		"""
		return xsi.Dictionary.GetObject(name, False)

	def _findNativeCamera(self, name='', uniqueId=0):
		"""
			\remarks	implements AbstractScene._findNativeObject method to looks up a native camera based on the inputed name
			\param		name <string>
			\return		<PySoftimage.xsi.X3DObject> nativeObject || None
		"""
		obj = xsi.Dictionary.GetObject(name, False)
		if 'camera' in obj.Type.lower():
			return obj
		return None

	def _freezeNativeObjects(self, nativeObjects, state):
		"""
			\remarks	implements the AbstractScene._freezeNativeObjects method to freeze(lock)/unfreeze(unlock) the inputed objects
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\param		state			<bool>
			\return		<bool> success
		"""
		for object in nativeObjects:
			object.Properties('Visibility').Parameters('selectability').SetValue(not state)
		return True
	
	def _hideNativeObjects(self, nativeObjects, state):
		"""
			\remarks	implements the AbstractScene._hideNativeObjects method to hide/unhide the inputed objects
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\param		state			<bool>
			\return		<bool> success
		"""
		for object in nativeObjects:
			object.Properties('Visibility').Parameters('viewvis').SetValue(not state)
			object.Properties('Visibility').Parameters('rendvis').SetValue(not state)
		return True
	
	@pendingdeprecation
	def _nativeCameras(self):
		"""
			\remarks	implements the AbstractScene._nativeCameras method to return the native cameras of the scene
			\return		<PySoftimage.xsi.X3DObject> nativeObject
		"""
		cameras = []
		for obj in self._nativeObjects():
			if "camera" in obj.Type.lower():
				cameras.append(obj)
		return cameras
		
	def _nativeRenderPasses(self):
		"""
			\remarks	implements the AbstractScene._nativeRenderPasses that returns the native render passes in the scene
			\return		nativeRenderPasses [ <PySoftimage.xsi.Pass>, <...> ]
		"""	
		return xsi.ActiveProject.ActiveScene.Passes
		
	def _findNativeRenderPass(self, displayName=''):
		"""
			\remarks	implements the AbstractScene._findNativeRenderPass that find render passes in the scene based on their display name
			\Param		displayName <string>
			\return		nativeRenderPasses [ <PySoftimage.xsi.Pass>, <...> ]
		"""	
		return self._findNativeObject("Passes." + displayName)
		
	def _currentNativeRenderPass(self):
		"""
			\remarks	implements the AbstractScene._currentNativeRenderPass that returns the active render pass in the scene	
			\return		<PySoftimage.xsi.Pass> nativeRenderPass
		"""	
		return xsi.ActiveProject.ActiveScene.ActivePass
		
	def _setCurrentNativeRenderPass(self, nativeSceneRenderPass):
		"""
			\remarks	implements the AbstractScene._setCurrentNativeRenderPass method to set the current render pass in the scene			\param		displayName			<str>
			\return		<PySoftimage.xsi.Pass> nativeRenderPass
		"""	
		xsi.SetCurrentPass(nativeSceneRenderPass)
		return True
		
	def _removeNativeRenderPasses(self , nativeRenderPasses):
		"""
			\remarks	implements the AbstractScene._createNativeRenderPass method to create a new Softimage render pass
			\param		displayName			<str>
			\return		<PySoftimage.xsi.Pass> nativeRenderPass
		"""	
		self._removeNativeObjects(nativeRenderPasses)
		return True
		
	def _createNativeRenderPass(self, displayName):
		"""
			\remarks	implements the AbstractScene._createNativeRenderPass method to create a new Softimage render pass
			\param		displayName			<str>
			\return		<PySoftimage.xsi.Pass> nativeRenderPass
		"""
		self.setSilentMode(True)
		renderPass = xsi.CreatePass("", displayName)("Value")
		self.setSilentMode(False)
		return renderPass
		
	def _exportNativeObjectsToFBX(self, nativeObjects, path, frameRange=None, showUI=False):
		"""
			\remarks	exports a given set of nativeObjects as FBX.
			\return		<bool> success
		"""
		
		# Collecting the controllers we want to plot.
		controllers = []
		for nativeObject in nativeObjects:
			transformsGlobal = nativeObject.Kinematics.Global
			transformsLocal = nativeObject.Kinematics.Local
			for transform in [ 'pos', 'rot', 'scl' ]:
				for axis in 'xyz':
					controllerGlobal = transformsGlobal.Parameters(transform + axis)
					controllerLocal = transformsLocal.Parameters(transform + axis)
					if (controllerGlobal and controllerGlobal.IsAnimated()) or (controllerLocal and controllerLocal.isAnimated()):
						controllers.append(controllerLocal)

		# Storing all the stuff we will be doing.
		xsi.OpenUndo("Plotting and Exporting to FBX")

		# Defining the range.
		if frameRange:
			self.setAnimationRange(frameRange)

		# Setting the selection.
		self._setNativeSelection(nativeObjects)
		
		# Plotting.
		if controllers:
			xsi.PlotAndApplyActions(controllers, "plot", frameRange[0], frameRange[1], "", 20, 3, "", "", "", "", True, True)

		# Setting the FBX export options.
		xsi.FBXExportScaleFactor(1)
		xsi.FBXExportGeometries(True)
		xsi.FBXExportSkins(True)
		xsi.FBXExportCameras(True)
		xsi.FBXExportAscii(True)
		xsi.FBXExportLights(True)
		xsi.FBXExportAnimation(True)
		xsi.FBXExportShapes(True)
		xsi.FBXExportFrameRate(self.animationFPS())
		xsi.FBXExportEmbedMedias(False)
		xsi.FBXExportKeepXSIEffectors(False)	
		xsi.FBXExportGroupAsCache(False)	
		xsi.FBXExportDeformerAsSkeleton(False)
		xsi.FBXExportSelection(True)

		# Exporting.
		xsi.FBXExport(path)

		# Restoring the scene state.
		xsi.CloseUndo()
		xsi.Undo("")
		
		return True
		
	def viewports(self):
		"""
			\remarks	implements the AbstractScene.viewports method to return the visible viewports
			\return		[ <blur3d.api.SceneViewport>, ... ]
		"""
		from blur3d.api import SceneViewport
		viewportNames = SceneViewport.viewportNames
		viewportLetters = [ viewportNames[ key ] for key in viewportNames.keys() ]
		viewportLetters = sorted(viewportLetters)
		viewports = []
		viewManager = xsi.Desktop.ActiveLayout.Views('vm')
		for letter in viewportLetters:
			if not viewManager.GetAttributeValue('layout:%s' % letter) == 'hidden':
				number = viewportLetters.index(letter) + 1
				viewports.append(SceneViewport(self, number))
		return viewports
		
	def _createNativeModel(self, name='Model', nativeObjects=[], referenced=False):
		"""
			\remarks	implements the AbstractScene._createNativeModel method to return a new Softimage model
			\param		name			<str>
			\return		<PySoftimage.xsi.Model> nativeModel
		"""
		if referenced:
			model = xsi.CreateEmptyRefModel('', name)
			xsi.RemoveRefModelResolution(model, "res1")
			return  model
		root = self._nativeRootObject()
		fact = xsiFactory.CreateObject('XSI.Collection')
		fact.AddItems(nativeObjects)
		return root.addModel(fact, name)
		
	def _createNativeCamera(self, name='Camera', type='Standard'):
		"""
			\remarks	implements the AbstractScene._createNativeCamera method to return a new Softimage camera
			\param		name			<str>
			\return		<PySoftimage.xsi.Camera> nativeCamera
		"""
		root = self._nativeRootObject()
		return root.addCamera('Camera', name)
		
	def _exportNativeModel(self, nativeModel, path):
		"""
			\remarks	implements the AbstractScene._exportNativeModel method to export a Softimage model
			\param		nativeModel <PySoftimage.xsi.Model>
			\param		path <string>
		"""
		xsi.ExportModel(nativeModel, path, "", "")
		return True
	
	def _isolateNativeObjects(self, nativeObjects):
		selection = self._nativeSelection()
		self._setNativeSelection(nativeObjects)
		xsi.IsolateSelected()
		self._setNativeSelection(selection)
		return True
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def cacheXmesh(self, path, objList, start, end, worldLock, stack=3, saveVelocity=True, ignoreTopology=True):
		"""
			\remarks	runXmesh cache function
			\param		models [ <SceneModel>, ... ]
			\return		<bool> success
		"""
		mesh = xsi.Export_XMesh(objList, stack, start, end, path, worldLock)
		return True
	
	def loadFile(self, filename='' , confirm=True):
		"""
			\remarks	loads the inputed filename into the application, returning true on success
			\param		filename	<str>
			\return		<bool> success
		"""
		xsi.OpenScene(filename, confirm)
		return False
		
	def animationRange(self):
		"""
			\remarks	implements AbstractScene.animationRange method to return the current animation start and end frames
			\return		<blur3d.api.FrameRange>
		"""
		from blur3d.api import FrameRange
		playControl = xsi.ActiveProject.Properties("Play Control")
		return FrameRange([ int(playControl.Parameters("In").Value), int(playControl.Parameters("Out").Value) ])

	def animationFPS(self):
		"""
			\remarks	implements AbstractScene.animationFPS method to return the current frame per second rate.
			\return		<float> fps
		"""
		return float(xsi.ActiveProject.Properties("Play Control").Parameters("Rate").Value)
	
	@classmethod
	def currentFileName(cls):
		"""
			\remarks	implements AbstractScene.currentFileName method to return the current filename for the scene that is active in the application
			\return		<str>
		"""
		return xsi.ActiveProject.ActiveScene.FileName.Value
	
	def currentFrame(self):
		"""
			\remarks	implements AbstractScene.currentFrame method to return the current frame
			\return		<int>
		"""
		return int(xsi.ActiveProject.Properties("Play Control").Parameters("Current").Value)

	def objectsKeyedFrames(self, objects, start=None, end=None):
		frames = []
		for obj in objects:
			frames += obj.keyedFrames(start, end)
		return sorted(list(set(frames)))

	def setCurrentFrame(self, frame):
		"""
			\remarks	implements AbstractScene.setCurrentFrame method to set the current frame
			\return		<bool> success
		"""
		xsi.ActiveProject.Properties("Play Control").Parameters("Current").Value = frame
		return True
	
	def _highlightNativeObjects(self, nativeObjects, color=None, tme=.2, branch=True):

		# Saving the selection in order to retrieve it at the end.
		if self._cache.get('selection') == None:
			self._cache['selection'] = xsiFactory.CreateObject("XSI.Collection")
			self._cache['selection'].AddItems(xsi.Selection)

		pref = xsi.Dictionary.GetObject("Preferences")
		sceneColor = dynDispatch(pref.NestedObjects("Scene Colors"))
		selColor = sceneColor.Parameters("selcol")
		inhColor = sceneColor.Parameters("inhcol")

		self._cache['selColorValue'] = selColor.Value
		self._cache['inhColorValue'] = inhColor.Value

		# If a color is provided we use it.
		if color:
			color = color or QColor(233, 233, 0)
			r = -color.red() << 16
			g = color.green() << 16
			b = color.blue() << 8
			selColor.Value = r | g | b
			inhColor.Value = r | g | b

		# Otherwise we use the selection color.
		else:
			inhColor.Value = self._cache['selColorValue']

		if branch:
			mode = "BRANCH"
		else:
			mode = "ASITIS"

		dispatch.blockSignals(True)
		xsi.SelectObj(nativeObjects, mode)
		dispatch.blockSignals(False)

		xsi.Refresh()
		
		def callback():
			sceneColor = dynDispatch(pref.NestedObjects("Scene Colors"))

			# Revert inital colors.
			sceneColor.Parameters("selcol").Value = self._cache['selColorValue']
			sceneColor.Parameters("inhcol").Value = self._cache['inhColorValue']

			# Retrieve selection.
			dispatch.blockSignals(True)
			xsi.SelectObj(self._cache.get('selection', []))
			dispatch.blockSignals(False)

			# Clearing the cached selection.
			if 'selection' in self._cache:
				del self._cache['selection']

		if self._timer == None:
			self._timer = QTimer(self)
			self._timer.setSingleShot(True)
			self._timer.timeout.connect(callback)

		self._timer.stop()
		self._timer.start(tme * 1000)

		return True

	def clearSelection(self):
		"""
			\remarks	implements AbstractScene.clearSelection method to clear the selection in the scene.
			\return		<bool> success
		"""
		xsi.DeselectAll()
		return True

	def saveFileAs(self, filename=None):
		"""
			\remarks	implements AbstractScene.saveFileAs to save the current scene to the inputed name specified.  If no name is supplied, then the user should be prompted to pick a filename
			\param		filename 	<str>
			\return		<bool> success
		"""
		if not filename:
			from PyQt4.QtGui import QFileDialog
			filename = QFileDialog.getSaveFileName(None, 'Save Scene File', '', 'Scene files (*.scn);;All files (*.*)')
		
		if filename:
			xsi.SaveSceneAs(str(filename))
			return True
		return False
	
	def setAnimationFPS(self, fps, changeType=constants.FPSChangeType.Seconds, callback=None):
		
		"""
			\remarks	Updates the scene's fps to the provided value and scales existing keys as specified.
						If you have any code that you need to run after changing the fps and plan to use it in
						3dsMax you will need to pass that code into the callback argument.
			\param		fps 		<float>
			\param		changeType	<constants.FPSChangeType>	Defaults to constants.FPSChangeType.Frames
			\param		callback	<funciton>					Code called after the fps is changed.
			\return		<bool> success
		"""

		# Storing the ratio of the fps changed.
		ratio = fps / self.animationFPS()
		if ratio != 1.0:

			playControl = xsi.ActiveProject.Properties('Play Control')
			# Only update the change timing if it needs to change
			current = playControl.Parameters('KeepFrameTiming').Value
			if current and changeType == constants.FPSChangeType.Seconds:
				playControl.Parameters('KeepFrameTiming').Value = 0 # seconds
			elif not current and changeType == constants.FPSChangeType.Frames:
				playControl.Parameters('KeepFrameTiming').Value = 1 # frames
			playControl.Parameters('Format').Value = 11 # switch to custom format 
			playControl.Parameters('Rate').Value = fps

			if changeType == constants.FPSChangeType.Seconds:

				# Also converting the current scene range.
				self.setAnimationRange(self.animationRange().multiply(ratio))

			if callback:
				callback()

		return True

	def storeState(self):
		"""
			\remarks	stores the state of the scene.
			\return		<bool> success
		"""
		playControl = xsi.ActiveProject.Properties("Play Control")
		self._state['rangeIn'] = playControl.Parameters("In").Value
		self._state['rangeOut'] = playControl.Parameters("Out").Value
		self._state['rangeGlobalIn'] = playControl.Parameters("GlobalIn").Value
		self._state['rangeGlobalOut']= playControl.Parameters("GlobalOut").Value
		self._state['loop'] = playControl.Parameters("Loop").Value
		return True
	
	def renderSize(self):
		"""
			\remarks	return the render output size for the scene
			\return		<QSize>
		"""
		from PyQt4.QtCore import QSize
		return QSize(xsi.GetValue("Passes.RenderOptions.ImageWidth"), xsi.GetValue("Passes.RenderOptions.ImageHeight"))
	
	def restoreState(self):
		"""
			\remarks	restores the state of the scene based on previously stored state.
			\return		<bool> success
		"""
		playControl = xsi.ActiveProject.Properties("Play Control")
		playControl.Parameters("In").Value = self._state.get('rangeIn', 0)
		playControl.Parameters("Out").Value = self._state.get('rangeOut', 100)
		playControl.Parameters("GlobalIn").Value = self._state.get('rangeGlobalIn', 0)
		playControl.Parameters("GlobalOut").Value = self._state.get('rangeGlobalOut', 100)
		playControl.Parameters("Loop").Value = self._state.get('loop', False)
		return True

	def reset(self, silent=False):
		"""
			\remarks	implements AbstractScene.reset to reset this scene for all the data and in the application
			\return		<bool> success
		"""
		prompt = not silent
		xsi.NewScene('', prompt)
		return True
			
	def setAnimationRange(self, animationRange, globalRange=None):
		"""
			\remarks	implements AbstractScene.setAnimationRange method to set the current start and end frame for animation
			\param		animationRange	<tuple> ( <int> start, <int> end )
			\return		<bool> success
		"""
		if not globalRange:
			globalRange = animationRange
			
		playControl = xsi.ActiveProject.Properties("Play Control")
		playControl.Parameters("In").Value = animationRange[0]
		playControl.Parameters("Out").Value = animationRange[1]
		playControl.Parameters("GlobalIn").Value = globalRange[0]
		playControl.Parameters("GlobalOut").Value = globalRange[1]
		return True
	
	def setRenderSize(self, size):
		"""
			\remarks	set the render output size for the scene
			\param		size	<QSize>
			\return		<bool> success
		"""
		from PyQt4.QtCore import QSize
		if isinstance(size, QSize):
			width = size.width()
			height = size.height()
		elif isinstance(size, list):
			if len(size) < 2:
				raise TypeError('You must provide a width and a height when setting the render size using a list')
			width = size[0]
			height = size[1]
		xsi.SetValue("Passes.RenderOptions.ImageWidth", width)
		xsi.SetValue("Passes.RenderOptions.ImageHeight", height)
		return True
	
	def snapKeysToNearestFrames(self):
		for curve in [fcv for fcv in xsi.FindObjects(None, "{E2A86051-F669-11D1-8D60-080036F3CC02}") if not fcv.Locked]:
			try:
				curve.SnapToNearestFrame()
			except:
				pass
		return True

	def setRotation(self, objects, axes, relative=False):
		"""
		Rotates the provided objects in the scene
		:param objects: Rotate these objects
		:param axes: A list with a length of 3 floats representing x, y, z
		:param relative: Apply the rotation as relative or absolute. Absolute by default.
		"""
		relative = {True:'siRelative', False:'siAbsolute'}[relative]
		xsi.Rotate([obj.nativePointer() for obj in objects], axes[0], axes[1], axes[2], relative)
	
	def setSilentMode(self, switch):
		"""
			\remarks	implements AbstractScene.setSilentMode method to make the application silent during intense calls.
			\param		switch	<bool>
			\return		<bool> success
		"""
		if switch:
			if not self._buffer.get('silentMode', None):
				self._buffer['silentMode'] = {}
				self._buffer['silentMode']['cmdlog'] = xsi.GetValue("preferences.scripting.cmdlog")
				self._buffer['silentMode']['msglogverbose'] = xsi.GetValue("preferences.scripting.msglogverbose")
				self._buffer['silentMode']['msglogrealtime'] = xsi.GetValue("preferences.scripting.msglogrealtime")
				self._buffer['silentMode']['autoinspect'] = xsi.GetValue("preferences.Interaction.autoinspect")
				
			xsi.SetValue("preferences.scripting.cmdlog", False, "")
			xsi.SetValue("preferences.scripting.msglogverbose", False, "")
			xsi.SetValue("preferences.scripting.msglogrealtime", False, "")
			xsi.SetValue("preferences.Interaction.autoinspect", False, "")
		else:
			if self._buffer.get('silentMode', None):
				xsi.SetValue("preferences.scripting.cmdlog", self._buffer['silentMode']['cmdlog'], "")
				xsi.SetValue("preferences.scripting.msglogverbose", self._buffer['silentMode']['msglogverbose'], "")
				xsi.SetValue("preferences.scripting.msglogrealtime", self._buffer['silentMode']['msglogrealtime'], "")
				xsi.SetValue("preferences.Interaction.autoinspect", self._buffer['silentMode']['autoinspect'], "")
				del self._buffer['silentMode']
		return True
			
	def retime(self, offset, scale=1, activeRange=None, pivot=None):
		if activeRange:
			if not pivot:
				pivot = activeRange[0]
		else:
			activeRange = (-9999, 9999)
			if not pivot:
				pivot = 1
		xsi.SISequence("", "siAllAnimParams", offset, scale, activeRange[0], activeRange[1], activeRange[0], "siFCurvesAnimationSources")
		return True	
		
	def setTimeControlPlay(self, switch, fromStart=False):
		if switch:
			if fromStart:
			    xsi.PlayRealTimeFromStart()
			else:
				xsi.PlayRealTime()
		else:
			xsi.PlaybackStop()
		return True
			
	def setTimeControlLoop(self, switch):
		playControl = xsi.ActiveProject.Properties("Play Control")
		playControl.Parameters("Loop").Value = switch
		return True
	
	def translate(self, objects, axes, relative=False):
		"""
		Translates the objects in the scene
		:param objects: Translate these objects
		:param axes: A list with a length of 3 floats representing x, y, z
		:param relative: Apply the translation as relative or absolute. Absolute by default.
		"""
		relative = {True:'siRelative', False:'siAbsolute'}[relative]
		xsi.Translate([obj.nativePointer() for obj in objects], axes[0], axes[1], axes[2], relative)
	
	def isTimeControlLoop(self):
		playControl = xsi.ActiveProject.Properties("Play Control")
		return playControl.Parameters("Loop").Value
		
	def undo(self):
		"""
			\remarks	undos the last action.
			\return		<bool>
		"""
		xsi.Undo('')
		return True
	
# register the symbol
from blur3d import api
api.registerSymbol('Scene', SoftimageScene)
