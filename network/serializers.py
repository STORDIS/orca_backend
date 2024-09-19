from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from network.models import ReDiscoveryConfig


class ReDiscoveryConfigSerializer(serializers.ModelSerializer):
    device_ip = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=ReDiscoveryConfig.objects.all())]
    )

    class Meta:
        model = ReDiscoveryConfig
        fields = ['device_ip', 'interval', 'last_discovered', 'feature']

    def create(self, validated_data):
        device_id = validated_data.get('device_ip')
        config_data = validated_data.get('config_data')

        # Create or update the device config
        obj, created = ReDiscoveryConfig.objects.update_or_create(
            device_id=device_id,
            defaults={'config_data': config_data}
        )

        return obj

    def update(self, instance, validated_data):
        instance.config_data = validated_data.get('config_data', instance.config_data)
        instance.save()
        return instance
