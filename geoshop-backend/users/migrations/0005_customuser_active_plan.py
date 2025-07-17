from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_customuser_phone'),  # Sua última migração existente
        ('plans', '0001_initial'),          # Dependência do app plans
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='active_plan',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='plans.Plan',
                db_column='active_plan_id',  # Nome explícito da coluna no banco
                verbose_name='Plano Ativo'
            ),
        ),
    ]