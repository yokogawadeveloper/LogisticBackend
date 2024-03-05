from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import *


# Create your views here.
class WorkFLowTypeViewSet(viewsets.ModelViewSet):
    queryset = WorkFlowType.objects.all()
    serializer_class = WorkFlowTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = WorkFlowTypeSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        data = request.data
        instance = self.get_object()
        serializer = WorkFlowTypeSerializer(instance, data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkFlowControlViewSet(viewsets.ModelViewSet):
    queryset = WorkFlowControl.objects.all()
    serializer_class = WorkFlowControlSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = serializer.data
        # Fetch related WorkFlowType objects in bulk to avoid N+1 query issue
        wf_ids = [item['wf_id'] for item in response_data if 'wf_id' in item]
        work_flow_types = WorkFlowType.objects.filter(wf_id__in=wf_ids, is_active=True)
        work_flow_type_dict = {wf.wf_id: wf for wf in work_flow_types}
        # Update response data with related WorkFlowType objects
        for item in response_data:
            if 'wf_id' in item:
                wf_id = item['wf_id']
                item['wft'] = WorkFlowTypeSerializer(work_flow_type_dict[wf_id]).data
        return Response(response_data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = WorkFlowControlSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        data = request.data
        instance = self.get_object()
        serializer = WorkFlowControlSerializer(instance, data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkFlowEmployeesViewSet(viewsets.ModelViewSet):
    queryset = WorkFlowEmployees.objects.all()
    serializer_class = WorkFlowEmployeesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = serializer.data
        # Fetch related WorkFlowControl objects in bulk to avoid N+1 query issue
        wfc_ids = [item['wfc_id'] for item in response_data if 'wfc_id' in item]
        work_flow_controls = WorkFlowControl.objects.filter(wfc_id__in=wfc_ids)
        work_flow_control_dict = {wfc.wfc_id: wfc for wfc in work_flow_controls}
        # Update response data with related WorkFlowControl objects
        for item in response_data:
            if 'wfc_id' in item:
                wfc_id = item['wfc_id']
                item['wfc'] = WorkFlowControlSerializer(work_flow_control_dict[wfc_id]).data
        return Response(response_data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = WorkFlowEmployeesSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        data = request.data
        instance = self.get_object()
        serializer = WorkFlowEmployeesSerializer(instance, data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkflowAccessViewSet(viewsets.ModelViewSet):
    queryset = WorkflowAccess.objects.all()
    serializer_class = WorkflowAccessSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = serializer.data
        # Fetch related WorkFlowType objects in bulk to avoid N+1 query issue
        wf_ids = [item['wf_id'] for item in response_data if 'wf_id' in item]
        work_flow_types = WorkFlowType.objects.filter(wf_id__in=wf_ids, is_active=True)
        work_flow_type_dict = {wf.wf_id: wf for wf in work_flow_types}
        # Update response data with related WorkFlowType objects
        for item in response_data:
            if 'wf_id' in item:
                wf_id = item['wf_id']
                item['work_flow_control'] = WorkFlowTypeSerializer(work_flow_type_dict[wf_id]).data
        return Response(response_data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = WorkflowAccessSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        data = request.data
        instance = self.get_object()
        serializer = WorkflowAccessSerializer(instance, data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


