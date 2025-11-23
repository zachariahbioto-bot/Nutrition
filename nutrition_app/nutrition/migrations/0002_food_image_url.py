from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('nutrition', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='food',
            name='image_url',
            field=models.URLField(max_length=500, null=True, blank=True),
        ),
    ]
