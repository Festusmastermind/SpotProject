from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string
from django.conf import settings



# Create your models here.


def unique_generator(model, field, length=12, allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                                            'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    # Klass = instance.__class__
    # qs_exists = Klass.objects.filter(chat_id=chat_new_id).exists()
    unique = get_random_string(length=length, allowed_chars=allowed_chars)
    kwargs = {field: unique}
    qs_exists = model.objects.filter(**kwargs).exists()
    if qs_exists:
        return unique_generator(model, field)
    return unique

def format_phone_number(number):
    if len(number) == 13:
        if number.startswith('234'):
            return number
    elif len(number) == 11:
        if number.startswith('0'):
            return number.replace('0', '234', 1)
    elif len(number) == 10:
        return '234' + number
    return None


class User(AbstractUser):
    type_choices = (
        ('1', 'customer'),
        ('2', 'spotowner'),
    )
    user_type        = models.CharField(max_length=1, choices=type_choices, null=True, blank=True)
    spotname         = models.CharField(max_length=200, null=True, blank=True)
    logo             = models.ImageField(upload_to='Profile_pics', default='default.jpg') # Spot Account pics identity
    number           = models.CharField(unique=True, max_length=13, null=True, blank=True)
    email            = models.EmailField(unique=True, blank=True, null=True)  # this will override the default.
    city             = models.CharField(max_length=100, blank=True, null=True)
    state            = models.CharField(max_length=100, blank=True, null=True)
    instagram_handle = models.URLField(blank=True, null=True)
    address          = models.TextField(help_text='specified your location with comma', null=True, blank=True)
    latitude         = models.FloatField(default=0.0, null=True, blank=True)
    longitude        = models.FloatField(default=0.0, null=True, blank=True)
    recovery_email   = models.EmailField(unique=True, blank=True, null=True)
    recovery_phone   = models.CharField(max_length=13, null=True, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'user'
        ordering = ['-created_at']

    def __str__(self):
        return self.email


    def delete(self, **kwargs):
        pass
        super(User, self).delete(**kwargs)

    def save(self, *args, **kwargs):
        # generate a username and save into the DB
        self.username = unique_generator(User, 'username')
        super(User, self).save(*args, **kwargs)



class MenuList(models.Model):
    order_choices = (
        ('Chicken Double Sausage', 'Chicken Double Sausage'),
        ('Chicken Single Sausage', 'Chicken Single Sausage'),
        ('Chicken Plain', 'Chicken Plain'),
        ('Beef Double Sausage', 'Beef Double Sausage'),
        ('Beef Single Sausage', 'Beef Single Sausage'),
        ('Beef Plain', 'Beef Plain'),
        ('Double Hotdog', 'Double Hotdog'),
    )
    order_name   = models.CharField(choices=order_choices, max_length=50, blank=True, null=True)
    order_price  = models.FloatField(default=0.00)
    content      = models.TextField(blank=True, null=True)
    excludes     = models.TextField(blank=True, null=True)
    order_upload = models.ImageField(upload_to='order_pics', default='pics.jpg')
    owner        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.owner.spotname}' +" "+ f'{self.order_name}'

    def get_content(self):
        return self.content.split(",")

    def get_exlcudes(self):
        return self.excludes.split(",")

   # A method to reduce the size of the images...


class Newsletter(models.Model):
    sub_email = models.EmailField(blank=True, null=True)


    def __str__(self):
        return self.sub_email
















            # class Profile(models.Model):
#     user             = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     city             = models.CharField(max_length=100, blank=True, null=True)
#     state            = models.CharField(max_length=100, blank=True, null=True)
#     instagram_handle = models.URLField(blank=True, null=True)
#     latitude         = models.FloatField(default=0.0, null=True, blank=True)
#     longitude        = models.FloatField(default=0.0, null=True, blank=True)
#     recovery_email   = models.EmailField(unique=True, blank=True, null=True)
#     recovery_phone   = models.CharField(max_length=13, null=True, blank=True)

    #
    # def __str__(self):
    #     return self.user.email