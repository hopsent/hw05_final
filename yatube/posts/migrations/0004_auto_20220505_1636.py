# Generated by Django 2.2.6 on 2022-05-05 16:36

from django.db import migrations, models
import posts.validators


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20220416_0917'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date']},
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(validators=[posts.validators.validate_not_empty]),
        ),
    ]
