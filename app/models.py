from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField

# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=200)
    phone_number = models.CharField(max_length=14)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        # Orders results by newest first automatically
        ordering = ['-created_at']
    def __str__(self):
         return f'{self.name} - {self.created_at.strftime("%Y-%m-%d")}'

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category/',blank=True, null=True)
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    def __str__(self):
        return self.name
    
        
class Article(models.Model):
    STATUS_CHOICES = (
        ('draft','Draft'),
        ('published','Published'),
    )
    CATEGORY_CHOICES = (
        ('category1','Category1'),
        ('category2','Category2'),
    )
    
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True)
    content = RichTextField(blank=True, null=True)
    featured_image = models.ImageField(upload_to='blog_images/',blank=True,null=True)
    article_image = models.ImageField(upload_to='blog_images/',blank=True,null=True)
    category=models.ForeignKey(Category, on_delete=models.CASCADE, null=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    published_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-published_date']

    def __str__(self):
        return self.title
    
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='brands/',blank=True, null=True)
    website = models.URLField(blank=True)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name 
    
class ProductCategory(models.Model):
    name=models.CharField(max_length=100, unique=True)
    image=models.ImageField(upload_to='categories/', blank=True, null=True)
    description=models.TextField(blank=True)
    parent=models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,related_name="subcategories")
    class Meta:
        verbose_name_plural="ProductCategories"
    def __str__(self):
        return self.name
    
#---CONSTANTS---
PRODUCT_TYPES=(
    ('seed','Seeds'),
    ('pesticide','Pesticide/Insecticide'),
    ('fertilizer','Fertilizer'),
    ('tools','Tools')
)

TOXICITY_LEVELS=(
    ('red','Red (Extremely Toxic)'),
    ('yellow','Yellow (Highly Toxic)'),
    ('blue','Blue (Moderately Toxic)'),
    ('green','Green (Slightly Toxic)'),
    ('None','No Toxicity/Organic'),
)

APPLICATION_METHODS=(
    ('spray','Foliar Spray'),
    ('drip','Drip Irrigation'),
    ('soil','Soil Application/Broadcasting'),
    ('seed_treatment','Seed Treatment'),
)

UNITS=(
    ('ml','Milliliter (ml)'),
    ('l','Liter (l)'),
    ('g','Gram (g)'),
    ('kg','Kilogram (kg)'),
    ('pkty','Packet'),
    ('unit','Unit')
)
    
class Product(models.Model):
    #--- BASIC INFO ---
    # We combine Name + Size usually, e.g., "Round 1L"
    name=models.CharField(max_length=200, help_text="e.g., Coragen 60ml")
    brand=models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)
    category=models.ForeignKey(ProductCategory, on_delete=models.CASCADE, null=True)
    product_type=models.CharField(max_length=20, choices=PRODUCT_TYPES)
    toxicity_levels=models.CharField(max_length=20,choices=TOXICITY_LEVELS)

    #--AGRI DETAILS (Repeated for every size)---
    technical_name=models.CharField(max_length=255, blank=True)
    target_crops=models.TextField(blank=True)
    dosage=models.CharField(max_length=255, blank=True)
    description=RichTextField(blank=True, null=True)
    is_organic=models.BooleanField(default=False)
    product_image = models.ImageField(upload_to='product_images/',blank=True,null=True)

    #---PRICING & STOCK (Specific to this row)---
    #Size Definition
    weight_volume=models.DecimalField(max_digits=10, decimal_places=2, help_text="e.g., 100")
    unit=models.CharField(max_length=10, choices=UNITS, help_text="e.g., ml")
    mrp=models.DecimalField(max_digits=10, decimal_places=2)
    selling_price=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    stock_qty=models.PositiveIntegerField(default=0)

    # batch info
    batch_number=models.CharField(max_length=100, blank=True)
    expiry_date=models.DateField(null=True, blank=True)

    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.weight_volume}{self.unit}"
    
    @property
    def in_stock(self):
        return self.stock_qty > 0
    @property
    def discount(self):
     if self.mrp and self.selling_price:
        return self.mrp - self.selling_price
     return 0

class PlantDisease(models.Model):
    name=models.CharField(max_length=100)
    explanation=models.TextField()
    solution=models.TextField()
    prevention=models.TextField()

    def __str__(self):
        return self.name