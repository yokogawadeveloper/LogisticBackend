from rest_framework import routers
from master.views import *
from subordinate.views import *
from dispatchInstruct.views import *

# Add routers here.

router = routers.DefaultRouter()
# ----------------------------- Master ------------------------------------------- #
router.register('role_master', RoleMasterViewSet, basename='role_master')
router.register('module_master', ModuleMasterViewSet, basename='module_master')
# ----------------------------- SubOrdinate ------------------------------------------- #
router.register('insurance_scope', InsuranceScopeViewSet, basename='insurance_scope')
router.register('freight_basis', FreightBasisViewSet, basename='freight_basis')
router.register('delivery_terms', DeliveryTermsViewSet, basename='delivery_terms')
router.register('mode_of_shipment', ModeOfShipmentViewSet, basename='mode_of_shipment')
router.register('payment_status', PaymentStatusViewSet, basename='payment_status')
router.register('special_packing', SpecialPackingViewSet, basename='special_packing')
router.register('export_packing_requirement', ExportPackingRequirementViewSet, basename='export_packing_requirement')
router.register('special_gst_rate', SpecialGSTRateViewSet, basename='special_gst_rate')
# ----------------------------- DispatchInstruction ------------------------------------------- #
router.register('dispatch_instruction', DispatchInstructionViewSet, basename='dispatch_instruction')
router.register('sap_dispatch_instruction', SAPDispatchInstructionViewSet, basename='sap_dispatch_instruction')
router.register('dispatch_instruction_bill_details', DispatchInstructionBillDetailsViewSet, basename='dispatch_instruction_bill_details')
router.register('master_item_list', MasterItemListViewSet, basename='master_item_list')
router.register('inline_item_list', InlineItemListViewSet, basename='inline_item_list')
