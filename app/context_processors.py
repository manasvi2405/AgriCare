from .models import Category,Brand,ProductCategory,Article


def categories(request):
    return {'categories':Category.objects.all()}

def brands(request):
    return {'brands':Brand.objects.all()}


def productcategories(request):
    return {
        'pcategories': ProductCategory.objects.filter(parent__isnull=True).
        prefetch_related('subcategories')
    }

def recent_articles(request):
    articles = Article.objects.order_by('-created_at')[:2]  # latest 2
    return {'recent_articles': articles}


