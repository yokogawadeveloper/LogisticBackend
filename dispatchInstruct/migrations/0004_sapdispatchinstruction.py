# Generated by Django 4.2.10 on 2024-02-26 08:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dispatchInstruct', '0003_masteritemlist_inlineitemlist'),
    ]

    operations = [
        migrations.CreateModel(
            name='SAPDispatchInstruction',
            fields=[
                ('sap_dil_id', models.AutoField(primary_key=True, serialize=False)),
                ('reference_doc', models.CharField(blank=True, max_length=100, null=True)),
                ('reference_doc_item', models.CharField(blank=True, max_length=100, null=True)),
                ('sold_to_party_no', models.CharField(blank=True, max_length=100, null=True)),
                ('sold_to_party_name', models.CharField(blank=True, max_length=100, null=True)),
                ('delivery', models.CharField(blank=True, max_length=100, null=True)),
                ('delivery_item', models.CharField(blank=True, max_length=100, null=True)),
                ('delivery_date', models.DateField(auto_now=True)),
                ('tax_invoice_no', models.CharField(blank=True, max_length=100, null=True)),
                ('tax_invoice_date', models.DateField(auto_now=True)),
                ('yil_invoice_no', models.CharField(blank=True, max_length=100, null=True)),
                ('ms_code', models.CharField(blank=True, max_length=100, null=True)),
                ('quantity', models.IntegerField(blank=True, null=True)),
                ('linkage_no', models.CharField(blank=True, max_length=100, null=True)),
                ('sales_office', models.CharField(blank=True, max_length=100, null=True)),
                ('term_of_payment', models.CharField(blank=True, max_length=100, null=True)),
                ('material_discription', models.CharField(blank=True, max_length=100, null=True)),
                ('shiping_point', models.CharField(blank=True, max_length=100, null=True)),
                ('shiping_point_discription', models.CharField(blank=True, max_length=100, null=True)),
                ('receiving_point', models.CharField(blank=True, max_length=100, null=True)),
                ('plant', models.CharField(blank=True, max_length=100, null=True)),
                ('plant_name', models.CharField(blank=True, max_length=100, null=True)),
                ('challan_no', models.CharField(blank=True, max_length=100, null=True)),
                ('challan_item', models.CharField(blank=True, max_length=100, null=True)),
                ('challan_date', models.DateField(auto_now=True)),
                ('category_ref', models.CharField(blank=True, max_length=100, null=True)),
                ('billing_number', models.CharField(blank=True, max_length=100, null=True)),
                ('billing_date', models.DateField(auto_now=True)),
                ('billing_status', models.CharField(blank=True, max_length=100, null=True)),
                ('billing_status_discription', models.CharField(blank=True, max_length=100, null=True)),
                ('billing_group', models.CharField(blank=True, max_length=100, null=True)),
                ('unit_of_sales', models.CharField(blank=True, max_length=100, null=True)),
                ('order_approval_no', models.CharField(blank=True, max_length=100, null=True)),
                ('purchase_order_no', models.CharField(blank=True, max_length=100, null=True)),
                ('purchase_order_item', models.CharField(blank=True, max_length=100, null=True)),
                ('ack_delivery_date', models.DateField(auto_now=True)),
                ('currency_type', models.CharField(blank=True, max_length=100, null=True)),
                ('ship_to_party_no', models.CharField(blank=True, max_length=100, null=True)),
                ('ship_to_party_name', models.CharField(blank=True, max_length=100, null=True)),
                ('ship_to_country', models.CharField(blank=True, max_length=100, null=True)),
                ('ship_to_postal_code', models.CharField(blank=True, max_length=100, null=True)),
                ('ship_to_city', models.CharField(blank=True, max_length=100, null=True)),
                ('ship_to_street', models.CharField(blank=True, max_length=100, null=True)),
                ('ship_to_street_for', models.CharField(blank=True, max_length=100, null=True)),
                ('insurance_scope', models.CharField(blank=True, max_length=100, null=True)),
                ('sold_to_country', models.CharField(blank=True, max_length=100, null=True)),
                ('sold_to_postal_code', models.CharField(blank=True, max_length=100, null=True)),
                ('sold_to_city', models.CharField(blank=True, max_length=100, null=True)),
                ('sold_to_street', models.CharField(blank=True, max_length=100, null=True)),
                ('sold_to_street_for', models.CharField(blank=True, max_length=100, null=True)),
                ('material_no', models.CharField(blank=True, max_length=100, null=True)),
                ('bupfpgpl', models.CharField(blank=True, max_length=100, null=True)),
                ('hs_code', models.CharField(blank=True, max_length=100, null=True)),
                ('hs_code_export', models.CharField(blank=True, max_length=100, null=True)),
                ('delivery_quantity', models.IntegerField(blank=True, null=True)),
                ('unit_of_delivery', models.CharField(blank=True, max_length=100, null=True)),
                ('storage_location', models.CharField(blank=True, max_length=100, null=True)),
                ('dil_output_date', models.DateField(auto_now=True)),
                ('sales_doc_type', models.CharField(blank=True, max_length=100, null=True)),
                ('sales_doc_type_discription', models.CharField(blank=True, max_length=100, null=True)),
                ('distribution_channel', models.CharField(blank=True, max_length=100, null=True)),
                ('distribution_channel_discription', models.CharField(blank=True, max_length=100, null=True)),
                ('shipping_invoice_no', models.CharField(blank=True, max_length=100, null=True)),
                ('invoice_item', models.CharField(blank=True, max_length=100, null=True)),
                ('tax_invoice_assessable_value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('tax_invoice_total_tax_value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('tax_invoice_total_value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('sales_item_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('packing_status', models.CharField(blank=True, max_length=100, null=True)),
                ('do_item_packed_quantity', models.IntegerField(blank=True, null=True)),
                ('packed_unit_quantity', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'SAPDispatchInstruction',
            },
        ),
    ]
