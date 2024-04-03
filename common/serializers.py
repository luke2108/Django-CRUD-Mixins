from rest_framework import serializers

from common.models import Area, Status


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'


class MyQueryParamSerializer(serializers.Serializer):
    my_name = serializers.CharField()
    my_number = serializers.IntegerField(help_text="Some custom description for the number")
    my_bool = serializers.BooleanField()