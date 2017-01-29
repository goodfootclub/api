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
    'RsvpDetailsSerializer',
    'RsvpListCreateSerializer',
    'RsvpSerializer',
]


class RsvpSerializer(ModelSerializer):
    rsvp = ChoiceField(RsvpStatus.RSVP_CHOICES, source='status')
    rsvp_id = ReadOnlyField(source='id')

    class Meta:
        model = RsvpStatus
        fields = 'rsvp_id', 'rsvp',

    def to_representation(self, obj):
        data = super().to_representation(obj)
        request = self.context.get('request', None)
        if request and request.accepted_renderer.format == 'api':
            data['url'] = reverse(
                'game-rsvp',
                (self.context['view'].kwargs['game_id'], obj.id),
                request=request
            )
        return data

    def create(self, validated_data):
        if 'game_id' not in validated_data:
            validated_data.update(self.context['view'].kwargs)
        try:
            return super().create(validated_data)
        except IntegrityError as e:
            raise RelationAlreadyExist(
                detail=e.args[0].split('DETAIL:  ')[1]
            )


class RsvpListCreateSerializer(RsvpSerializer):
    id = IntegerField(source='player_id')

    class Meta(RsvpSerializer.Meta):
        fields = 'id', 'rsvp_id', 'rsvp', 'team'


class RsvpDetailsSerializer(RsvpListCreateSerializer):

    first_name = ReadOnlyField(source='player.first_name')
    last_name = ReadOnlyField(source='player.last_name')
    img = ImageField(source='player.img', read_only=True)

    class Meta(RsvpListCreateSerializer.Meta):
        fields = RsvpListCreateSerializer.Meta.fields + (
            'first_name', 'last_name', 'img'
        )
