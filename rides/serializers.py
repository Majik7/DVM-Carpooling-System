from rest_framework import serializers
from .models import CarpoolRequest

# serializers convert python objs into json
class CarpoolRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarpoolRequest
        fields = ['id', 'passenger', 'pickup_node', 'dropoff_node', 'status']