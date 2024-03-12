from rest_framework import serializers
from .models import *


# Serializers define the API representation.
class WorkFlowTypeSerializer(serializers.ModelSerializer):
    wf_name = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = WorkFlowType
        fields = '__all__'

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['is_active'] = True
        return WorkFlowType.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super(WorkFlowTypeSerializer, self).update(instance=instance, validated_data=validated_data)


class WorkFlowControlSerializer(serializers.ModelSerializer):
    wft = WorkFlowTypeSerializer(many=True, required=False)

    class Meta:
        model = WorkFlowControl
        fields = '__all__'

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return WorkFlowControl.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super(WorkFlowControlSerializer, self).update(instance=instance, validated_data=validated_data)


class WorkFlowEmployeesSerializer(serializers.ModelSerializer):
    wfc = WorkFlowControlSerializer(many=True, required=False)

    class Meta:
        model = WorkFlowEmployees
        fields = '__all__'

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return WorkFlowEmployees.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super(WorkFlowEmployeesSerializer, self).update(instance=instance, validated_data=validated_data)


class WorkFlowDaApproversSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkFlowDaApprovers
        fields = '__all__'

    def create(self, validated_data):
        return WorkFlowDaApprovers.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.wf_id = validated_data.get('wf_id', instance.wf_id)
        return super(WorkFlowDaApproversSerializer, self).update(instance=instance, validated_data=validated_data)


class WorkflowAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowAccess
        fields = '__all__'

    def create(self, validated_data):
        return WorkflowAccess.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.wfa_id = validated_data.get('wfa_id', instance.wfa_id)
        return super(WorkflowAccessSerializer, self).update(instance=instance, validated_data=validated_data)
