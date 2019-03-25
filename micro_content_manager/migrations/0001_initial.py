# Generated by Django 2.1.7 on 2019-03-24 17:00

from django.db import migrations, models
import djongo.models.fields
import micro_content_manager.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice_text', models.CharField(max_length=200)),
                ('votes', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='MicroLearningContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('text', djongo.models.fields.ListField()),
                ('video', djongo.models.fields.EmbeddedModelField(model_container=micro_content_manager.models.Video, null=True)),
                ('meta_data', djongo.models.fields.EmbeddedModelField(model_container=micro_content_manager.models.MetaData, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('choices_text', models.TextField()),
                ('answer', models.TextField()),
                ('explanation', models.TextField()),
                ('choices', models.ManyToManyField(to='micro_content_manager.Choice')),
            ],
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='microlearningcontent',
            name='mc_tags',
            field=models.ManyToManyField(to='micro_content_manager.Tag'),
        ),
        migrations.AddField(
            model_name='microlearningcontent',
            name='questions',
            field=models.ManyToManyField(to='micro_content_manager.Question'),
        ),
    ]
