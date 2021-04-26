# Generated by Django 3.2 on 2021-04-26 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('template_email_manager', '0004_auto_20210426_1827'),
    ]

    operations = [
        migrations.RenameField(
            model_name='emailprototype',
            old_name='template_html',
            new_name='html_template',
        ),
        migrations.RenameField(
            model_name='emailqueue',
            old_name='template_html',
            new_name='html_template',
        ),
        migrations.AddField(
            model_name='contextclass',
            name='value_type',
            field=models.CharField(choices=[('INT', 'Integer Number'), ('FLO', 'Float'), ('STR', 'String'), ('DAT', 'Date'), ('TIM', 'Time'), ('DTI', 'DateTime')], default='INT', help_text='Used to format the content in a more readable way', max_length=5),
        ),
        migrations.AddField(
            model_name='emailconfig',
            name='address',
            field=models.EmailField(blank=True, help_text='Only needed when SMTP backend is used', max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='emailconfig',
            name='timeout',
            field=models.IntegerField(blank=True, default=30, help_text='Only needed when SMTP backend is used, SMTP server timeout time in seconds', null=True),
        ),
        migrations.AddField(
            model_name='emailconfig',
            name='use_ssl',
            field=models.BooleanField(blank=True, default=True, help_text='Only needed when SMTP backend is used, SMTP server Use SSL. Mutually exclusive with TLS', null=True),
        ),
        migrations.AlterField(
            model_name='contextclass',
            name='name',
            field=models.CharField(help_text='Name of the Context Class, must be Unique', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='emailconfig',
            name='backend',
            field=models.CharField(choices=[('SMTP', 'SMTP Backend'), ('CONS', 'Console Backend')], default='SMTP', help_text='When SMTP is chosen, all other fields are mandatory, otherwise when Console is chosen, Host, Port, TLS, Username and Password are not needed', max_length=5),
        ),
        migrations.AlterField(
            model_name='emailconfig',
            name='config_name',
            field=models.CharField(default='Default', help_text='Configuration Name, must be unique', max_length=255, unique=True, verbose_name='Config Name'),
        ),
        migrations.AlterField(
            model_name='emailconfig',
            name='default',
            field=models.BooleanField(default=True, help_text='If checked this is the default account when new messages have no selected account', verbose_name='default'),
        ),
        migrations.AlterField(
            model_name='emailconfig',
            name='host',
            field=models.CharField(blank=True, help_text='Only needed when SMTP backend is used, SMTP server host name', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='emailconfig',
            name='password',
            field=models.CharField(blank=True, help_text='Only needed when SMTP backend is used, SMTP server authentication password', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='emailconfig',
            name='port',
            field=models.IntegerField(blank=True, default=587, help_text='Only needed when SMTP backend is used, SMTP server host port', null=True),
        ),
        migrations.AlterField(
            model_name='emailconfig',
            name='use_tls',
            field=models.BooleanField(blank=True, default=True, help_text='Only needed when SMTP backend is used, SMTP server Use TLS. Mutually exclusive with SSL', null=True),
        ),
        migrations.AlterField(
            model_name='emailconfig',
            name='username',
            field=models.CharField(blank=True, help_text='Only needed when SMTP backend is used, SMTP server authentication user name', max_length=255, null=True),
        ),
    ]