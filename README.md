# Django Template Email Manager

![PyPI](https://img.shields.io/pypi/v/django-template-email-manager)
![GitHub](https://img.shields.io/github/license/mbacicc/django-template-email-manager)

Template Email Manager is a Django App that manages all the email communications of your Django project. You can create multiple sending accounts, HTML templates with attached images and email receivers. Everything is run-time customizable, since all the parameters are stored in DB. All messages are stored in a DB based queue.

## Features
- Allows you to use multiple source e-mail provider on the same Django project
- Allows you to use multiple source e-mail addresses on the same Django project
- Each configured email provider has its own attributes (max send attempts, delay between retries, and so on...)
- You can add and edit TXT and HTML e-mail templates at run-time, without the need to change the code
- You can attach picture and/or other format attachment to the e-mails
- Automatic queue management using [Django Background Tasks](https://github.com/arteria/django-background-tasks)
- Storage of all added and processed e-mails with status and logs

## System Architecture


## Docs


## Installation



## Screenshots


## FAQ

