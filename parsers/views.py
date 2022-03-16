from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.http import HttpResponse
from django.core.serializers import serialize
import requests
import datetime
from django.apps import apps
from django.db import IntegrityError
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import OfferSerializer, ParserSerializer, EngineSerializer
from .models import Parser, ENGINE
from synrate_main.models import OfferCategory, OfferSubcategory
Offer = apps.get_model('synrate_main', 'Offer')


class OfferListView(ListAPIView):
    """
        Вьюшка апишки для вывода списка объяв
    """
    model = Offer
    serializer_class = OfferSerializer
    queryset = Offer.objects.all()


class OfferCreateView(CreateAPIView):
    """
            Вьюшка апишки для создания объяв
    """
    model = Offer
    serializer_class = OfferSerializer

    def post(self, request, *args, **kwargs):
        try:
            x = OfferSubcategory.objects.get(name=request.data["subcategory"])
            del request.data["category"]
            request.data["category"] = x.id
            del request.data["subcategory"]
        except:
            try:
                x = OfferCategory.objects.get(name=request.data["category"])
                subcategory = OfferSubcategory(name=request.data["subcategory"], category=x)
                subcategory.save()
                del request.data["category"]
                request.data["category"] = subcategory.id
                del request.data["subcategory"]
            except:
                category = OfferCategory(name=request.data["category"])
                category.save()
                subcategory = OfferSubcategory(name=request.data["subcategory"], category=category)
                del request.data["category"]
                request.data["category"] = subcategory.id
                del request.data["subcategory"]
        return self.create(request, *args, **kwargs)


class ParserListView(ListAPIView):
    model = Parser
    serializer_class = ParserSerializer
    queryset = Parser.objects.all()


class ParserUpdateView(APIView):
    """
            Вьюшка апишки для обновления общения парсера
    """

    def get(self, request, pk):
        kek = Parser.objects.get(id=pk)
        data = data = {"name": kek.name, "text":kek.text, "unique_code":kek.unique_code, "status":kek.status,
                       "message":kek.message, "error":kek.error, "time_started": kek.time_started,
                       "offers_parsed": kek.offers_parsed}
        return Response(data)

    def post(self, request, pk):
        saved_parser = Parser.objects.get(unique_code=pk)
        data = request.data.get('parser')
        serializer = ParserSerializer(instance=saved_parser, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            parser_updated = serializer.save()
        return Response({"success": "Parser '{}' updated successfully".format(parser_updated.name)})


class EngineListView(ListAPIView):
    """
                Вьюшка апишки для общения движка
    """
    model = ENGINE
    serializer_class = ParserSerializer
    queryset = ENGINE.objects.all()


class EngineUpdateView(APIView):
    """
            Вьюшка апишки для общения движка
    """

    def get(self, request, pk):
        kek = ENGINE.objects.get(id=pk)
        data = {"name": kek.name, "text":kek.text, "unique_code":kek.unique_code, "status":kek.status,
                "message":kek.message, "error":kek.error}
        return Response(data)

    def post(self, request, pk):
        saved_engine = ENGINE.objects.get(id=pk)
        data = request.data.get('engine')
        serializer = EngineSerializer(instance=saved_engine, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            engine_updated = serializer.save()
        return Response({"success": "ENGINE '{}' updated successfully".format(engine_updated.name)})
