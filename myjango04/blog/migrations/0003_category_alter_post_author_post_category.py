# Generated by Django 5.1.1 on 2024-12-16 11:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def create_initial_category(apps, schema_editor):
    # 최소 1개의 Category가 있도록 생성
    Category = apps.get_model("blog", "Category")

    is_existed = Category.objects.filter(pk=1).exists()
    if is_existed is False:
        Category.objects.create(name="initial", pk=1)


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0002_post_author"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
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
                ("name", models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterField(
            model_name="post",
            name="author",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="category",
            field=models.ForeignKey(
                default=1,  # pk=1인 Category를 기본값으로 참조
                on_delete=django.db.models.deletion.CASCADE,
                to="blog.category",
            ),
            preserve_default=False,
        ),
        migrations.RunPython(
            create_initial_category,
            migrations.RunPython.noop,
        ),
    ]
