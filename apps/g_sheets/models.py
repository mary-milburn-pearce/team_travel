
from django.contrib.auth.models import User
from django.db import models
# from oauth2client.contrib.django_util.storage import DjangoORMStorage
# from oauth2client.contrib.django_util.models import CredentialsField

# class FlowModel(models.Model):
#   id = models.ForeignKey(User, primary_key=True)
#   flow = FlowField()

# class CredentialsModel(models.Model):
#   id = models.ForeignKey(User, primary_key=True)
#   credential = CredentialsField()

# user = # A User object usually obtained from request.
# storage = Storage(CredentialsModel, 'id', user, 'credential')
# credential = storage.get()
# ...
# storage.put(credential)