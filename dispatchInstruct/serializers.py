from rest_framework import serializers
from .models import *


# Serializers define the API representation.
class DispatchInstructionSerializer(serializers.ModelSerializer):
    dil_no = serializers.CharField(max_length=20, required=True)
    so_no = serializers.CharField(max_length=20, required=True)
    po_no = serializers.CharField(max_length=20, required=True)

    # insurance_scope = serializers.PrimaryKeyRelatedField(queryset=InsuranceScope.objects.all(), required=True)
    # freight_basis = serializers.PrimaryKeyRelatedField(queryset=FreightBasis.objects.all(), required=True)
    # delivery_terms = serializers.PrimaryKeyRelatedField(queryset=DeliveryTerms.objects.all(), required=True)
    # mode_of_shipment = serializers.PrimaryKeyRelatedField(queryset=ModeOfShipment.objects.all(), required=True)
    # payment_status = serializers.PrimaryKeyRelatedField(queryset=PaymentStatus.objects.all(), required=True)
    # special_packing = serializers.PrimaryKeyRelatedField(queryset=SpecialPacking.objects.all(), required=True)
    # export_packing_req = serializers.PrimaryKeyRelatedField(queryset=ExportPackingRequirement.objects.all(),
    #                                                         required=True)
    # special_gst_rate = serializers.PrimaryKeyRelatedField(queryset=SpecialGSTRate.objects.all(), required=True)

    class Meta:
        model = DispatchInstruction
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_by', 'updated_at', 'is_active']

    # def validate(self, attrs):
    #     insurance_scope = attrs.get('insurance_scope')
    #     if insurance_scope is None:
    #         raise serializers.ValidationError("Insurance Scope is required.")

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['updated_by'] = self.context['request'].user
        validated_data['is_active'] = True
        return DispatchInstruction.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super(DispatchInstructionSerializer, self).update(instance, validated_data)


class SAPDispatchInstructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SAPDispatchInstruction
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_by', 'updated_at', 'is_active']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['updated_by'] = self.context['request'].user
        validated_data['is_active'] = True
        return DispatchInstruction.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super(SAPDispatchInstructionSerializer, self).update(instance, validated_data)


class DispatchInstructionBillDetailsSerializer(serializers.ModelSerializer):
    dil_id = serializers.PrimaryKeyRelatedField(queryset=DispatchInstruction.objects.all(), required=True)

    class Meta:
        model = DispatchInstructionBillDetails
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_by', 'updated_at', 'is_active']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['updated_by'] = self.context['request'].user
        validated_data['is_active'] = True
        return DispatchInstructionBillDetails.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super(DispatchInstructionBillDetailsSerializer, self).update(instance, validated_data)


class MasterItemListSerializer(serializers.ModelSerializer):
    material_description = serializers.CharField(max_length=100, required=True)
    material_no = serializers.CharField(max_length=20, required=True)

    class Meta:
        model = MasterItemList
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_by', 'updated_at', 'is_active']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['updated_by'] = self.context['request'].user
        validated_data['is_active'] = True
        return MasterItemList.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super(MasterItemListSerializer, self).update(instance, validated_data)


class InlineItemListSerializer(serializers.ModelSerializer):
    serial_no = serializers.CharField(max_length=20, required=True)

    class Meta:
        model = InlineItemList
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_by', 'updated_at', 'is_active']
        depth = 1
