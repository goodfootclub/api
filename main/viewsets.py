from rest_framework.viewsets import ModelViewSet


class AppViewSet(ModelViewSet):
    """
    DRF ModelViewSet, but you can specify different serializers
    for different actions like this:

    MyViewSet(AppViewSet):
        serializer_classes = {
           'list': MyListSerializer,
           'create': MyCreateSerializer,
           ...
        }
    """
    def get_serializer_class(self):
        try:
            return self.serializer_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()
