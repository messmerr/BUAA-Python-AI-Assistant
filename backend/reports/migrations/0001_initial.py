# Generated by Django 5.2.4 on 2025-07-25 11:45

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="LearningReport",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "period",
                    models.CharField(
                        choices=[
                            ("week", "一周"),
                            ("month", "一个月"),
                            ("semester", "一学期"),
                            ("all", "全部时间"),
                        ],
                        max_length=20,
                        verbose_name="时间段",
                    ),
                ),
                ("subjects", models.JSONField(default=list, verbose_name="科目列表")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("generating", "生成中"),
                            ("completed", "已完成"),
                            ("failed", "生成失败"),
                        ],
                        default="generating",
                        max_length=20,
                        verbose_name="状态",
                    ),
                ),
                (
                    "total_assignments",
                    models.IntegerField(default=0, verbose_name="总作业数"),
                ),
                (
                    "completed_assignments",
                    models.IntegerField(default=0, verbose_name="已完成作业数"),
                ),
                (
                    "average_score",
                    models.FloatField(default=0.0, verbose_name="平均得分"),
                ),
                (
                    "total_questions",
                    models.IntegerField(default=0, verbose_name="总提问数"),
                ),
                (
                    "report_content",
                    models.TextField(blank=True, verbose_name="报告内容"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
                (
                    "generated_by",
                    models.ForeignKey(
                        help_text="可以是学生自己或教师",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="generated_reports",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="生成者",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="learning_reports",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="学生",
                    ),
                ),
            ],
            options={
                "verbose_name": "学习报告",
                "verbose_name_plural": "学习报告",
                "db_table": "learning_reports",
                "ordering": ["-created_at"],
            },
        ),
    ]
