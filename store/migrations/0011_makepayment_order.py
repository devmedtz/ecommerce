# Generated by Django 3.0.7 on 2020-10-05 16:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_order_cart_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='makepayment',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.Order'),
        ),
    ]
