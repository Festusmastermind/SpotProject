from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from spotlocator.models import format_phone_number
from spotlocator.models import MenuList, Newsletter
from spotlocator.forms import OwnerProfileForm, MenuCreateForm, SubscriptionForm
from validate_email import validate_email
from django.db.models import Q
from SpotProject.settings import EMAIL_HOST_USER
User = get_user_model()



def index(request):
    template_name = 'spotlocator/index.html' # global_var

    # menulist pagination
    menulist_list = MenuList.objects.all().order_by("-order_name")
    paginator = Paginator(menulist_list, 4)
    page = request.GET.get('page')
    try:
        menulist = paginator.page(page)
    except PageNotAnInteger:
        menulist = paginator.page(1)
    except EmptyPage:
        menulist = paginator.page(paginator.num_pages)

    # spotowners pagination
    spotowners_list = User.objects.filter(user_type='2')
    paginator = Paginator(spotowners_list, 4)
    page = request.GET.get('page')
    try:
        spotowner = paginator.page(page)
    except PageNotAnInteger:
        spotowner = paginator.page(1)
    except EmptyPage:
        spotowner = paginator.page(paginator.num_pages)

    # receiving the queries
    query1 = request.GET.get("q")
    query2 = request.GET.get("query")
    #Search field for SpotOwners
    if query1:
        owners = User.objects.filter(user_type='2')
        spotowners = owners.filter(Q(state__icontains=query1)|
                                    Q(city__icontains=query1)|
                                    Q(address__icontains=query1)).distinct()
        if spotowners.exists():
            #paginate_obj(request, spotowner, spotowners)
            paginator = Paginator(spotowners, 4)
            page = request.GET.get('page')
            try:
                spotowner = paginator.page(page)
            except PageNotAnInteger:
                spotowner = paginator.page(1)
            except EmptyPage:
                spotowner = paginator.page(paginator.num_pages)

            total_search = spotowners.count()
            if total_search > 0:
                messages.success(request, f'We found {total_search} SharwamaSpots near your location')
                context = {'spotowners': spotowner, 'menulist':menulist}
                return render(request, template_name, context)
        else:
            messages.info(request, f'Ooops!! ...None Found')
            return render(request, template_name, {'menulist': menulist})
    # Search field for sharwama only
    elif query2:
        menulist2 = MenuList.objects.filter(order_name__icontains=query2).order_by("-order_name")
        if menulist2.exists():
            #paginate_obj(request, menulist, menulist2) # when an item is searched, it retain the pag_object.
            paginator = Paginator(menulist2, 4)
            page = request.GET.get('page')
            try:
                menulist = paginator.page(page)
            except PageNotAnInteger:
                menulist = paginator.page(1)
            except EmptyPage:
                menulist = paginator.page(paginator.num_pages)
            total_count = menulist2.count()
            if total_count > 0:
                messages.success(request, f'We found {total_count} Sharwama for you...Order Now')
            context = {'spotowners': spotowner, 'menulist': menulist}
            return render(request, template_name, context)
        else:
            messages.info(request, f'Sharwama Type not found')
            return render(request, template_name, {'spotowners': spotowner, 'menulist':menulist})

    # handling of the subcription form
    if request.method == 'POST':
        context = {'spotowners': spotowner, 'menulist': menulist}
        email_obj = Newsletter()
        email = request.POST.get('sub_email')
        # validating the email
        if Newsletter.objects.filter(sub_email=email).exists():
            messages.warning(request, f'This is an already registered email')
            return render(request, template_name, context)
        if not validate_email(email):
            messages.warning(request, f'Email is not Valid')
            return render(request, template_name, context)
        email_obj.sub_email = email
        subject = 'SharwamaLocator Notification'
        message = 'Explore our rich features to enjoy delicious sharwama' # suppose to be dynamic
        from_email = EMAIL_HOST_USER
        recipient_list = email_obj.sub_email

        # sending the mssg
        send_mail(subject, message, from_email, [recipient_list], fail_silently=False)
        email_obj.save()
        messages.success(request, f'Thanks for subscribing to our site')
    context = {
        'spotowners': spotowner,
        'menulist': menulist
    }
    return render(request, template_name, context)

