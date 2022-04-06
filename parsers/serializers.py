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
                raise ValidationError({"unique_error": f"{offer.pk}"})
        if attrs["name"] is None or attrs["name"] == "":
            raise ValidationError("Поле name обязательно должно быть заполнено")

        return attrs


class OfferUpdateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    def update(self, instance, validated_data):
        instance.offer_price = validated_data['offer_price']
        instance.owner = validated_data['owner']
        instance.additional_data = validated_data['additional_data']
        instance.location = validated_data['location']
        instance.offer_type = validated_data['offer_type']
        instance.offer_start_date = validated_data['offer_start_date']
        instance.offer_end_date = validated_data['offer_end_date']
        instance.ownercontact = validated_data['ownercontact']
        instance.organisation = validated_data['organisation']
        instance.from_id = validated_data['from_id']
        instance.short_cat = validated_data['short_cat']
        instance.save()
        return instance

    class Meta:
        model = Offer
        fields = ("id", 'offer_price', 'owner', 'additional_data', 'location', 'offer_type',
                  "offer_start_date", "offer_end_date", 'ownercontact', 'organisation', 'from_id',
                  "short_cat",)


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
