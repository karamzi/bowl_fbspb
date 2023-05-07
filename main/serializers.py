from rest_framework import serializers
from main.models import CalendarModel


class CalendarSerializer(serializers.ModelSerializer):
    regulation = serializers.SerializerMethodField()

    def get_regulation(self, obj: CalendarModel):
        if obj.regulation:
            return obj.regulation.document.url
        return ''

    class Meta:
        model = CalendarModel
        fields = ['id', 'competition', 'city', 'status', 'date_start', 'date_finish', 'regulation']
        depth = 0
