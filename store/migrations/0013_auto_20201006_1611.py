# Generated by Django 3.0.7 on 2020-10-06 13:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_auto_20201005_1937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='makepayment',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.Order'),
        ),
    ]
