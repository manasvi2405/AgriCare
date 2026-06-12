from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from .forms import ContactForm
from .models import Article,Category,Product,ProductCategory,Brand
import requests,json
from user.models import Cart,CartItem,Order,OrderItem,Address,Wishlist
from django.contrib.auth.decorators import login_required
import razorpay
from django.views.decorators.csrf import csrf_exempt
import pickle
import joblib
import numpy as np
from django.core.files.storage import FileSystemStorage
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os
from .models import PlantDisease

# Create your views here.
def news(request):
    apikey=settings.NEWS_API_KEY
    url="https://gnews.io/api/v4/search?q=farming&lang=en&apikey="+apikey
    response=requests.get(url)
    response=response.json()
    data=response['articles']
    p = Paginator(data,4)
    page_num=request.GET.get('page')
    news=p.get_page(page_num)
    return render(request,'news.html',{'news':news})

def home(request):
    articles = Article.objects.filter(status='published')[0:3]
    products = Product.objects.filter(is_active=True)[0:8]

    return render(request,'home.html',{'articles':articles,'products':products})

def about(request):
    return render(request,'about.html',{})

def privacy(request):
    return render(request,'privacy.html',{})

def terms(request):
    return render(request,'terms.html',{})

def cart(request):
    return render(request,'cart.html',{})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # 1. Save the data to the database
            contact_instance = form.save()


            # 2. Extract data for the email
            user_name = form.cleaned_data['name']
            user_email = form.cleaned_data['email']
           
            # 3. Send the email
            try:
                send_mail(
                subject=f'Thank You, {user_name}!',
                message=f'Hi {user_name},\n\nWe have received your message. We will get back to you shortly.\n\nBest Regards,\nTeam AgriCare',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user_email],
                fail_silently=False)
            except Exception as e:
                print(f"Email sending failed: {e}")
           
            # 4. Add a success message to display on the page
            messages.success(request, "Your message has been sent successfully! Check your email for confirmation.")
       
            form = ContactForm()


    else:
    # GET request: Display an empty form
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

def blog(request,cat):
    category = Category.objects.get(id=cat)
    data = Article.objects.filter(status='published',category=cat)
    p = Paginator(data,6)
    page_num=request.GET.get('page')
    articles=p.get_page(page_num)
    return render(request,'blog.html',{'articles':articles,'category':category})

def article(request,id):
    article = Article.objects.get(id=id)
    return render(request,'article.html',{'article':article})

def shop(request,cat):
    category = ProductCategory.objects.get(id=cat)
    data = Product.objects.filter(is_active=True,category=cat)
    p = Paginator(data,8)
    page_num=request.GET.get('page')
    product=p.get_page(page_num)
    return render(request,'shop.html',{'products':product,'category':category})

def shopbybrand(request,brand):
    brand=Brand.objects.get(id=brand)
    data=Product.objects.filter(is_active=True,brand=brand)
    p=Paginator(data,8)
    page_num=request.GET.get('page')
    product=p.get_page(page_num)
    return render(request,'shop.html',{'products':product ,'category':brand})

def shopbycategory(request,cat):
    parentcategory=ProductCategory.objects.get(id=cat)
    category_ids = parentcategory.subcategories.all().values_list('id', flat=True)
    all_ids = [parentcategory.id] + list(category_ids)
    # Filter products
    data = Product.objects.filter(category_id__in=all_ids)
    p=Paginator(data,8)
    page_num=request.GET.get('page')
    product=p.get_page(page_num)
    return render(request,'shop.html',{'products':product ,'category':parentcategory})

def product(request,id):
    product=Product.objects.get(id=id)
    brand=product.brand
    brands_products=Product.objects.filter(is_active=True,brand=brand).exclude(id=id)
    category=product.category
    category_products=Product.objects.filter(is_active=True,category=category).exclude(id=id)
    return render(request,'product.html',{'product':product,'brands_products':brands_products,'category_products':category_products,})

@login_required
def add_to_cart(request,item_id):
    product=get_object_or_404(Product,id=item_id)
    # get the user active cart or create one
    cart,created=Cart.objects.get_or_create(user=request.user)
    # check if the product is already in the cart
    cart_item,item_created=CartItem.objects.get_or_create(cart=cart,product=product)
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')    

@login_required
def view_cart(request):
    # Fetch the cart for the logged-in user
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()  # Assuming related_name is default or set
   
    total_price = sum(item.product.selling_price * item.quantity for item in items)
   
    context = {
        'cart': cart,
        'items': items,
        'total_price': total_price,
    }
    return render(request, 'cart.html', context)


