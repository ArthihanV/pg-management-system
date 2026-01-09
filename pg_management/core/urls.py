from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),

    path('signup/<str:role>/', views.signup_view, name='signup'),
    path('login/<str:role>/', views.login_view, name='login'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),

    path('panel/users/', views.admin_users, name='admin_users'),
    path('panel/approve-owners/', views.admin_approve_pg_owners, name='approve_pg_owners'),
    path('panel/approve-owner/<int:user_id>/', views.approve_pg_owner, name='approve_pg_owner'),
    path('panel/reject-owner/<int:user_id>/', views.reject_pg_owner, name='reject_pg_owner'),
    path('bookings/', views.admin_bookings, name='admin_bookings'),    
    path('users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    



    path('owner/add-pg/', views.add_pg, name='add_pg'),
    path('owner/pgs/', views.owner_pg_list, name='owner_pg_list'),
    path('owner/edit-pg/<int:pg_id>/', views.edit_pg, name='edit_pg'),
    path('owner/delete-pg/<int:pg_id>/', views.delete_pg, name='delete_pg'),
    path('owner/bookings/', views.owner_bookings, name='owner_bookings'),
    path('owner/booking/approve/<int:booking_id>/', views.approve_booking, name='approve_booking'),
    path('owner/booking/reject/<int:booking_id>/', views.reject_booking, name='reject_booking'),
    path('owner/bookings/history/', views.owner_booking_history, name='owner_booking_history'),
    path('owner/customers/', views.owner_customers, name='owner_customers'),
    path('owner/customers/remove/<int:booking_id>/', views.owner_remove_customer, name='owner_remove_customer'),
   

    

    path('customer/pgs/', views.customer_pg_list, name='customer_pg_list'),
    path('customer/pg/<int:pg_id>/', views.customer_pg_detail, name='customer_pg_detail'),
    path('customer/pg/<int:pg_id>/', views.customer_pg_detail, name='customer_pg_detail'),
    path('owner/pg/<int:pg_id>/rooms/', views.owner_pg_rooms, name='owner_pg_rooms'),
    path('owner/pg/<int:pg_id>/add-room/', views.add_room, name='add_room'),
    path('customer/book-room/<int:room_id>/', views.book_room, name='book_room'),
    path('customer/bookings/', views.customer_bookings, name='customer_bookings'),
    path('owner/room/delete/<int:room_id>/',views.delete_room,name='delete_room'),
    path('owner/room/edit/<int:room_id>/',views.edit_room,name='edit_room'),
    
     
    path('customer/booking/cancel/<int:booking_id>/',views.cancel_booking,name='cancel_booking'),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)