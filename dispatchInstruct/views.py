import time
import pandas as pd
from django.db import transaction
from rest_framework import permissions, status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
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

    @action(detail=False, methods=['post'], url_path='dil_upload')
    def dil_upload_transaction(self, request, *args, **kwargs):
        try:
            start_time = time.time()  # Start timing
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
                        sold_to_party_no=row['Sold-to Party'],
                        sold_to_party_name=row['Sold-to Party Name'],
                        delivery=row['Delivery'],
                        delivery_create_date=row['Delivery Create Date'],
                        delivery_item=row['Delivery Item'],
                        tax_invoice_no=row['Tax Invoice Number (ODN)'],
                        reference_doc_item=row['Reference Document Item'],
                        ms_code=row['MS Code'],
                        sales_quantity=row['Quantity (Sales)'],
                        linkage_no=row['Linkage Number'],
                        sales_office=row['Sales Office'],
                        term_of_payment=row['Terms of Payment'],
                        tax_invoice_date=row['Tax Invoice Date'],

                        material_discription=row['Material Description'],
                        plant=row['Plant'],
                        plant_name=row['Plant Name'],
                        unit_sales=row['Unit (Sales)'],
                        billing_number=row['Billing Number'],
                        billing_create_date=row['Billing Create Date'],
                        currency_type=row['Currency (Sales)'],
                        ship_to_party_no=row['Ship-to party'],
                        ship_to_party_name=row['Ship-to Party Name'],
                        ship_to_country=row['Ship-to Country'],
                        ship_to_postal_code=row['Ship-to Postal Code'],
                        ship_to_city=row['Ship-to City'],
                        ship_to_street=row['Ship-to Street'],
                        ship_to_street_for=row['Ship-to Street4'],
                        insurance_scope=row['Insurance Scope'],
                        sold_to_country=row['Sold-to Country'],
                        sold_to_postal_code=row['Sold-to Postal Code'],
                        sold_to_city=row['Sold-to City'],
                        sold_to_street=row['Sold-to Street'],
                        sold_to_street_for=row['Sold-to Street4'],
                        material_no=row['Material Number'],
                        hs_code=row['HS Code'],
                        hs_code_export=row['HS Code Export'],
                        delivery_quantity=row['Delivery quantity'],
                        unit_delivery=row['Unit (Delivery)'],
                        storage_location=row['Storage Location'],
                        dil_output_date=row['DIL Output Date'],
                        sales_doc_type=row['Sales Document Type'],
                        distribution_channel=row['Distribution Channel'],
                        invoice_item=row['Invoice Item'],
                        tax_invoice_assessable_value=row['Tax Invoice Assessable Value'],
                        tax_invoice_total_tax_value=row['Tax Invoice Total Tax Value'],
                        tax_invoice_total_value=row['Tax Invoice Total Value'],
                        sales_item_price=row['Item Price (Sales)'],
                        packing_status=row['Packing status'],
                        do_item_packed_quantity=row['DO Item Packed Quantity'],
                        packed_unit_quantity=row['Packed Quantity unit'],
                        created_by=request.user
                    )
                    objects_to_create.append(obj)
                # Bulk create objects
                with transaction.atomic():
                    SAPDispatchInstruction.objects.bulk_create(objects_to_create)
                    # Calculate upload time
                    end_time = time.time()
                    upload_time = end_time - start_time
                return Response(
                    {'message': 'File uploaded successfully',
                     'timeComplexity': upload_time,
                     'status': status.HTTP_201_CREATED
                     })
            else:
                return Response(
                    {'message': 'File does not contain required columns', 'status': status.HTTP_400_BAD_REQUEST})
        except Exception as e:
            transaction.rollback()
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})

    @action(detail=False, methods=['post'], url_path='dil_based_on_delivery')
    def dil_based_on_delivery(self, request, *args, **kwargs):
        try:
            delivery_no = request.data['delivery']
            dil = SAPDispatchInstruction.objects.filter(delivery=delivery_no).all()
            if not dil:
                return Response({'message': 'DIL Not found for this delivery', 'status': status.HTTP_204_NO_CONTENT})
            serializer = SAPDispatchInstructionSerializer(dil, many=True)
            return Response(serializer.data)
        except Exception as e:
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

    @action(detail=False, methods=['post'], url_path='create_bill_details')
    def create_bill_details(self, request, *args, **kwargs):
        try:
            payload = request.data
            with transaction.atomic():
                for item in payload:
                    dil = DispatchInstruction.objects.filter(dil_id=item['dil_id']).first()
                    if not dil:
                        transaction.set_rollback(True)
                        return Response({'message': 'DIL not found', 'status': status.HTTP_204_NO_CONTENT})
                    if not dil.is_active:
                        transaction.set_rollback(True)
                        return Response({'message': 'DIL is not active', 'status': status.HTTP_204_NO_CONTENT})
                    DispatchInstructionBillDetails.objects.create(
                        dil_id=dil,
                        material_description=item['material_discription'],
                        material_no=item['material_no'],
                        ms_code=item['ms_code'],
                        s_loc=item['storage_location'],
                        sap_line_item_no=item['delivery_item'],
                        linkage_no=item['linkage_no'],
                        # group=item['group'],
                        quantity=item['delivery_quantity'],
                        country_of_origin=item['ship_to_country'],
                        # item_status=item['item_status'],
                        # item_status_no=item['item_status_no'],
                        packed_quantity=item['do_item_packed_quantity'],
                        item_price=item['sales_item_price'],
                        # igst=item['igst'],
                        # cgst=item['cgst'],
                        # sgst=item['sgst'],
                        tax_amount=item['tax_invoice_assessable_value'],
                        total_amount=item['tax_invoice_total_tax_value'],
                        total_amount_with_tax=item['tax_invoice_total_value'],
                        created_by=request.user
                    )
                return Response({'message': 'Bill details created successfully', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            transaction.set_rollback(True)
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})


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

    @action(detail=False, methods=['post'], url_path='create_master_item_list')
    def create_master_item_list(self, request, *args, **kwargs):
        try:
            payload = request.data
            with transaction.atomic():
                for item in payload:
                    dil = DispatchInstruction.objects.filter(dil_id=item['dil_id']).first()
                    if not dil:
                        transaction.set_rollback(True)
                        return Response({'message': 'DIL not found', 'status': status.HTTP_204_NO_CONTENT})
                    if not dil.is_active:
                        transaction.set_rollback(True)
                        return Response({'message': 'DIL is not active', 'status': status.HTTP_204_NO_CONTENT})
                    MasterItemList.objects.create(
                        dil_id=dil,
                        material_description=item['material_discription'],
                        material_no=item['material_no'],
                        ms_code=item['ms_code'],
                        s_loc=item['storage_location'],
                        plant=item['plant'],
                        linkage_no=item['linkage_no'],
                        quantity=item['delivery_quantity'],
                        country_of_origin=item['ship_to_country'],
                        # serial_no=item['serial_no'],
                        # match_no=item['match_no'],
                        # tag_no=item['tag_no'],
                        # range=item['range'],
                        # customer_po_sl_no=item['customer_po_sl_no'],
                        # customer_po_item_code=item['customer_po_item_code'],
                        # item_status=item['item_status'],
                        # item_status_no=item['item_status_no'],
                        packed_quantity=item['do_item_packed_quantity'],
                        created_by=request.user
                    )
                return Response({'message': 'Master item list created successfully', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            transaction.set_rollback(True)
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})


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
