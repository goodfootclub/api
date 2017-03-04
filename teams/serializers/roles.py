from django.db import IntegrityError

from rest_framework.reverse import reverse
from rest_framework.serializers import (
    ImageField,
    IntegerField,
    ModelSerializer,
    ReadOnlyField,
)

from main.exceptions import RelationAlreadyExist
from ..models import Role


__all__ = ['RoleSerializer']


class RoleSerializer(ModelSerializer):

    role_id = ReadOnlyField(source='id')
    id = ReadOnlyField(source='player_id')
    first_name = ReadOnlyField(source='player.first_name')
    last_name = ReadOnlyField(source='player.last_name')
    img = ImageField(source='player.img', read_only=True)

    class Meta:
        model = Role
        fields = 'id', 'role', 'role_id', 'first_name', 'last_name', 'img'

    def to_representation(self, obj):
        data = super().to_representation(obj)
        request = self.context.get('request', None)

        if request and request.accepted_renderer.format == 'api':
            try:
                data['url'] = reverse(
                    'team-role-detail',
                    (obj.team_id, obj.id),
                    request=request
                )
            except KeyError:
                pass
        return data

    def create(self, validated_data):
        if 'team_id' not in validated_data:
            validated_data.update(self.context['view'].kwargs)
        try:
            return super().create(validated_data)
        except IntegrityError as e:
            raise RelationAlreadyExist(
                detail=e.args[0].split('DETAIL:  ')[1]
            )
