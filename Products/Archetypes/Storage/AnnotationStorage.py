from Products.Archetypes.interfaces.storage import IStorage
from Products.Archetypes.interfaces.layer import ILayer
from Products.Archetypes.debug import log
from Products.Archetypes.Storage.BaseStorage import Storage, StorageLayer, _marker
from Products.Archetypes.ATAnnotations import AT_ANN_STORAGE, AT_MD_STORAGE

from Acquisition import aq_base

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import setSecurity, registerStorage

class BaseAnnotationStorage(Storage):
    """Stores data using annotations on the instance
    """

    __implements__ = IStorage
    
    security = ClassSecurityInfo()
    
    _key = None
    
    security.declarePrivate('get')
    def get(self, name, instance, **kwargs):
        ann = instance.getAnnotation()
        value = ann.getSubkey(self._key, default=_marker, subkeys=name)
        if value is _marker:
            raise AttributeError(name)
        return value

    security.declarePrivate('set')
    def set(self, name, instance, value, **kwargs):
        # Remove acquisition wrappers
        value = aq_base(value)
        ann = instance.getAnnotation()
        ann.setSubkey(self._key, value, subkeys=name)

    security.declarePrivate('unset')
    def unset(self, name, instance, **kwargs):
        ann = instance.getAnnotation()
        try:
            ann.delSubkey(self._key, subkeys=name)
        except KeyError:
            pass

setSecurity(BaseAnnotationStorage)

class AnnotationStorage(BaseAnnotationStorage):
    """Stores values as ATAnnotations on the object
    """
    
    _key = AT_ANN_STORAGE
    
    security = ClassSecurityInfo()
    
class MetadataAnnotationStorage(BaseAnnotationStorage, StorageLayer):
    """Stores metadata as ATAnnotations on the object
    """
    
    _key = AT_MD_STORAGE
    
    security = ClassSecurityInfo()
    
    __implements__ = IStorage, ILayer

    security.declarePrivate('initializeInstance')
    def initializeInstance(self, instance, item=None, container=None):
        # annotations are initialized on first access
        pass

    security.declarePrivate('initializeField')
    def initializeField(self, instance, field):
        # Check for already existing field to avoid  the reinitialization
        # (which means overwriting) of an already existing field after a
        # copy or rename operation
        ann = instance.getAnnotation()
        if not ann.hasSubkey(self._key, subkeys=field.getName()):
            self.set(field.getName(), instance, field.getDefault(instance))


__all__ = ('AnnotationStorage', 'MetadataAnnotationStorage', )

#for name in __all__:
#    storage = locals()[name]
#    registerStorage(storage)
