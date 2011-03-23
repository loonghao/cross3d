##
#	\namespace	blur3d.api.abstract.abstractscenewrapper
#
#	\remarks	The AbstractSceneWrapper class defines the base class for all other scene wrapper instances.  This creates a basic wrapper
#				class for mapping native object instances from a DCC application to the blur3d structure
#
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

class AbstractSceneWrapper:
	def __eq__( self, other ):
		"""
			\remarks	compares this instance to another object
			\param		other	<variant>
			\return		<bool> equal
		"""
		if ( isinstance( other, AbstractSceneWrapper ) ):
			return other._nativePointer == self._nativePointer
		return False
		
	def __init__( self, scene, nativePointer = None ):
		"""
			\remarks	initialize the abstract scene controller
		"""
		self._scene				= scene
		self._nativePointer		= nativePointer
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _nativeControllers( self ):
		"""
			\remarks	[abstract] collect a list of the native controllers that are currently applied to this cache instance
			\return		<list> [ <variant> nativeController, .. ]
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError

		return []
	
	def _nativeController( self, name ):
		"""
			\remarks	[abstract] find a controller for this object based on the inputed name
			\param		name		<str>
			\return		<variant> nativeController || None
		"""
		from blurdev import debug
				
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError

		return None
	
	def _nativeCopy( self ):
		"""
			\remarks	[abstract] return a native copy of the instance in the scene
			\return		<variant> nativePointer || None
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError

		return None
		
	def _nativeProperty( self, key, default = None ):
		"""
			\remarks	[abstract] return the value of the property defined by the inputed key
			\sa			hasProperty, setProperty, _nativeProperty, AbstractScene._fromNativeValue
			\param		key			<str>
			\param		default		<variant>	(auto-converted from the application's native value)
			\return		<variant>
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return default
	
	def _setNativeController( self, name, nativeController ):
		"""
			\remarks	[abstract] find a controller for this object based on the inputed name
			\param		name		<str>
			\param		<variant> nativeController || None
			\return		<bool> success
		"""
		from blurdev import debug
				
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError

		return False
		
	def _setNativeProperty( self, key, nativeValue ):
		"""
			\remarks	[abstract] set the value of the property defined by the inputed key
			\sa			hasProperty, property, setProperty, AbstractScene._toNativeValue
			\param		key		<str>
			\param		value	<variant>	(pre-converted to the application's native value)
			\retrun		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def copy( self ):
		"""
			\remarks	create a copy of this wrapper in the scene
			\return		<blur3d.api.SceneWrapper> || None
		"""
		nativeCopy = self._nativeCopy()
		if ( nativeCopy ):
			return self.__class__( self._scene, nativeCopy )
		return None
		
	def controllers( self ):
		"""
			\remarks	return a list of SceneAnimationControllers that are linked to this object and its properties
			\return		<list> [ <blur3d.api.SceneAnimationController> control, .. ]
		"""
		from blur3d.api import SceneAnimationController
		return [ SceneAnimationController( self, nativeController ) for nativeController in self._nativeControllers ]
		
	def controller( self, name ):
		"""
			\remarks	lookup a controller based on the inputed controllerName for this object
			\param		controllerName		<str>
			\return		<blur3d.api.SceneAnimationController> || None
		"""
		nativeController = self._nativeController( name )
		if ( nativeController ):
			from blur3d.api import SceneAnimationController
			return SceneAnimationController( self._scene, nativeController )
		return None

	def hasProperty( self, key ):
		"""
			\remarks	[abstract] check to see if the inputed property name exists for this controller
			\sa			property, setProperty
			\param		key		<str>
			\return		<bool> found
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def name( self ):
		"""
			\remarks	[abstract] return the name of this controller instance
			\sa			setControllerName
			\return		<str> name
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return ''
	
	def nativePointer( self ):
		"""
			\remarks	return the pointer to the native controller instance
			\return		<variant> nativeController
		"""
		return self._nativePointer
	
	def property( self, key, default = None ):
		"""
			\remarks	return the value of the property defined by the inputed key
			\sa			hasProperty, setProperty, _nativeProperty
			\param		key			<str>
			\param		default		<variant>		the default value to return if the property is not found
			\return		<variant>
		"""
		return self._scene._fromNativeValue( self._nativeProperty( key, default ) )
	
	def propertyNames( self ):
		"""
			\remarks	[abstract] return a list of the property names linked to this instance
			\return		<list> [ <str> propname, .. ]
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def recordXml( self, xml ):
		"""
			\remarks	define a way to record this controller to xml
			\param		xml		<blurdev.XML.XMLElement>
			\return		<bool> success
		"""
		if ( not xml ):
			return False
		
		xml.setAttribute( 'name', 	self.name() )
		xml.setAttribute( 'id', 	self.uniqueId() )
		return True
	
	def scene( self ):
		"""
			\remarks	return the scene instance that this wrapper instance is linked to
			\return		<blur3d.api.Scene>
		"""
		return self._scene
	
	def setController( self, name, controller ):
		"""
			\remarks	lookup a controller based on the inputed controllerName for this object
			\param		name				<str>
			\param		controller			<blur3d.api.SceneAnimationController> || None
			\return		<bool> success
		"""
		nativeController = None
		if ( controller ):
			nativeController = controller.nativePointer()
		return self._setNativeController( name, nativeController )
		
	def setName( self, name ):
		"""
			\remarks	[abstract] set the name of this wrapper instance
			\sa			name
			\param		name	<str>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def setUniqueId( self, uniqueId ):
		"""
			\remarks	[abstract] set the unique id for this wrapper instance
			\sa			uniqueId
			\param		uniqueId <int>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
		
	def setProperty( self, key, value ):
		"""
			\remarks	set the value of the property defined by the inputed key
			\sa			hasProperty, property, _setNativeProperty
			\param		key		<str>
			\param		value	<variant>
			\retrun		<bool> success
		"""
		return self._setNativeProperty( key, self._scene._toNativeValue( value ) )
	
	def uniqueId( self ):
		"""
			\remarks	[abstract] return the unique id for this controller instance
			\sa			setControllerId
			\return		<int> id
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return 0
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												static/class methods
	#------------------------------------------------------------------------------------------------------------------------
	@classmethod
	def fromXml( cls, scene, xml ):
		"""
			\remarks	[abstract] create a new wrapper instance from the inputed xml data
			\param		xml		<blurdev.XML.XMLElement>
			\return		
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return 0
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneWrapper', AbstractSceneWrapper, ifNotFound = True )