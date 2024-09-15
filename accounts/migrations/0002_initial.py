# Generated by Django 5.1 on 2024-09-15 17:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('pharmacy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctorprofile',
            name='pharmacies',
            field=models.ManyToManyField(blank=True, to='pharmacy.pharmacy'),
        ),
        migrations.AddField(
            model_name='doctorprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='availability',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availabilities', to='accounts.doctorprofile'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='accounts.doctorprofile'),
        ),
        migrations.AddField(
            model_name='doctorprofile',
            name='languages_spoken',
            field=models.ManyToManyField(blank=True, to='accounts.language'),
        ),
        migrations.AddField(
            model_name='medicalrecord',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medical_records', to='accounts.doctorprofile'),
        ),
        migrations.AddField(
            model_name='patientprofile',
            name='doctors',
            field=models.ManyToManyField(related_name='patients', through='accounts.Appointment', to='accounts.doctorprofile'),
        ),
        migrations.AddField(
            model_name='patientprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='medicalrecord',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medical_records', to='accounts.patientprofile'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='accounts.patientprofile'),
        ),
        migrations.AddField(
            model_name='pharmacistprofile',
            name='languages_spoken',
            field=models.ManyToManyField(blank=True, to='accounts.language'),
        ),
        migrations.AddField(
            model_name='pharmacistprofile',
            name='pharmacy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pharmacy.pharmacy'),
        ),
        migrations.AddField(
            model_name='pharmacistprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='prescription',
            name='medical_record',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions', to='accounts.medicalrecord'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='medication',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions', to='pharmacy.medication'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='prescribed_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions', to='accounts.doctorprofile'),
        ),
        migrations.AddField(
            model_name='review',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='accounts.doctorprofile'),
        ),
        migrations.AddField(
            model_name='review',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='accounts.patientprofile'),
        ),
        migrations.AddField(
            model_name='shareablelink',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shareable_links', to='accounts.patientprofile'),
        ),
        migrations.AlterUniqueTogether(
            name='review',
            unique_together={('doctor', 'patient')},
        ),
    ]
