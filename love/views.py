from django.shortcuts import render
from love.models import *
from django.shortcuts import render , redirect
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.core.mail import send_mail
from love.forms import UserProfileForm
from love.forms import UpdateProfileForm

# Create your views here.
def postlist(request):
    if request.GET.get('search'):
        search = request.GET.get('search')
        posts = PostModel.objects.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search)
        )
    elif request.GET.get('category'):
        category = request.GET.get('category')
        posts = PostModel.objects.filter(category_id =category)
    else:
        posts = PostModel.objects.all().order_by('-create_date')

    for p in posts:
        p.images = ImageModel.objects.filter(post=p.id).first()

    paginator = Paginator(posts, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'postlist.html', {'posts':page_obj})

@permission_required('my_blog.add_postmodel', login_url='/login')
def postcreate(request):
    if request.method == 'GET':
        category = CategoryModel.objects.all()
        return render(request, 'postcreate.html',{'category':category})
    if request.method == 'POST':
        post = PostModel.objects.create(
            title = request.POST.get('title'),
            content = request.POST.get('content'),
            author_id = request.user.id,
            category_id = request.POST.get('category')
        )
        images = request.FILES.getlist('image')
        for p in images:
            ImageModel.objects.create(
                image = p,
                post_id = post.id
            )
        messages.success(request, 'Post Created Success!')
        return redirect('postlist')
    
   
def postdetail(request, p_id):
    if request.method == "GET":
        post = PostModel.objects.get(id=p_id)
        cmt = Comment.objects.filter(post_id=p_id)
        post.images = ImageModel.objects.filter(post_id=p_id)
        return render(request, 'postdetail.html',{'post':post,'cmt':cmt})
    if request.method == "POST":
        if request.user.id == None:
            return redirect('/login')
        cmt = Comment.objects.create(
            content = request.POST.get('content'),
            post_id = p_id,
            author_id = request.user.id
        )
        return redirect(f'/blog/detail/{p_id}/#cmt')

@permission_required('my_blog.delete_postmodel', login_url='/login')
def postdelete(request, p_id):
    post = PostModel.objects.get(id=p_id)
    images = ImageModel.objects.filter(post_id=p_id)
    for i in images:
        i.image.delete()
    post.delete()
    messages.success(request, 'Post Deleted Success!')
    return redirect('/blog/list/')

@permission_required('my_blog.change_postmodel', login_url='/login')
def postupdate(request, p_id):
    if request.method == 'GET':
        post = PostModel.objects.get(id=p_id)
        category = CategoryModel.objects.all()
        post.images = ImageModel.objects.filter(post_id=p_id)
        return render(request, 'postupdate.html',{'post':post, 'category': category})

    if request.method == 'POST':
        post = PostModel.objects.get(id=p_id)
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        if request.FILES.get('image'):
            post.image.delete()
            post.image = request.FILES.get('image')
        post.category_id = request.POST.get('category')
        post.save()
        messages.success(request, 'Post Updated Success!')
        return redirect(f'/blog/detail/{p_id}')

def imagedelete(request, p_id, i_id):
    image = ImageModel.objects.get(id=i_id)
    image.image.delete()
    image.delete()
    return redirect(f'/blog/update/{p_id}')

def imagecreate(request,p_id):
    if request.method == "POST":
        image = ImageModel.objects.create(
            image = request.FILES.get('image'),
            post_id = p_id
        )
        return redirect (f'/blog/update/{p_id}')

def cmtdelete(request, p_id, c_id):
    cmt = Comment.objects.get(id=c_id)
    cmt.delete()
    return redirect(f'/blog/detail/{p_id}/#cmt')

def cmtupdate(request, p_id, c_id):
    if request.method == "GET":
        cmt = Comment.objects.get(id=c_id)
        return render(request, 'cmtupdate.html',{'cmt':cmt})
    if request.method == "POST":
        cmt = Comment.objects.get(id=c_id)
        cmt.content = request.POST.get('content')
        cmt.save()
        return redirect(f'/blog/detail/{p_id}/#cmt')

def myLogin(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(Q(email=username) | Q(username=username))
        except Exception:
            messages.error(request, 'Email or Password is incorrect !')
            return redirect('/login')
        else:
            if user.check_password(password):
                login(request, user)
                messages.success(request, 'Login Success!')
                return redirect('/blog/list')
            else:
                messages.error(request, 'Email or Password is incorrect !')
                return redirect('/login')
        
def mylogout(request):
    logout(request)
    messages.success(request, 'log out Successfully!')
    return redirect('/blog/list')

def myRegister(request):
    if request.method == "GET":
        return render(request,'register.html')
    if request.method == "POST":
        passwd1 = request.POST.get('password')
        passwd2 = request.POST.get('repassword')
        username = request.POST.get('username')
        email = request.POST.get('email')
        if passwd1 == passwd2:
            if User.objects.filter(username=username):
                messages.error(request,'Username already existed !')
                return redirect('/register')
            if User.objects.filter(email=email):
                messages.error(request, 'Email already exists !')
                return redirect('/register')
            user = User.objects.create(
                username = request.POST.get('username'),
                email = request.POST.get('email'),
                password = make_password(passwd1)
        )
            login(request, user)
            
            subject = 'welcome to GFG world'
            #message = f'Hi {user.username}, thank you'
            message = f'Hi {user.username}, thank you for registering!'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email,]
            send_mail(subject,message,email_from,recipient_list)
            

            messages.success(request, 'Register Success!')    
            return redirect('/blog/list')
        else:
            messages.error(request, 'Password is not the same!')
            return redirect('/register')

def profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        return render(request, 'profile.html', {'user_profile': user_profile})
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profile does not exist. Please create your profile.')
        return redirect('create_profile')
    
def create_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            messages.success(request, 'Profile created successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm()
    return render(request, 'create_profile.html', {'form': form})

def update_profile(request):
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Assuming 'profile' is the name of the profile page URL
    else:
        form = UpdateProfileForm(instance=request.user.userprofile)
    return render(request, 'update_profile.html', {'form': form})
