# Generated by Django 5.2.4 on 2025-07-16 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='brand',
        ),
        migrations.AlterField(
            model_name='product',
            name='package_type',
            field=models.CharField(choices=[('saco', 'Saco'), ('pacote', 'Pacote'), ('lata', 'Lata'), ('caixa', 'Caixa'), ('bandeja', 'Bandeja'), ('garrafa', 'Garrafa'), ('outro', 'Outro')], max_length=10),
        ),
    ]
