from rest_framework import serializers
from rest_framework.serializers import ValidationError
from synrate_main.models import Offer
from .models import ENGINE, Parser


class OfferSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance.error = validated_data.get('message', instance.error)
        instance.message = validated_data.get('error', instance.message)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.unique_code = validated_data.get('unique_code', instance.unique_code)
        instance.status = validated_data.get('status', instance.status)\

        instance.save()
        return instance


    class Meta:
        model = Offer
        fields = ('pk',
                  'name',
                  'home_name',
                  'url',
                  'location',
                  'offer_type',
                  'offer_start_date',
                  'offer_end_date',
                  'owner',
                  'ownercontact',
                  'offer_price',
                  'additional_data',
                  'category',
                  'organisation',
                  'from_id',
                  'short_cat')

    def validate(self, attrs):
        group = Offer.objects.filter(url=attrs['url'])
        for offer in group:
            if offer.name == attrs['name']:
                raise ValidationError({"answer": "not uniq offer"})
        if attrs["name"] is None or attrs["name"] == "":
            raise ValidationError("Поле name обязательно должно быть заполнено")

        return attrs


class ParserSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        instance.error = validated_data.get('message', instance.error)
        instance.message = validated_data.get('error', instance.message)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.unique_code = validated_data.get('unique_code', instance.unique_code)
        instance.status = validated_data.get('status', instance.status)
        instance.time_started = validated_data.get('time_started', instance.time_started)
        instance.offers_parsed = validated_data.get('offers_parsed', instance.message)

        instance.save()
        return instance

    class Meta:
        model = Parser
        fields = ('pk', 'name', 'text', 'unique_code', 'status', 'time_started', 'offers_parsed', 'message', 'error')


class EngineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ENGINE
        fields = ('pk', 'name', 'text', 'unique_code', 'status', 'message', 'error')