# to be debug
def paginate_obj(request, x, y):
    paginator = Paginator(y, 4)
    page = request.GET.get('page')
    try:
        x = paginator.page(page)
    except PageNotAnInteger:
        x = paginator.page(1)
    except EmptyPage:
        x = paginator.page(paginator.num_pages)
    return x, y

def register(request):
    # if the request is post
    if request.method == 'POST':
        context = {}
        template_name = 'spotlocator/register.html'
        user = User()
        # validating the fields manually i.e. not django automated way
        if User.objects.filter(email=request.POST.get('email')).exists():
            messages.warning(request, f'Email already exists')
            return render(request, template_name, context)
        if not validate_email(request.POST.get('email')):
            messages.warning(request, f'Email is not Valid')
            return render(request, template_name, context)
        number = request.POST.get('number', None)
        if number:
            number = format_phone_number(number)
            if not number:
                messages.warning(request, f'Invalid Phone number')
                return render(request, template_name, context)
        else:
            messages.warning(request, f'Phone number is required')
            return render(request, template_name, context)
        if User.objects.filter(number=number).exists():
            messages.warning(request, f'Contact number already exists')
            return render(request, template_name, context)
            # receiving the values
        user_type = request.POST.get('type')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        spotname = request.POST.get('spotname')
        spotlocation = request.POST.get('spotlocation')
        if user_type == 'customer':
            if firstname and lastname is None:
                messages.warning(request, f'First and lastname is required')
                return render(request, template_name, context)
            # accepting the values into the database...
            user.first_name = firstname
            user.last_name = lastname
            user.user_type = 1
        elif user_type == 'spotowner':
            if spotname and spotlocation is None:
                messages.warning(request, f'Spotname and SpotLocation is required')
                return render(request, template_name, context)
            user.spotname = spotname
            user.address = spotlocation
            user.user_type = 2
        user_number = number
        password = request.POST.get('password')
        if password is None:
            messages.warning(request, f'Enter your password')
            return render(request, template_name, context)
        user.email = request.POST.get('email')
        user.number = user_number
        user.password = password
        user.set_password(password)
        user.save()
        return redirect('login')

        # if the request is get method
    else:
        context = {}
        template_name = 'spotlocator/register.html'
        return render(request, template_name, context)



def login_view(request):
   # Post method
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.user_type == '1':
                return redirect('index')
            elif user.user_type == '2':
                messages.success(request, f'Complete your profile information below')
                return redirect('owners_profile')
            else:
                messages.info(request, f'Invalid Account, Please Register')
                return redirect('register')
        else:
            messages.warning(request, f'Invalid email or password supplied')
            return render(request, 'spotlocator/login.html')
     # if Get method
    else:
        return render(request, 'spotlocator/login.html')

@login_required(redirect_field_name='owners_profile', login_url='login')
def owners_profiles(request):
    user = request.user
    if user.user_type != '2':
        messages.info(request, f'Ooops! you are not permitted ')
        return redirect('login')
    if request.method == 'POST':
        owner_form = OwnerProfileForm(request.POST, request.FILES, instance=request.user)
        if owner_form.is_valid():
            owner_form.save()
        messages.info(request, f'Your account has been updated!.')
        return redirect('owners_profile')

    else:
        owner_form = OwnerProfileForm(instance=request.user)
    context = {'form': owner_form}
    return render(request, 'spotlocator/owners_profiles.html', context)


