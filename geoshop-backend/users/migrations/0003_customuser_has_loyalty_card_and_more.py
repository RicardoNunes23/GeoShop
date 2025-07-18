# Generated by Django 5.2.4 on 2025-07-16 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customuser_cnpj'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='has_loyalty_card',
            field=models.BooleanField(default=False, help_text='Ative para permitir preços especiais para clientes fidelizados', verbose_name='Oferece cartão fidelidade?'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='use_bulk_pricing',
            field=models.BooleanField(default=False, help_text='Ative para permitir preços por quantidade nos produtos', verbose_name='Trabalha com quantidade mínima?'),
        ),
    ]
