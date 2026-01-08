from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login,logout
from .forms import SignupForm
from .models import User
from .forms import PGForm
from .forms import RoomForm
from .forms import BookingForm
from .models import Booking
from .models import Room
from .models import PG
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Sum
User = get_user_model()


def index(request):
    return render(request, 'index.html')





def signup_view(request, role):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # password match check
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('signup', role=role)

        # username exists check
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup', role=role)

        # create user
        user = User.objects.create_user(
            username=username,
            password=password,
            role=role
        )

        user.is_active = True

        if role in ['ADMIN', 'CUSTOMER']:
            user.is_approved = True
        else:
            user.is_approved = False

        user.save()

        messages.success(request, "Signup successful. Please login.")
        return redirect('login', role=role)

    return render(request, 'signup.html', {'role': role})





def login_view(request, role):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        # ❌ invalid credentials
        if user is None:
            messages.error(request, "Invalid username or password")
            return redirect('login', role=role)

        # ❌ role mismatch
        if user.role != role:
            messages.error(request, "You are not allowed to login here")
            return redirect('login', role=role)

        # ❌ not approved
        if not user.is_approved:
            messages.error(request, "Waiting for admin approval")
            return redirect('login', role=role)

        # ✅ SUCCESS LOGIN
        login(request, user)
        return redirect('dashboard')

    return render(request, 'login.html', {'role': role})



@login_required
def admin_approve_pg_owners(request):
    if request.user.role != 'ADMIN':
        return redirect('dashboard')

    pending_owners = User.objects.filter(
        role='PG_OWNER',
        is_approved=False
    )

    return render(
        request,
        'admin/approve_pg_owners.html',
        {'pending_owners': pending_owners}
    )



@login_required
def approve_pg_owner(request, user_id):
    if request.user.role != 'ADMIN':
        return redirect('dashboard')

    owner = User.objects.get(id=user_id, role='PG_OWNER')
    owner.is_approved = True
    owner.save()

    messages.success(request, "PG Owner approved successfully")
    return redirect('approve_pg_owners')


@login_required
def reject_pg_owner(request, user_id):
    if request.user.role != 'ADMIN':
        return redirect('dashboard')

    User.objects.filter(id=user_id, role='PG_OWNER').delete()
    messages.success(request, "PG Owner rejected and deleted")

    return redirect('approve_pg_owners')




from django.db.models import Sum

@login_required
def dashboard(request):
    user = request.user

    # ADMIN
    if user.role == 'ADMIN':
        context = {
            'total_users': User.objects.count(),
            'total_owners': User.objects.filter(role='PG_OWNER').count(),
            'pending_owners': User.objects.filter(role='PG_OWNER', is_approved=False).count(),
            'total_customers': User.objects.filter(role='CUSTOMER').count(),
            'total_pgs': PG.objects.count(),
            'total_bookings': Booking.objects.count(),
        }
        return render(request, 'admin/dashboard.html', context)

    # PG OWNER  ✅ ADD THIS
    elif user.role == 'PG_OWNER':
        my_pgs = PG.objects.filter(owner=user)

        total_rooms = Room.objects.filter(pg__owner=user).aggregate(
            total=Sum('total_rooms')
        )['total'] or 0

        available_rooms = Room.objects.filter(pg__owner=user).aggregate(
            total=Sum('available_rooms')
        )['total'] or 0

        pending_bookings = Booking.objects.filter(
            room__pg__owner=user,
            status='PENDING'
        ).count()

        approved_bookings = Booking.objects.filter(
            room__pg__owner=user,
            status='APPROVED'
        ).count()
        income = Booking.objects.filter(
            room__pg__owner=user,
            status='APPROVED'
        ).aggregate(total=Sum('room__price'))['total'] or 0


        context = {
            'my_pgs': my_pgs.count(),
            'total_rooms': total_rooms,
            'available_rooms': available_rooms,
            'pending_bookings': pending_bookings,
            'approved_bookings': approved_bookings,
            'income': income,
        }

        return render(request, 'owner/dashboard.html', context)

    # CUSTOMER
    elif user.role == 'CUSTOMER':
        total_pgs = PG.objects.filter(owner__is_approved=True).count()
        my_bookings = Booking.objects.filter(customer=user).count()
        approved = Booking.objects.filter(customer=user, status='APPROVED').count()

        context = {
            'total_pgs': total_pgs,
            'my_bookings': my_bookings,
            'approved': approved,
        }

        return render(request, 'customer/dashboard.html', context)







