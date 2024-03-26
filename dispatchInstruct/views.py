import time
import pandas as pd
from datetime import datetime
from django.db import transaction
from rest_framework import permissions, status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .frames import column_mapping
from workflow.models import *
from .serializers import *


# Create your views here.
class DispatchInstructionViewSet(viewsets.ModelViewSet):
    queryset = DispatchInstruction.objects.all()
    serializer_class = DispatchInstructionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer_data = serializer.save()

        if 'approverlist' in request.data:
            appover_list_to_app = 0
            appover_current_da_lev_2 = 0
            for val in request.data['approverlist']:
                appover_current_da_lev_1 = val['level']
                if val['required_list']:
                    if appover_current_da_lev_1 != appover_current_da_lev_2:
                        appover_list_to_app += 1
                    for emp_id in val['emp_list']:
                        WorkFlowDaApprovers.objects.create(
                            dil_id_id=serializer.instance.dil_id,
                            wf_id_id=val['wf_id'],
                            approver=val['approval'],
                            level=val['level'],
                            parallel=val['parallel'],
                            emp_id=emp_id,
                            status="pending",
                            created_by=request.user
                        )
                appover_current_da_lev_2 = val['level']
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

    @action(methods=['post'], detail=False, url_path='complete_dil')
    def complete_dil(self, request, *args, **kwargs):
        try:
            payload = request.data
            dil_id = payload.get("dil_id")
            data = DispatchInstruction.objects.values().get(dil_id=dil_id)
            if not data:
                return Response({'message': 'DA not found', 'status': status.HTTP_204_NO_CONTENT})

            dil_filter = DispatchInstruction.objects.filter(dil_id=dil_id).values('dil_stage')[0]['dil_stage']
            workflow_da_list = WorkFlowDaApprovers.objects.filter(dil_id_id=dil_id, level=1).values()
            for wf in workflow_da_list:
                DAUserRequestAllocation.objects.create(
                    dil_id_id=dil_id,
                    emp_id_id=wf['emp_id'],
                    status="pending",
                    approver_stage=wf['approver'],
                    approver_level=wf['level'],
                    created_by_id=request.user.id
                )
            # create DAUserRequestAllocation for each approver
            DAAuthThreads.objects.create(
                dil_id_id=dil_id,
                emp_id=request.user.id,
                remarks='DA prepared',
                status="DA Submitted",
                created_by_id=request.user.id
            )
            # update the dil_stage
            DispatchInstruction.objects.filter(dil_id=dil_id).update(
                submitted_date=datetime.now(),
                dil_status_no=1,
                dil_status='DIL Submitted'
            )
            return Response({'message': 'DA completed successfully', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})


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

    @action(detail=False, methods=['post'], url_path='sap_dil_upload')
    def dil_upload_transaction(self, request, *args, **kwargs):
        try:
            start_time = time.time()  # Start timing
            file = request.FILES['file']
            df = pd.read_excel(file, sheet_name='Sheet1')

            # Filter DataFrame to keep only required columns
            df = df.rename(columns=column_mapping)
            required_columns = list(column_mapping.values())
            df = df[required_columns]

            # Check if all required columns are present
            missing_columns = [col for col in required_columns if col not in df.columns]
            if not missing_columns:
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
                    {'message': f'File is missing the following required columns: {", ".join(missing_columns)}',
                     'status': status.HTTP_400_BAD_REQUEST})
        except Exception as e:
            transaction.rollback()
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})


