"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from accounts.views import Account
from api.views import Health


urlpatterns = [
    path('', Account.as_view(), name='index'),
    path('admin/', admin.site.urls),
    path('health/', Health.as_view(), name='health'),
    path('accounts/', include('accounts.urls'), name='accounts'),
    path('robots.txt', TemplateView.as_view(template_name='base/robots.txt', content_type='text/plain'), name='robots'),
    path('docs/', include('docs.urls')),
    path('api/', include('api.urls')),
    path('payments/', include('payments.urls')),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = 'base.views.page_not_found'
handler403 = 'base.views.page_forbidden'
