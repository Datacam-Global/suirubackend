# Generated by Django 5.2.3 on 2025-06-17 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("monitoring", "0002_usersettings_email_verified"),
    ]

    operations = [
        migrations.CreateModel(
            name="FacebookPost",
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
                ("post_id", models.CharField(max_length=50, unique=True)),
                ("created_time", models.CharField(max_length=50)),
                ("timestamp", models.BigIntegerField()),
                ("post_type", models.CharField(max_length=50)),
                ("text", models.TextField(blank=True)),
                ("text_lang", models.CharField(blank=True, max_length=10)),
                ("text_tagged_users", models.JSONField(default=list)),
                ("text_tags", models.JSONField(default=list)),
                ("attached_link", models.URLField(blank=True)),
                ("attached_link_description", models.TextField(blank=True)),
                ("attached_image_url", models.URLField(blank=True)),
                ("attached_image_url_s3", models.URLField(blank=True)),
                ("attached_image_content", models.TextField(blank=True)),
                ("attached_medias_id", models.JSONField(default=list)),
                ("attached_medias_preview_url", models.JSONField(default=list)),
                ("attached_medias_preview_url_s3", models.JSONField(default=list)),
                ("attached_medias_preview_content", models.JSONField(default=list)),
                ("attached_post_id", models.CharField(blank=True, max_length=50)),
                ("attached_video_preview_url", models.URLField(blank=True)),
                ("attached_video_preview_url_s3", models.URLField(blank=True)),
                ("attached_video_url", models.URLField(blank=True)),
                ("post_screenshot", models.URLField(blank=True)),
                ("reactions_like_count", models.IntegerField(default=0)),
                ("reactions_love_count", models.IntegerField(default=0)),
                ("reactions_haha_count", models.IntegerField(default=0)),
                ("reactions_wow_count", models.IntegerField(default=0)),
                ("reactions_sad_count", models.IntegerField(default=0)),
                ("reactions_angry_count", models.IntegerField(default=0)),
                ("reactions_support_count", models.IntegerField(default=0)),
                ("reactions_total_count", models.IntegerField(default=0)),
                ("comments_count", models.IntegerField(default=0)),
                ("shares_count", models.IntegerField(default=0)),
                ("video_view_count", models.IntegerField(default=0)),
                ("video_duration", models.IntegerField(default=0)),
                ("overlay_text", models.TextField(blank=True)),
                ("fact_checks", models.JSONField(default=list)),
                ("owner_id", models.CharField(max_length=50)),
                ("owner_username", models.CharField(max_length=100)),
                ("owner_full_name", models.CharField(max_length=200)),
                ("group_id", models.CharField(blank=True, max_length=50)),
                ("recommends", models.BooleanField(default=False)),
                ("tagged_location_id", models.CharField(blank=True, max_length=50)),
                ("post_location_id", models.CharField(blank=True, max_length=50)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-timestamp"],
            },
        ),
    ]
