# Generated by Django 4.1 on 2023-12-04 16:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("base", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Mixnet",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("voting_id", models.PositiveIntegerField()),
                ("auth_position", models.PositiveIntegerField(default=0)),
                (
                    "auths",
                    models.ManyToManyField(related_name="mixnets", to="base.auth"),
                ),
                (
                    "key",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="mixnets",
                        to="base.key",
                    ),
                ),
                (
                    "pubkey",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="mixnets_pub",
                        to="base.key",
                    ),
                ),
            ],
        ),
    ]
