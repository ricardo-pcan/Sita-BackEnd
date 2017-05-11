# -*- coding: utf-8 -*-
import os
from hashlib import md5

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.contrib.gis.db import models
# from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from sita.core.db.models import TimeStampedMixin

class UserManager(BaseUserManager):
    """Custom Manager for crete users"""

    def _create_user(self, email, password, **extra_fields):
        """ Create new Users. """

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            last_login = timezone.now(),
            **extra_fields
        )
        user.set_password(password)
        user.save()

        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create a user."""

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """Create custom model User."""

    name = models.CharField(
        max_length=100
        )
    first_name = models.CharField(
        max_length=100
    )
    mothers_name = models.CharField(
        max_length=100
    )
    email = models.EmailField(
        max_length=254,
        unique=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('is_active')
    )
    is_staff = models.BooleanField(
        default=True,
        verbose_name=_('is_staff')
    )
    activation_code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    reset_pass_code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    conekta_customer = models.CharField(
        max_length=254
    )
    created_date = models.DateField(
        auto_now_add=True
    )
    updated_date = models.DateField(
        auto_now=True
    )
    logined_date = models.DateField(
        null=True
    )
    has_subscription = models.BooleanField(
        default=False
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        return "{0} {1}".format(self.name, self.last_name)

    def get_short_name(self):
        return "{0}".format(self.name)

class Subscription(TimeStampedMixin):
    """ Create The subscriptions from User."""

    expiration_date = models.DateField(
        editable=False,
        blank=True,
        null=True
    )
    is_current = models.BooleanField(
        default=True
    )
    is_test = models.BooleanField(
        default=False
    )
    time_in_minutes = models.IntegerField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )