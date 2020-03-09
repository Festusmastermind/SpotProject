from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from spotlocator.models import format_phone_number
from django.contrib.auth import get_user_model
from spotlocator.models import MenuList
from spotlocator.forms import OwnerProfileForm, MenuCreateForm
from validate_email import validate_email
from django.db.models import Q


User = get_user_model()

# Functional Views / class based views...

def index(request):
    # handling two search functions simultaneously...
    if request.method == 'GET':
        context = {}
        if request.GET.get('status') == 'P':
            pass
        else:
            # dont really get the above code ...
            template_name = 'spotlocator/index.html'
            menulist = MenuList.objects.all()[:20]
            spotowners = User.objects.filter(user_type='2')
            query1 = request.GET.get("q")
            query2 = request.GET.get("query")
            # Search field for SpotOwners
            if query1:
                owners = User.objects.filter(user_type='2')
                spotowners = owners.filter(Q(state__icontains=query1)|
                                            Q(city__icontains=query1)|
                                            Q(address__icontains=query1)).distinct()
                if spotowners.exists():
                    total_search = spotowners.count()
                    if total_search > 0:
                        messages.success(request, f'We found {total_search} SharwamaSpots near your location')
                        menus = menulist
                        context = {'spotowners': spotowners, 'menus': menus}
                        return render(request, template_name, context)
                else:
                    messages.info(request, f'Ooops!! ...None Found')
                    menus = menulist
                    return render(request, template_name, {'menus': menus})
            # Search field for sharwama only
            if query2:
                menulist2 = MenuList.objects.filter(order_name__icontains=query2)
                if menulist2.exists():
                    total_count = menulist2.count()
                    if total_count > 0:
                        messages.success(request, f'We found {total_count} Sharwama for you...Order Now')
                        context = {'menus': menulist2, 'spotowners': spotowners}
                        return render(request, template_name, context)
                else:
                    messages.info(request, f'Sharwama Type not found')
                    return render(request, template_name, {'spotowners': spotowners})
            context = {
                'spotowners': spotowners,
                'menus': menulist
            }
            # trying to output the contents of the sharwama
            return render(request, template_name, context)

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


def menu_delete(request, menu_id):
    pass
    # try:
    #     menu_item = MenuList.objects.get(pk='menu_id')
    # except:
    #     menu_item = None
    # menu_item.delete()
    # return redirect('menulist')



def logout_view(request):
    logout(request)
    messages.info(request, f'Logged out Successfully')
    return redirect('login')