@login_required
def add_pg(request):
    if request.user.role != 'PG_OWNER':
        return redirect('dashboard')

    form = PGForm()

    if request.method == 'POST':
        form = PGForm(request.POST, request.FILES)
        if form.is_valid():
            pg = form.save(commit=False)
            pg.owner = request.user
            pg.save()
            return redirect('owner_pg_list')

    return render(request, 'owner/add_pg.html', {'form': form})

@login_required
def owner_pg_list(request):
    if request.user.role != 'PG_OWNER':
        return redirect('dashboard')

    pgs = PG.objects.filter(owner=request.user)
    return render(request, 'owner/pg_list.html', {'pgs': pgs})


@login_required
def owner_bookings(request):
    if request.user.role != 'PG_OWNER':
        return redirect('dashboard')

    bookings = Booking.objects.filter(
        room__pg__owner=request.user,
        status='PENDING'
    )

    return render(request, 'owner/bookings.html', {
        'bookings': bookings
    })

@login_required
def approve_booking(request, booking_id):
    if request.user.role != 'PG_OWNER':
        return redirect('dashboard')

    booking = Booking.objects.get(
        id=booking_id,
        room__pg__owner=request.user
    )

    if booking.room.available_rooms > 0:
        booking.status = 'APPROVED'
        booking.room.available_rooms -= 1
        booking.room.save()
        booking.save()

    return redirect('owner_bookings')


@login_required
def reject_booking(request, booking_id):
    if request.user.role != 'PG_OWNER':
        return redirect('dashboard')

    booking = Booking.objects.get(
        id=booking_id,
        room__pg__owner=request.user
    )

    booking.status = 'REJECTED'
    booking.save()

    return redirect('owner_bookings')



@login_required
def edit_pg(request, pg_id):
    if request.user.role != 'PG_OWNER':
        return redirect('dashboard')

    pg = PG.objects.get(id=pg_id, owner=request.user)

    if request.method == 'POST':
        form = PGForm(request.POST, request.FILES, instance=pg)
        if form.is_valid():
            form.save()
            return redirect('owner_pg_list')
    else:
        form = PGForm(instance=pg)

    return render(request, 'owner/edit_pg.html', {'form': form})


@login_required
def delete_pg(request, pg_id):
    if request.user.role != 'PG_OWNER':
        return redirect('dashboard')

    if request.method == 'POST':
        PG.objects.filter(id=pg_id, owner=request.user).delete()

    return redirect('owner_pg_list')

    #customer views

@login_required
def customer_pg_list(request):
    if request.user.role != 'CUSTOMER':
        return redirect('dashboard')

    pgs = PG.objects.filter(owner__is_approved=True)

    # 🔍 FILTERS
    location = request.GET.get('location')
    gender = request.GET.get('gender')
    max_price = request.GET.get('max_price')

    if location:
        pgs = pgs.filter(location__icontains=location)

    if gender:
        pgs = pgs.filter(gender_type=gender)

    if max_price:
        pgs = pgs.filter(price__lte=max_price)

    context = {
        'pgs': pgs,
        'location': location or '',
        'gender': gender or '',
        'max_price': max_price or '',
    }

    return render(request, 'customer/pg_list.html', context)


@login_required
def customer_pg_detail(request, pg_id):
    if request.user.role != 'CUSTOMER':
        return redirect('dashboard')

    pg = PG.objects.get(id=pg_id, owner__is_approved=True)

    return render(request, 'customer/pg_detail.html', {
        'pg': pg
    })

@login_required
def add_room(request, pg_id):
    if request.user.role != 'PG_OWNER':
        return redirect('dashboard')

    pg = PG.objects.get(id=pg_id, owner=request.user)
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.pg = pg
            room.save()
            return redirect('owner_pg_rooms', pg_id=pg.id)

    return render(request, 'owner/add_room.html', {
        'form': form,
        'pg': pg
    })

@login_required
def owner_pg_rooms(request, pg_id):
    if request.user.role != 'PG_OWNER':
        return redirect('dashboard')

    pg = PG.objects.get(id=pg_id, owner=request.user)
    rooms = pg.rooms.all()

    return render(request, 'owner/room_list.html', {
        'pg': pg,
        'rooms': rooms
    })

@login_required
def customer_pg_detail(request, pg_id):
    if request.user.role != 'CUSTOMER':
        return redirect('dashboard')

    pg = PG.objects.get(id=pg_id, owner__is_approved=True)
    rooms = pg.rooms.filter(available_rooms__gt=0)

    return render(request, 'customer/pg_detail.html', {
        'pg': pg,
        'rooms': rooms
    })

