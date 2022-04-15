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
                  'short_cat', "owner_id",)

    # owner_id передают только парсеры вк. поэтому заявки с ним проверяем по методу для вк заявок
    def validate(self, attrs):
        if attrs['home_name'] == 'tenderpro':
            group = Offer.objects.filter(home_name='tenderpro')
            for y in group:
                if y.name == attrs['name']:
                    raise ValidationError({"not_unique": "Error in tenderpro validation"})
            return attrs
        vk = False
        try:
            owner_id = attrs['owner_id']
            vk = True
        except Exception as ex:
            print(ex)
        if vk:
            group = Offer.objects.filter(owner_id=owner_id)
            for offer in group:
                if offer.additional_data == attrs['additional_data']:
                    raise ValidationError({"vk_validation_mode": "Описание заявки не уникально"})
        else:
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
        try:
            instance.offer_price = validated_data['offer_price']
        except:
            pass
        try:
            instance.owner = validated_data['owner']
        except:
            pass
        try:
            instance.additional_data = validated_data['additional_data']
        except:
            pass
        try:
            instance.location = validated_data['location']
        except:
            pass
        try:
            instance.offer_type = validated_data['offer_type']
        except:
            pass
        try:
            instance.offer_start_date = validated_data['offer_start_date']
        except:
            pass
        try:
            instance.offer_end_date = validated_data['offer_end_date']
        except:
            pass
        try:
            instance.ownercontact = validated_data['ownercontact']
        except:
            pass
        try:
            instance.organisation = validated_data['organisation']
        except:
            pass
        try:
            instance.from_id = validated_data['from_id']
        except:
            pass
        try:
            instance.short_cat = validated_data['short_cat']
        except:
            pass
        try:
            instance.save()
        except:
            pass
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
