from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
import sys
# from django.contrib.auth import get_user_model
# from django.core.files.uploadedfile import InMemoryUploadedFile
# from django.urls import reverse
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _




class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email, first_name, last_name, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, first_name, last_name, password, **extra_fields)

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, first_name, last_name, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()



class Category(models.Model):

    title = models.CharField(max_length=150, db_index=True, verbose_name='Название категории')
    slug = models.SlugField(unique=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

    @staticmethod
    def get_all_categories():
        return Category.object.all()

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']


class Item(models.Model):


    category = models.ForeignKey('Category', on_delete=models.PROTECT, null=True, verbose_name='Категория')
    title = models.CharField(max_length=200, verbose_name='Наименование')
    content = models.TextField(verbose_name='Описание', null=True, blank=True)
    slug = models.SlugField(unique=True, null=True)
    price = models.PositiveIntegerField(verbose_name='Цена')
    image = models.ImageField(upload_to='photos', verbose_name='Фото', blank=True)
    classroom = models.URLField(blank=True, null=True,)
    class_code = models.CharField(max_length=7, null=True, blank=True)
    grade = models.PositiveIntegerField(verbose_name='Класс обучения', null=True, blank=True)
    subject = models.CharField(max_length=255, verbose_name='Предмет', null=True, blank=True)
    is_available = models.BooleanField(verbose_name='Наличие')

    def __str__(self):
        return self.title

    def get_model_name(self):
        return self.__class__.__name__.lower()

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})


    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['title']



class Customer(models.Model):

    user = models.OneToOneField(User, verbose_name='Пользователь', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, verbose_name='Имя')
    email = models.EmailField()
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Покупатель')
    date_ordered = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    complete = models.BooleanField(default=False, verbose_name='Оплачен')
    transaction_id = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderItem(models.Model):
    product = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Товар')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name='Заказ')
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name='Количество')

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

    class Meta:
        verbose_name = 'Товар заказа'
        verbose_name_plural = 'Товары заказов'


