import csv
from django.http import HttpResponse
from rest_framework import viewsets, mixins, status

from common.models import Area, Status

from .serializers import AreaSerializer, MyQueryParamSerializer, StatusSerializer
from django.urls import include, path
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class CRUDViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    pass

class AreaViewSet(CRUDViewSet):
    http_method_names = ["get", "post", "put", "delete"]
    queryset = Area.objects.all()
    serializer_class = AreaSerializer

class StatusViewSet(CRUDViewSet):
    http_method_names = ["get", "post", "put", "delete"]
    queryset = Status.objects.all()
    serializer_class = StatusSerializer

class ExportDataViewSet(viewsets.GenericViewSet):
    serializer_classes = {
        'area': AreaSerializer,
        'status': StatusSerializer,
    }
    http_method_names = ["get"]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'model_name',
                openapi.IN_QUERY,
                description="Model Name",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    def list(self, request):
        model_name = request.query_params.get('model_name', None)
        if model_name not in self.serializer_classes:
            return Response({'error': 'Invalid model name'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset(model_name)
        serializer_class = self.serializer_classes[model_name]
        serializer = serializer_class(queryset, many=True)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{model_name}.csv"'

        writer = csv.writer(response)
        writer.writerow(serializer.data[0].keys())
        for data in serializer.data:
            writer.writerow(data.values())

        return response

    def get_queryset(self, model_name):
        if model_name == 'area':
            return Area.objects.all()
        elif model_name == 'status':
            return Status.objects.all()

        return None

    def get_queryset(self, model_name):
        if model_name == 'area':
            return Area.objects.all()
        elif model_name == 'status':
            return Status.objects.all()

        return None

from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ImportDataViewSet(viewsets.GenericViewSet):
    serializer_classes = {
        'area': AreaSerializer,
        'status': StatusSerializer,
    }
    http_method_names = ["post"]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'model_name': openapi.Schema(type=openapi.TYPE_STRING),
                'file': openapi.Schema(type=openapi.TYPE_FILE),
            },
            required=['model_name', 'file'],
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
        },
        operation_summary="Upload CSV file to import data",
        operation_description="Upload a CSV file along with the model name to import data.",
    )
    def create(self, request):
        model_name = request.data.get('model_name', None)
        if model_name not in self.serializer_classes:
            return Response({'error': 'Invalid model name'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'File not found'}, status=status.HTTP_400_BAD_REQUEST)

        data = self.read_csv_file(file)
        serializer_class = self.serializer_classes[model_name]
        serializer = serializer_class(data=data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Data imported successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def read_csv_file(self, file):
        data = []
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
        return data