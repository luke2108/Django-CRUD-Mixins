import csv
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from common.models import Area, Status
from .serializers import AreaSerializer, StatusSerializer
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'

class XYZModelView(viewsets.ModelViewSet):
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True) if page else self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data) if page else Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def bulk_delete(self, request):
        queryset = self.get_queryset()
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AreaViewSet(XYZModelView):
    http_method_names = ["get", "post", "put", "delete"]
    queryset = Area.objects.all()
    serializer_class = AreaSerializer

class StatusViewSet(XYZModelView):
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

class ImportDataViewSet(viewsets.GenericViewSet):
    serializer_classes = {
        'area': AreaSerializer,
        'status': StatusSerializer,
    }
    http_method_names = ["post"]
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('file', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Upload CSV file to import data'),
            openapi.Parameter('model_name', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Model name')
        ],
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
        reader = csv.DictReader(file.read().decode('utf-8').splitlines())
        for row in reader:
            data.append(row)
        return data
