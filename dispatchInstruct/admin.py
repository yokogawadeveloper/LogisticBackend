from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(DispatchInstruction)
admin.site.register(SAPDispatchInstruction)
admin.site.register(DispatchInstructionBillDetails)
admin.site.register(MasterItemList)
admin.site.register(InlineItemList)