@login_required
def update_cart_quantity(request,action, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease' and cart_item.quantity > 1:
        cart_item.quantity -= 1
    elif action == 'decrease' and cart_item.quantity == 1:
        cart_item.delete()
        return redirect('view_cart')
    cart_item.save()
    return redirect('view_cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('view_cart')

def checkout_view(request):
    user = request.user
   
    # 1. Get the User's Cart
    try:
        cart = Cart.objects.get(user=user)
        cart_items = cart.items.all() # Uses the related_name 'items' from CartItem
    except Cart.DoesNotExist:
        return redirect('cart') # Redirect if cart is empty


    # 2. Fetch Saved Addresses
    addresses = Address.objects.filter(user=user).order_by('-is_default')
   
    # 3. Calculate Totals (using your existing @property)
    total_amount = cart.total_price


    context = {
        'cart': cart,
        'cart_items': cart_items,
        'addresses': addresses,
        'total_amount': total_amount,
    }
   
    return render(request, 'checkout.html', context)

@login_required
def process_order(request):
    #validate address
    if request.method=='POST':
        user=request.user
        address_id=request.POST.get('address_id')
        payment_method = request.POST.get('payment_method')
        #validate address
        if not address_id:
            return redirect('checkout_view')
        shipping_address=get_object_or_404(Address,id=address_id,user=user)
        #get user cart
        cart=get_object_or_404(Cart,user=user)
        if not cart.items.exists():
            return redirect('view_cart')
        #create the order object
        order=Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            total_amount=cart.total_price,
            status='Pending',
            payment_method=payment_method
        )
     #Snapshot cartitems into orderitems
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.selling_price,
                quantity=item.quantity
            )
        if payment_method == "cod":

            return render(request, "success.html", {
                "order": order
            })
        else:
            client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.RAZOR_PAY_KEY_SECRET))
            razorpay_order = client.order.create({
                "amount": int(order.total_amount * 100), # Amount in paise
                "currency": "INR",
                "receipt": f"order_{order.id}"
            })
            order.razorpay_order_id = razorpay_order['id']
            order.save()
            return redirect('payment_page', order_id=order.id)

    return render(request, 'checkout.html', {})

def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
   
    context = {
        'order': order,
        'razorpay_key_id': settings.RAZOR_PAY_KEY_ID, # Store this in settings.py
        'amount_in_paise': int(order.total_amount * 100),
        'currency': 'INR',
        'callback_url': "http://127.0.0.1:8000/payment/verify/", # Your verification URL
    }
    return render(request, 'payment.html', context)

@csrf_exempt
def payment_verify(request):
    if request.method == "POST":
        # 1. Extract data from Razorpay's callback
        payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        # 2. Initialize Razorpay Client
        client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.RAZOR_PAY_KEY_SECRET))

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        try:
            # 3. Verify the signature
            client.utility.verify_payment_signature(params_dict)
           
            # 4. Success: Update Order in Database
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.is_paid = True
            order.razorpay_payment_id = payment_id
            order.status = 'Packed' # Or your desired next status
            order.save()

            Cart.objects.get(user=order.user).items.all().delete()

            return render(request, 'success.html', {'order': order})

        except razorpay.errors.SignatureVerificationError:
            # 6. Failure: Signature mismatch
            return render(request, 'failure.html', {'error': 'Payment verification failed.'})
        except Order.DoesNotExist:
            return render(request, 'failure.html', {'error': 'Order not found.'})

    return redirect('home')

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in ["Pending", "Packed"]:
        order.status = "Cancelled"
        order.save()
        messages.success(request, "Order cancelled successfully.")
    else:
        messages.error(request, "This order cannot be cancelled.")

    return redirect('track_order')

def croprecommendation(request):
    res=""
    status="" 
    sample={}
    conf=None
    try:
        if request.method=='POST':
            with open("./app/crop_recommendation_model.pkl","rb") as f:
               b=pickle.load(f)
            N=request.POST.get('N')
            P=request.POST.get('P')
            K=request.POST.get('K')
            ph=request.POST.get('ph')
            temp=request.POST.get('temp')
            humidity=request.POST.get('humidity')
            rainfall=request.POST.get('rainfall')
            sample={'N':N,'P':P,'K':K,'temp':temp,'humidity':humidity,'ph':ph,'rainfall':rainfall}
            sample_values=list(sample.values())
            res=(b['model'].predict([sample_values])[0])
            conf=(b['model'].predict_proba([sample_values])[0])
            conf=conf.max()
            conf=conf*100
            status="success"
        else:
            pass
    except Exception as e:
        res="oops, error"
        status="danger"
    return render(request,'croprecommendation.html',{'res':res,'status':status,'sample':sample,'conf':conf})


yield_model = joblib.load('./app/crop_yield_model.pkl')
state_encoder = joblib.load('./app/state_encoder.pkl')
season_encoder = joblib.load('./app/season_encoder.pkl')
crop_encoder = joblib.load('./app/crop_encoder.pkl')

