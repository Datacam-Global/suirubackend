# Generated by Django 5.2.3 on 2025-06-21 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("monitoring", "0007_contentmodelanalysis"),
    ]

    operations = [
        migrations.CreateModel(
            name="RegisteredPlatform",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("display_name", models.CharField(blank=True, max_length=100)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name="facebookpost",
            name="platform",
            field=models.CharField(default="facebook", max_length=50),
        ),
        migrations.AlterField(
            model_name="platformanalytics",
            name="platform_name",
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