@login_required(redirect_field_name='create_menu', login_url='login')
def create_menu(request):
    user = request.user
    if user.user_type != '2':
        messages.info(request, f'You are not permitted')
        return redirect('login')
    template_name = 'spotlocator/create_menu.html'
    if request.method == 'POST':
        menu_form = MenuCreateForm(request.POST, request.FILES)
        if menu_form.is_valid():
            menu_owner = menu_form.save(commit=False)
            menu_owner.owner = request.user
            menu_owner.save()
            messages.success(request, f'Menu added')
            return redirect('create-menu')
        else:
            messages.info(request, f'Invalid data supplied')
            return render(request, template_name, {'form': menu_form})
    else:
        menu_form = MenuCreateForm()
    # passing the context of the data to the view..
    current_user = user
    menus = current_user.menulist_set.all()
    context = {
        'form': menu_form,
        'menus': menus
    }
    return render(request, template_name, context)

@login_required(redirect_field_name='create-menu', login_url='login')
def menu_list(request):
    user = request.user
    if user.user_type != '2':
        messages.info(request, f'You are not permitted')
        return redirect('login')
    current_user = user
    template_name = 'spotlocator/menulist.html'
    menus = current_user.menulist_set.all()  # associates the menulist items to the creator[current user]
    if menus:
        menus_total = menus.count()
        if menus_total > 0:
            messages.info(request, f'{menus_total} item is added, Add more!')
            return render(request, template_name, {'menus': menus})
    else:
        messages.info(request, f'You have zero menu item, Click the create-menu to Add!.')
        return render(request, template_name)
    return render(request, template_name)


def delete_menu(request, menu_id):
    #getting the related set makes sure that only the owner can delete the menu_item...
    user = request.user
    if user.user_type != '2':
        messages.info(request, f'You are not permitted')
        return redirect('login')
    current_user = user
    menus = current_user.menulist_set.get(pk=menu_id)
    menus.delete()
    return redirect('menulist')


def logout_view(request):
    logout(request)
    messages.info(request, f'Logged out Successfully')
    return redirect('login')


# not using this one for the newsletter
def subscription_view(request):
    # using django form to process the form...
    # plus it will be included inside the index view..
    template_name = 'spotlocator/index.html'
    if request.method == 'POST':
        form = SubscriptionForm(request.POST or None)
        if form.is_valid():
            email_obj = form.save(commite=False)
            email_obj.sub_email = form.cleaned_data_get('sub_email')
            email_obj.save()
            # sending the mail
            subject = 'Horlacode Notification'
            message = 'Explore our rich features to enjoy awesome satisfaction.'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = form.cleaned_data.get('sub_email')
            # actual sending...
            send_mail(subject, message, from_email, [recipient_list], fail_silently=False)
            messages.success(request, 'You have subscribed succesfully')
            return redirect('index')
    else:
        form = SubscriptionForm()
    return render(request, template_name, {'form': form})



# custom python function...DRY principle



# def emailSubscription(request):
#     template_name = 'spotlocator/index.html'
#     sub = forms.SubscriptionForm()
#     if request.method == 'POST':
#         sub       = forms.SubscriptionForm(request.POST)
#         subject   = 'Welcome to SharwamaSport Notification'
#         message   = 'Explore our latest features by signing here..'
#         recipient = str(sub['sub_email'].value())
#         send_mail(subject, messages, EMAIL_HOST_USER, [recipient], fail_silently=False)
#         return render(request, template_name)
#     return render(request, template_name, {'form': sub})










    # form = SignupForm(request.POST or None)
    # if form.is_valid():
    #     save_it = form.save(commit=False)
    #     save_it.save()
    #     # send_mail(subject, message, from_email, to_list, fail_silently=True)
    #     subject = 'Thank you for your Pre-Order from CFE'
    #     message = 'Welcome to CFE! We very much appreciate your business./n'
    #     from_email = settings.EMAIL_HOST_USER
    #     to_list = [save_it.email, settings.EMAIL_HOST_USER]
    #
    #     send_mail(subject, message, from_email, to_list, fail_silently=True)
    #     messages.success(request, 'Thank you for your order. We will be in touch')
    #     return HttpResponseRedirect('/thank-you/')
    # return render(request, template_name, context)