class DispatchBillDetailsViewSet(viewsets.ModelViewSet):
    queryset = DispatchBillDetails.objects.all()
    serializer_class = DispatchBillDetailsSerializer
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
                    DispatchBillDetails.objects.create(
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

    @action(detail=False, methods=['post'], url_path='create_bill')
    def create_bill(self, request, *args, **kwargs):
        try:
            payload = request.data
            dil_id = payload.get("dil_id")
            item_list = payload.get("item_list", [])
            dil = DispatchInstruction.objects.filter(dil_id=dil_id).first()
            if not dil:
                return Response({'message': 'DIL not found', 'status': status.HTTP_204_NO_CONTENT})
            for item_data in item_list:
                material_description = item_data.get("material_discription")
                material_no = item_data.get("material_no")
                ms_code = item_data.get("ms_code")
                linkage_no = item_data.get("linkage_no")
                quantity = item_data.get("sales_quantity")
                packed_quantity = item_data.get("packed_quantity")
                item_price = item_data.get("sales_item_price")
                tax_amount = item_data.get("tax_invoice_total_tax_value")
                total_amount = item_data.get("tax_invoice_total_value")
                total_amount_with_tax = total_amount
                # Create DispatchBillDetails instance
                DispatchBillDetails.objects.create(
                    dil_id=dil,
                    material_description=material_description,
                    material_no=material_no,
                    ms_code=ms_code,
                    linkage_no=linkage_no,
                    quantity=quantity,
                    packed_quantity=packed_quantity,
                    item_price=item_price,
                    tax_amount=tax_amount,
                    total_amount=total_amount,
                    total_amount_with_tax=total_amount_with_tax,
                    created_by=request.user
                )
            return Response({'message': 'Bill created successfully', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='bill_details_based_dil')
    def bill_details_based_dil(self, request, *args, **kwargs):
        try:
            dil_id = request.data['dil_id']
            bill_details = DispatchBillDetails.objects.filter(dil_id=dil_id).all()
            if not bill_details:
                return Response({'message': 'Bill Details not found', 'status': status.HTTP_204_NO_CONTENT})
            serializer = DispatchBillDetailsSerializer(bill_details, many=True)
            return Response(serializer.data)
        except Exception as e:
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

    @action(detail=False, methods=['post'], url_path='list_based_on_dil')
    def list_based_on_dil(self, request, *args, **kwargs):
        try:
            dil_id = request.data['dil_id']
            master_item_list = MasterItemList.objects.filter(dil_id=dil_id).all()
            if not master_item_list:
                return Response({'message': 'Master Item List not found', 'status': status.HTTP_204_NO_CONTENT})
            serializer = MasterItemListSerializer(master_item_list, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})

    @action(detail=False, methods=['post'], url_path='create_master_item_list')
    def create_master_item_list(self, request, *args, **kwargs):
        try:
            payload = request.data
            with transaction.atomic():
                for item in payload:
                    dil = DispatchInstruction.objects.filter(dil_id=item['dil_id']).first()
                    if DispatchInstruction.objects.filter(dil_id=item['dil_id']).exists():
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
                        return Response(
                            {'message': 'Master item list created successfully', 'status': status.HTTP_201_CREATED})
                    else:
                        return Response({'message': 'DIL not found', 'status': status.HTTP_204_NO_CONTENT})
        except Exception as e:
            transaction.set_rollback(True)
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})

    @action(detail=False, methods=['post'], url_path='create_master_item')
    def create_master_item(self, request, *args, **kwargs):
        try:
            payload = request.data
            dil_id = payload.get("dil_id")
            item_list = payload.get("item_list", [])
            dil = DispatchInstruction.objects.filter(dil_id=dil_id).first()
            if not dil:
                return Response({'message': 'DIL not found', 'status': status.HTTP_204_NO_CONTENT})
            for item_data in item_list:
                material_description = item_data.get("material_discription")
                material_no = item_data.get("material_no")
                ms_code = item_data.get("ms_code")
                linkage_no = item_data.get("linkage_no")
                quantity = item_data.get("sales_quantity")
                packed_quantity = item_data.get("packed_quantity")
                plant = item_data.get("plant")
                storage_location = item_data.get("s_loc")
                # Create DispatchBillDetails instance
                MasterItemList.objects.create(
                    dil_id=dil,
                    material_description=material_description,
                    material_no=material_no,
                    ms_code=ms_code,
                    linkage_no=linkage_no,
                    quantity=quantity,
                    packed_quantity=packed_quantity,
                    plant=plant,
                    s_loc=storage_location,
                    created_by=request.user
                )
            return Response({'message': 'Master List created successfully', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


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


class FileTypeViewSet(viewsets.ModelViewSet):
    queryset = FileType.objects.all()
    serializer_class = FileTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MultiFileAttachmentViewSet(viewsets.ModelViewSet):
    queryset = MultiFileAttachment.objects.all()
    serializer_class = MultiFileAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='create_multi_file_attachment')
    def create_multi_file_attachment(self, request, *args, **kwargs):
        try:
            payload = request.FILES.getlist('file')
            dil_id = request.data['dil_id']
            file_type = request.data['file_type']
            module_name = request.data['module_name']
            module_id = request.data['module_id']
            with transaction.atomic():
                for file in payload:
                    dil = DispatchInstruction.objects.filter(dil_id=dil_id).first()
                    fileType = FileType.objects.filter(file_type_id=file_type).first()
                    if not dil:
                        transaction.set_rollback(True)
                        return Response({'message': 'DIL not found', 'status': status.HTTP_204_NO_CONTENT})
                    if not fileType:
                        transaction.set_rollback(True)
                        return Response({'message': 'File type not found', 'status': status.HTTP_204_NO_CONTENT})
                    # Create multi file attachment
                    MultiFileAttachment.objects.create(
                        dil_id=dil,
                        file=file,
                        file_type=fileType,
                        module_name=module_name,
                        module_id=module_id,
                    )
                return Response({'message': 'Multiple File uploaded successfully', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            transaction.set_rollback(True)
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})


class DILAuthThreadsViewSet(viewsets.ModelViewSet):
    queryset = DAAuthThreads.objects.all()
    serializer_class = DAAuthThreadsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = DAAuthThreads.objects.all().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        global currentlevel
        try:
            data = request.data.copy()
            user_id = request.user.id
            stature = data['status']
            dil_id = data['dil_id']
            dil = DispatchInstruction.objects.filter(dil_id=dil_id)
            if dil is not None:
                current_level = dil.values('current_level')[0]['current_level']
                dil_level = dil.values('dil_level')[0]['dil_level']
                wf_approver = WorkFlowDaApprovers.objects.filter(dil_id_id=dil_id, level=current_level)
                checking = wf_approver.values('approver')[0]['approver']
                wf_da_count = wf_approver.count()
                currentlevel = current_level

                if stature == "modification":
                    dispatch = DispatchInstruction.objects.filter(dil_id=data['da_id'])
                    dispatch.update(current_level=1, status="modification")
                    DAUserRequestAllocation.objects.filter(dil_id_id=data['da_id'], approve_status='Approver',
                                                           approved_date=datetime.now()).delete()
                    WorkFlowDaApprovers.objects.filter(dil_id_id=data['da_id']).update(status="pending")

                elif stature == "reject":
                    DispatchInstruction.objects.filter(dil_id=data['da_id']).update(current_level=1, status="rejected")
                    allocation = DAUserRequestAllocation.objects.filter(dil_id_id=data['da_id'], emp_id=user_id)
                    allocation.update(status="rejected", approved_date=datetime.now())

                else:
                    wf_da_status = WorkFlowDaApprovers.objects.filter(emp_id=user_id).values('approver')[0]['approver']
                    data['approver'] = wf_da_status
                    # update the allocation table
                    allocation = DAUserRequestAllocation.objects.filter(dil_id_id=dil_id, emp_id=user_id)
                    allocation.update(status="approved", approved_date=datetime.now())
                    DAUserRequestAllocation.objects.filter(dil_id_id=dil_id).update(approver_flag=True)
                    # if all the approvers are approved then update the status
                    if int(dil_level) >= int(current_level):
                        wf_approver.filter(emp_id=request.user.id).update(status=stature)
                        if wf_da_count == wf_approver.exclude(parallel=True, status__contains='approved').count():
                            currentlevel = current_level
                            current_level = int(current_level) + 1
                            dil.update(
                                current_level=current_level,
                                dil_status=wf_da_status + ' ' + 'approved',
                                dil_status_no=2
                            )
                            # for each level create the allocation
                            flow_approvers = WorkFlowDaApprovers.objects.filter(dil_id_id=dil_id,
                                                                                level=current_level).values()
                            for i in flow_approvers:
                                DAUserRequestAllocation.objects.create(
                                    dil_id_id=dil_id,
                                    emp_id_id=i['emp_id'],
                                    status="pending",
                                    approver_stage=i['approver'],
                                    approver_level=i['level']
                                )
                        # if the current level is greater than the dil level then update the dil level
                        elif wf_da_count == wf_approver.filter(parallel=True, status__contains='approved').count():
                            currentlevel = current_level
                            current_level = current_level + 1
                            dil.update(
                                current_level=current_level,
                                status=wf_da_status + ' ' + "approved",
                                da_status_number=2
                            )
                            # for each level create the allocation
                            flow_approvers = WorkFlowDaApprovers.objects.filter(dil_id_id=dil_id,
                                                                                level=current_level).values()
                            for i in flow_approvers:
                                DAUserRequestAllocation.objects.create(
                                    dil_id_id=dil_id,
                                    emp_id_id=i['emp_id'],
                                    status="pending")
                        # if the current level is greater than the dil level then update the dil level
                        if int(dil_level) < int(current_level):
                            dil.update(approved_flag=True)

                if int(dil_level) == int(currentlevel) and status == "approved":
                    dil.update(dil_status_no=3)

                # create the DA Auth Threads by serializing the data
                serializer = DAAuthThreadsSerializer(data=data, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {'message': 'DIL Auth Threads created successfully', 'status': status.HTTP_201_CREATED})
            return Response({'message': 'DA not found', 'status': status.HTTP_204_NO_CONTENT})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='get_da_auth_thread')
    def get_da_auth_thread(self, request, *args, **kwargs):
        try:
            dil_id = request.data['dil_id']
            da_auth_thread = DAAuthThreads.objects.filter(dil_id=dil_id).all()
            if not da_auth_thread:
                return Response({'message': 'DA Auth Thread not found', 'status': status.HTTP_204_NO_CONTENT})
            serializer = DAAuthThreadsSerializer(da_auth_thread, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})

    @action(methods=['post'], detail=False, url_path='da_packing_approved')
    def da_packing_approved(self, request):
        try:
            data = request.data
            stature = data['status']
            dil_id = data['dil_id']

            if stature == "modification":
                DispatchInstruction.objects.filter(dil_id=dil_id).update(current_level=1, status="modification")
                DAUserRequestAllocation.objects.filter(dil_id_id=dil_id).delete()

                WorkFlowDaApprovers.objects.filter(dil_id_id=dil_id).update(status="pending")
                WorkFlowDaApprovers.objects.create(
                    dil_id_id=dil_id,
                    emp_id=request.user.id,
                    remarks=data['remarks'],
                    status="Sent for Modification"
                )

            elif stature == "reject":
                DispatchInstruction.objects.filter(dil_id=dil_id).update(current_level=1, status="rejected")
                DAUserRequestAllocation.objects.filter(dil_id_id=dil_id, emp_id=request.user.id).update(
                    status="rejected")
                DAAuthThreads.objects.create(
                    dil_id_id=dil_id,
                    emp_id=request.user.id,
                    remarks=data['remarks'],
                    status="Rejected"
                )

            elif stature == "hold":
                DispatchInstruction.objects.filter(dil_id=dil_id).update(status="hold")
                DAAuthThreads.objects.create(
                    dil_id_id=dil_id,
                    emp_id=request.user.id,
                    remarks=data['remarks'],
                    status="Hold")

            else:
                DAAuthThreads.objects.create(
                    da_id_id=data['da_id'],
                    emp_id=request.user.id,
                    remarks=data['remarks'],
                    status="packing acknowledged"
                )
                DispatchInstruction.objects.filter(da_id=data['da_id']).update(
                    packing_approver_flag=True,
                    status="packing acknowledged",
                    da_status_number=4
                )
            return Response({'message': 'DA Packing Approved', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
