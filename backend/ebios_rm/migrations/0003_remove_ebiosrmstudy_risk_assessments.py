# Generated by Django 5.1.4 on 2024-12-11 11:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ebios_rm", "0002_alter_roto_target_objective"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="ebiosrmstudy",
            name="risk_assessments",
        ),
    ]
