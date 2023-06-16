# Generated by Django 4.1.3 on 2023-06-16 13:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0017_alter_user_first_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Community',
            fields=[
                ('community_id', models.AutoField(default=None, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField(blank=True, max_length=140)),
                ('cover', models.ImageField(blank=True, upload_to='covers/')),
                ('postlist', models.ManyToManyField(blank=True, related_name='postlist', to='network.post')),
                ('userlist', models.ManyToManyField(blank=True, related_name='userlist', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='community',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='network.community'),
        ),
        migrations.AddField(
            model_name='user',
            name='community',
            field=models.ManyToManyField(blank=True, default=None, null=True, related_name='users', to='network.community'),
        ),
    ]
