from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from ckeditor.fields import RichTextField
from app.models import Product


class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(blank=True, null=True, verbose_name="Date of Birth")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    city = models.CharField(max_length=100, blank=True)


    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()




# --- 2. Cart Management (My Cart) ---


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Cart for {self.user.username}"
   
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


    @property
    def total_price(self):
        return self.quantity * self.product.selling_price


# --- 3. Order & Payment Management (Checkout, Razorpay & History) ---
class Address(models.Model):
    ADDRESS_TYPE_CHOICES = [
        ('Home', 'Home'),
        ('Work', 'Work'),
        ('Other', 'Other'),
    ]


    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=100, help_text="Name of the person receiving the package")
    phone_number = models.CharField(max_length=15)
   
    # Detailed Address Fields
    street_address = models.CharField(max_length=255) # House No, Street, Colony
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)     # Zip/Pin Code
    country = models.CharField(max_length=100, default='India')
   
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='Home')
    is_default = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.full_name} - {self.city} ({self.address_type})"
   
    def save(self, *args, **kwargs ):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
       # If this is the user's only address, force it to be default
        if not Address.objects.filter(user=self.user).exists():
            self.is_default = True
        super(Address,self).save(*args, **kwargs)


    class Meta:
        verbose_name_plural = "Addresses"


class Order(models.Model):
    # Order Status Choices
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Packed', 'Packed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
   
    # Payment & Order Info
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=20, null=True, blank=True)
   
    # Razorpay Specific Fields
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at'] # Shows latest orders first

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True) # Keep record even if product is deleted
    price = models.DecimalField(max_digits=10, decimal_places=2) # Snapshot of price at time of purchase
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

