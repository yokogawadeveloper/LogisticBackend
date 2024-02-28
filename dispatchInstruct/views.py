import pandas as pd
from rest_framework import permissions, status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .frames import dil_upload_columns
from .serializers import *


# Create your views here.
class DispatchInstructionViewSet(viewsets.ModelViewSet):
    queryset = DispatchInstruction.objects.all()
    serializer_class = DispatchInstructionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SAPDispatchInstructionViewSet(viewsets.ModelViewSet):
    queryset = DispatchInstruction.objects.all()
    serializer_class = SAPDispatchInstructionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='dil_upload', url_name='dil_upload')
    def dil_upload(self, request, *args, **kwargs):
        try:
            file = request.FILES['file']
            df = pd.read_excel(file, sheet_name='Sheet1')
            pre_columns = dil_upload_columns
            column_names = df.columns.tolist()

            # check if all the columns are present in the file
            if all(element in pre_columns for element in column_names):
                for column_name in df.columns:
                    # Try to convert each column to the desired type
                    try:
                        if column_name in ['Reference Document', 'Delivery Create Date', 'Tax Invoice Date',
                                           'Billing Create Date', 'DIL Output Date']:
                            df[column_name] = df[column_name].astype(str)
                        elif column_name in ['Tax Invoice Assessable Value', 'Tax Invoice Total Tax Value',
                                             'Tax Invoice Total Value', 'Item Price (Sales)']:
                            df[column_name] = df[column_name].astype(float)
                    except ValueError:
                        # If there's a conversion error, return a response indicating the column causing the issue
                        return Response({'message': f'Error converting column "{column_name}" to the desired type',
                                         'status': status.HTTP_400_BAD_REQUEST})

                    # If all conversions succeed, you can proceed with creating objects or any other operations
                    # SAPDispatchInstruction.objects.create(...)

                return Response({'message': 'File uploaded successfully', 'status': status.HTTP_201_CREATED})
            else:
                return Response({'message': 'File does not contain all the required columns',
                                 'status': status.HTTP_400_BAD_REQUEST})
        except Exception as e:
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})

    @action(detail=False, methods=['post'], url_path='dil_upload_transaction', url_name='dil_upload_transaction')
    def dil_upload_transaction(self, request, *args, **kwargs):
        try:
            file = request.FILES['file']
            df = pd.read_excel(file, sheet_name='Sheet1')
            pre_columns = dil_upload_columns
            column_names = df.columns.tolist()

            # Check if all the required columns are present
            if all(element in pre_columns for element in column_names):
                objects_to_create = []
                for index, row in df.iterrows():
                    obj = SAPDispatchInstruction(
                        reference_doc=row['Reference Document'],
                        delivery_create_date=row['Delivery Create Date'],
                        # Map other columns similarly
                        created_by=request.user  # Assuming you want to associate the current user
                    )
                    objects_to_create.append(obj)

                # Bulk create objects
                with transaction.atomic():
                    SAPDispatchInstruction.objects.bulk_create(objects_to_create)

                return Response({'message': 'File uploaded successfully', 'status': status.HTTP_201_CREATED})
            else:
                return Response({'message': 'File does not contain all the required columns',
                                 'status': status.HTTP_400_BAD_REQUEST})
        except Exception as e:
            # If any exception occurs during bulk creation, revert changes
            transaction.rollback()
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})


class DispatchInstructionBillDetailsViewSet(viewsets.ModelViewSet):
    queryset = DispatchInstructionBillDetails.objects.all()
    serializer_class = DispatchInstructionBillDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MasterItemListViewSet(viewsets.ModelViewSet):
    queryset = MasterItemList.objects.all()
    serializer_class = MasterItemListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = MasterItemList.objects.all().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        dil_no = request.data.get('dil_id')
        dispatch_instruction = DispatchInstruction.objects.filter(dil_id=dil_no).first()

        if not dispatch_instruction:
            return Response({'message': 'dil no does not exist', 'status': status.HTTP_204_NO_CONTENT})

        if not dispatch_instruction.is_active:
            return Response({'message': 'dil no is not active', 'status': status.HTTP_204_NO_CONTENT})

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InlineItemListViewSet(viewsets.ModelViewSet):
    queryset = InlineItemList.objects.all()
    serializer_class = InlineItemListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = InlineItemList.objects.all().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        item_list_id = request.data.get('item_list_id')
        master_item_list = MasterItemList.objects.filter(item_id=item_list_id).first()

        if not master_item_list:
            return Response({'message': 'item list id does not exist', 'status': status.HTTP_204_NO_CONTENT})

        if not master_item_list.is_active:
            return Response({'message': 'item list id is not active', 'status': status.HTTP_204_NO_CONTENT})

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
