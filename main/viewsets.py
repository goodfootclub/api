from rest_framework.viewsets import ModelViewSet


class AppViewSet(ModelViewSet):
    """
    Customised Django REST Framework's ModelViewSet:

    Can specify different serializers for different actions like this:

        MyViewSet(AppViewSet):
            serializer_classes = {
               'list': MyListSerializer,      # list action serializer
               'create': MyCreateSerializer,  # create action serializer
               ...
            }
            serializer_class = MyOtherSerializer  # the default serializer
    """
    def get_serializer_class(self):
        try:
            return self.serializer_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()
