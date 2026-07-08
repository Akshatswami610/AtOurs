from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import login, register, home, hosting, eventdetails, bookingcheckout, payment, about, careers, terms, profile, privacy, support, team


urlpatterns = [
    path('admin/', admin.site.urls),

    # API Routes
    path('accounts/', include('accounts.urls')),
    path('bookings/',include('bookings.urls')),
    path('hosting/',include('hosting.urls')),
    path('support/',include('support.urls')),

    # Frontend pages
    path('', home, name='home'),
    path('home/', home, name='home'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('hosting/', hosting, name='hosting'),
    path('event-details/<int:id>/', eventdetails, name='eventdetails'),
    path('booking-checkout/', bookingcheckout, name='bookingcheckout'),
    path('booking-checkout/payment/', payment, name='payment'),
    path('profile/', profile, name='profile'),
    path('careers/', careers, name='careers'),
    path('privacy-policy/', privacy, name='privacy'),
    path('support/', support, name='support'),
    path('about/', about, name='about'),
    path('terms-and-conditions/', terms, name='terms'),
    path('privacy/', privacy, name='privacy'),
    path('team/', team, name='team'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)