@login_required
def book_room(request, room_id):
    if request.user.role != 'CUSTOMER':
        return redirect('dashboard')

    room = Room.objects.get(id=room_id)

    if room.available_rooms <= 0:
        messages.error(request, "Room not available")
        return redirect('customer_pg_detail', pg_id=room.pg.id)

    form = BookingForm()

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.room = room
            booking.save()

            messages.success(request, "Booking request sent")
            return redirect('customer_bookings')

    return render(request, 'customer/book_room.html', {
        'form': form,
        'room': room
    })

@login_required
def customer_bookings(request):
    if request.user.role != 'CUSTOMER':
        return redirect('dashboard')

    bookings = Booking.objects.filter(customer=request.user).select_related(
        'room', 'room__pg'
    ).order_by('-created_at')

    return render(request, 'customer/bookings.html', {
        'bookings': bookings
    })

@login_required
def cancel_booking(request, booking_id):
    if request.user.role != 'CUSTOMER':
        return redirect('dashboard')

    booking = Booking.objects.get(id=booking_id, customer=request.user)

    # Only allow cancel if not rejected
    if booking.status in ['PENDING', 'APPROVED']:
        # If approved, restore room availability
        if booking.status == 'APPROVED':
            room = booking.room
            room.available_rooms += 1
            room.save()

        booking.status = 'REJECTED'
        booking.save()

    return redirect('customer_bookings')

@login_required
def delete_room(request, room_id):
    if request.user.role != 'PG_OWNER':
        return redirect('dashboard')

    room = Room.objects.get(
        id=room_id,
        pg__owner=request.user
    )

    # ❌ Prevent delete if bookings exist
    if room.bookings.exists():
        # optional: add message later
        return redirect('owner_pg_rooms', pg_id=room.pg.id)

    room.delete()
    return redirect('owner_pg_rooms', pg_id=room.pg.id)

@login_required
def edit_room(request, room_id):
    if request.user.role != 'PG_OWNER':
        return redirect('dashboard')

    room = Room.objects.get(
        id=room_id,
        pg__owner=request.user
    )

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('owner_pg_rooms', pg_id=room.pg.id)
    else:
        form = RoomForm(instance=room)

    return render(request, 'owner/edit_room.html', {
        'form': form,
        'room': room
    })

@login_required
def admin_users(request):
    if request.user.role != 'ADMIN':
        return redirect('dashboard')

    role = request.GET.get('role')

    users = User.objects.all()

    if role:
        users = users.filter(role=role)

    return render(request, 'admin/users.html', {
        'users': users,
        'role': role or ''
    })

@login_required
def admin_bookings(request):
    if request.user.role != 'ADMIN':
        return redirect('dashboard')

    status = request.GET.get('status')

    bookings = Booking.objects.select_related(
        'room', 'room__pg', 'customer'
    )

    if status:
        bookings = bookings.filter(status=status)

    return render(request, 'admin/bookings.html', {
        'bookings': bookings,
        'status': status or ''
    })



@login_required
def owner_booking_history(request):
    if request.user.role != 'PG_OWNER':
        return redirect('dashboard')

    bookings = Booking.objects.filter(
        room__pg__owner=request.user
    ).select_related('room', 'room__pg', 'customer')

    # income = sum of approved bookings
    income = bookings.filter(status='APPROVED').aggregate(
        total=Sum('room__price')
    )['total'] or 0

    return render(request, 'owner/booking_history.html', {
        'bookings': bookings,
        'income': income
    })


@login_required
def admin_delete_user(request, user_id):
    if request.user.role != 'ADMIN':
        return redirect('dashboard')

    user = User.objects.get(id=user_id)

    # ❌ Do not allow deleting admins
    if user.role == 'ADMIN':
        return redirect('admin_users')

    # ❌ Do not allow deleting yourself
    if user == request.user:
        return redirect('admin_users')

    user.delete()
    return redirect('admin_users')

@login_required
def owner_customers(request):
    if request.user.role != 'PG_OWNER':
        return redirect('dashboard')

    bookings = Booking.objects.filter(
        room__pg__owner=request.user
    ).select_related('customer', 'room', 'room__pg')

    return render(request, 'owner/customers.html', {
        'bookings': bookings
    })

@login_required
def owner_remove_customer(request, booking_id):
    if request.user.role != 'PG_OWNER':
        return redirect('dashboard')

    booking = Booking.objects.get(
        id=booking_id,
        room__pg__owner=request.user
    )

    # restore room availability if approved
    if booking.status == 'APPROVED':
        room = booking.room
        room.available_rooms += 1
        room.save()

    booking.delete()
    return redirect('owner_customers')



@login_required
def logout_view(request):
    logout(request)
    return redirect('index')
