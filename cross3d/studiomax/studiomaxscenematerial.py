##
#	\namespace	blur3d.api.abstract.abstractscenematerial
#
#	\remarks	3ds Max implementation of SceneMaterial.
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

import os.path
from Py3dsMax import mxs
from blur3d.constants import MaterialType, MapType
from blur3d.api.abstract.abstractscenematerial import AbstractSceneMaterial
from blur3d.api import Scene

# =============================================================================
# CLASSES
# =============================================================================

class StudiomaxSceneMaterial(AbstractSceneMaterial):
	def _nativeSubmaterials(self):
		"""The native submaterials of this material."""
		mtl	= self._nativePointer
		# Processing multi/sub materials directly is faster than the getnumsubs
		# system.
		if mxs.classof(mtl) == mxs.MultiMaterial:
			return [mtl[i] for i in range(mtl.numsubs)]
		else:
			# Process all other kinds of materials.
			get_submtl = mxs.getSubMtl
			return [get_submtl(mtl, i+1) for i in range(mxs.getNumSubMtls(mtl))]

	def edit(self):
		"""Launches the native material edit dialog for this material."""
		medit = mxs.medit
		medit.PutMtlToMtlEditor(self._nativePointer, medit.GetActiveMtlSlot())
		mxs.matEditor.open()

	@classmethod
	def fromDictionary(
			self,
			dictionary,
			materialType=MaterialType.Generic,
			mapType=MapType.Generic,
		):
		"""Creates a new material from the given dictionary.

		A new material is created from the description provided in the given
		dictionary.  For more information on the structure of the dictionary
		expected, please see the documentation for AbstractSceneMaterial.__iter__.

		Args:
			dictionary(dict): The dictionary containing the material description.
			materialType(blur3d.constants.MaterialType): The type of material to
				create.  Default is MaterialType.Generic.
			mapType(blur3d.constants.MapType): The type of map to use.  Default
				if MapType.Generic.

		Returns:
			StudiomaxSceneMaterial
		"""
		name = dictionary.get('name', None)
		maps = dictionary.get('maps', dict())
		objects = dictionary.get('objects', [])
		if materialType & MaterialType.VRay:
			mtl = mxs.VRayMtl()
			propMap = dict(
				diffuse='texmap_diffuse',
			)
		else:
			mtl = mxs.StandardMaterial()
			propMap = dict(
				diffuse='diffuseMap',
			)
		if name:
			mtl.name = name
		# We'll keep a running tab of loaders and reuse those that
		# point to the same files.  We can also go ahead and pull
		# the existing loaders of the correct type from the scene
		# so that we can potentially reuse those, as well.
		mapRefs = dict()
		if mapType & MapType.VRay:
			for bm in mxs.getClassInstances(mxs.vrayhdri):
				mapPath = bm.HDRIMapName
				if mapPath:
					mapRefs[mapPath] = bm
		else:
			for bm in mxs.getClassInstances(mxs.bitmaptex):
				mapPath = bm.fileName
				if mapPath:
					mapRefs[mapPath] = bm
		for prop, mapPath in maps.iteritems():
			if prop in propMap:
				# If a loader already exists for this map, then use
				# that rather than constructing a duplicate.
				if mapPath in mapRefs:
					bitmap = mapRefs[mapPath]
				elif mapType & MapType.VRay:
					bitmap = mxs.vrayhdri()
					bitmap.HDRIMapName = mapPath
					mapRefs[mapPath] = bitmap
				else:
					bitmap = mxs.bitmaptex()
					bitmap.fileName = mapPath
					mapRefs[mapPath] = bitmap
				bitmap.name = os.path.basename(mapPath) + '_{}'.format(prop)
				mtl.setProperty(propMap[prop], bitmap)
		# If we have a list of object names that the material
		# should be assigned to, get the object by name and do so.
		for objName in objects:
			obj = mxs.getNodeByName(objName)
			if obj:
				obj.material = mtl
		return StudiomaxSceneMaterial(self._scene, mtl)
	
	def name(self):
		"""The name of this material."""
		return self._nativePointer.name
	
	def setName(self, name):
		"""Sets the name of this material.

		Args:
			name(str): The new material name.
		"""
		self._nativePointer.name = name
		
	def uniqueId(self):
		"""The unique ID of this material."""
		return mxs.blurUtil.uniqueId(self._nativePointer)
	
from blur3d import api
api.registerSymbol('SceneMaterial', StudiomaxSceneMaterial)