def predict_yield(request):
    states=['Assam' ,'Karnataka' ,'Kerala' ,'Meghalaya' ,'West Bengal' ,'Puducherry', 'Goa',
 'Andhra Pradesh', 'Tamil Nadu', 'Odisha' ,'Bihar' ,'Gujarat' ,'Madhya Pradesh',
 'Maharashtra' ,'Mizoram' ,'Punjab' ,'Uttar Pradesh', 'Haryana',
 'Himachal Pradesh' ,'Tripura' ,'Nagaland' ,'Chhattisgarh', 'Uttarakhand',
 'Jharkhand' ,'Delhi' ,'Manipur' ,'Jammu and Kashmir' ,'Telangana',
 'Arunachal Pradesh', 'Sikkim']
    seasons=['Whole Year', 'Kharif' ,'Rabi', 'Autumn', 'Summer','Winter']
    crops=['Arecanut', 'Arhar/Tur', 'Castor seed', 'Coconut ', 'Cotton(lint)',
 'Dry chillies', 'Gram', 'Jute', 'Linseed', 'Maize', 'Mesta', 'Niger seed',
 'Onion', 'Other  Rabi pulses', 'Potato', 'Rapeseed &Mustard', 'Rice',
 'Sesamum', 'Small millets', 'Sugarcane', 'Sweet potato', 'Tapioca', 'Tobacco',
 'Turmeric', 'Wheat', 'Bajra', 'Black pepper', 'Cardamom', 'Coriander', 'Garlic',
 'Ginger', 'Groundnut', 'Horse-gram', 'Jowar', 'Ragi', 'Cashewnut', 'Banana',
 'Soyabean', 'Barley', 'Khesari', 'Masoor', 'Moong(Green Gram)',
 'Other Kharif pulses', 'Safflower', 'Sannhamp', 'Sunflower', 'Urad',
 'Peas & beans (Pulses)', 'other oilseeds', 'Other Cereals', 'Cowpea(Lobia)',
 'Oilseeds total', 'Guar seed', 'Other Summer Pulses', 'Moth']
    context = {'states':states,'seasons':seasons,'crops':crops}
    if request.method == 'POST':
        try:
            # 1. Get data from POST
            state = request.POST.get('state')
            season = request.POST.get('season')
            crop = request.POST.get('crop')
            area = float(request.POST.get('area'))
            rainfall = float(request.POST.get('rainfall'))
            fertilizer = float(request.POST.get('fertilizer'))
            pesticide = float(request.POST.get('pesticide'))
            avg_temp = float(request.POST.get('avg_temp'))
            print(state, season, crop, area, rainfall, fertilizer, pesticide, avg_temp)

            # 2. Transform Categorical data to match model training
            # We use transform([val])[0] to get the integer label
            state_encoded = state_encoder.transform([state])[0]
            crop_encoded = crop_encoder.transform([crop])[0]
            season_encoded = season_encoder.transform([season])[0]

            # 3. Create input array (Ensure this order matches your X_train columns)
            features = np.array([[
                crop_encoded,
                season_encoded,
                state_encoded,
                area,
                rainfall,
                fertilizer,
                pesticide,
                avg_temp
            ]])

            # 4. Predict
            prediction = yield_model.predict(features)[0]
            context["prediction"] = round(float(prediction), 2)

        except Exception as e:
            context["error"] = f"Error in prediction: {e}"

    return render(request, 'predict_yield.html', context)

MODEL_PATH=os.path.join(os.path.dirname(__file__),'plant_disease_model_v2.h5')
model=load_model(MODEL_PATH)

def preprocess_for_model(img_path):
    img=image.load_img(img_path,target_size=(224,224))
    img_array=image.img_to_array(img)
    img_array=np.expand_dims(img_array,axis=0)
    return img_array/255.0
CLASS_NAMES=[]

def detectdisease(request):
    CLASS_NAMES=PlantDisease.objects.values_list('name',flat=True)
    context={}
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_file = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        # Get the absolute path for processing
        filepath = os.path.join(fs.location, filename)
        uploaded_file_url = fs.url(filename)
        img_array=preprocess_for_model(filepath)
        predictions=model.predict(img_array)
        result_index=int(np.argmax(predictions[0]))
        confidence=float(predictions[0][result_index])
        if confidence < 0.4:
            return render(request,'detectdisease.html',{
                'error':"The model is unsure. Please provide a clearer photo of the leaf.",
                'image': uploaded_file_url
            })
        try:
            disease_name = CLASS_NAMES[result_index]
            data = PlantDisease.objects.get(name=disease_name)
            context = {
                'disease': data.name,
                'explanation': data.explanation,
                'solution': data.solution,
                'prevention': data.prevention,
                'image': uploaded_file_url,
                'confidence': f"{confidence * 100:.2f}%",
                'prediction':True
            }
        except PlantDisease.DoesNotExist:
            context = {'error': f"Disease {disease_name} not found in database."}
    return render(request, 'detectdisease.html', context)




