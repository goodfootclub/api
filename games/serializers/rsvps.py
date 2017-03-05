from rest_framework.reverse import reverse
from rest_framework.serializers import (
    ChoiceField,
    ImageField,
    IntegerField,
    ModelSerializer,
    ReadOnlyField,
)
from ..models import RsvpStatus


__all__ = [
    'RsvpCreateSerializer',
    'RsvpSerializer',
]


class RsvpSerializer(ModelSerializer):
    id = ReadOnlyField(source='player_id')
    rsvp = ChoiceField(RsvpStatus.RSVP_CHOICES, source='status')
    rsvp_id = ReadOnlyField(source='id')
    first_name = ReadOnlyField(source='player.first_name')
    last_name = ReadOnlyField(source='player.last_name')
    img = ImageField(source='player.img', read_only=True)

    class Meta:
        model = RsvpStatus
        fields = 'id', 'rsvp_id', 'rsvp', 'first_name', 'last_name', 'img'

    def to_representation(self, obj):
        data = super().to_representation(obj)
        request = self.context.get('request', None)
        if request and request.accepted_renderer.format == 'api':
            data['url'] = reverse(
                'rsvp-detail',
                (obj.game_id, obj.id),
                request=request
            )
        return data


class RsvpCreateSerializer(RsvpSerializer):
    id = IntegerField(source='player_id')

    class Meta(RsvpSerializer.Meta):
        fields = 'id', 'rsvp_id', 'rsvp', 'team'

    def create(self, validated_data):
        validated_data['game_id'] = self.context['view'].kwargs['game_pk']
        try:
            return super().create(validated_data)
        except IntegrityError as e:
            raise RelationAlreadyExist(
                detail=e.args[0].split('DETAIL:  ')[1]
            )
