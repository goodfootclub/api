from functools import wraps
from types import FunctionType

from rest_framework.viewsets import ModelViewSet


class ActionDocViewsetMeta(type):
    """
    When rendering viewset in the Browsable API use action's docstring
    instead of one that belongs to class if possible.
    (only for list and retrieve actions)
    """
    # FIXME:
    # A race condition happen with OPTIONS that gives you a random
    # docstring I'll check later to see if there is a better solution
    # or just remove this from this code...
    def __new__(cls, name, bases, namespace, **kwds):
        classdoc = namespace['__doc__'] = namespace.get('__doc__', '')

        def wrap(action):
            if type(action) is not FunctionType:
                return action

            @wraps(action)
            def _(obj, *args, **kwargs):
                obj.__class__.__doc__ = getattr(action, '__doc__', classdoc)
                return action(obj, *args, **kwargs)

            return _

        for action in ['list', 'retrieve']:
            if action in namespace:
                namespace[action] = wrap(namespace[action])

        return type.__new__(cls, name, bases, namespace)


class AppViewSet(ModelViewSet, metaclass=ActionDocViewsetMeta):
    """
    Django REST Framework's ModelViewSet on steroids:

    a). You can specify different serializers for different actions
        like this:

        MyViewSet(AppViewSet):
            serializer_classes = {
               'list': MyListSerializer,
               'create': MyCreateSerializer,
               ...
            }

    b). Switch action method docstring with a class docstring for
        rendering documentation in the Browsable API
    """
    def get_serializer_class(self):
        try:
            return self.serializer_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()
