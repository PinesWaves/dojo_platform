from django.shortcuts import render
from django.templatetags.static import static
from django.utils import translation
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST

from pathlib import Path
from django.conf import settings


def rename_images_in_galery():
    galery_path = Path(settings.STATIC_ROOT) / 'img' / 'galery'
    images = [f for f in galery_path.iterdir() if f.suffix.lower() in ('.png', '.jpg', '.jpeg')]
    images.sort()
    for idx, file_path in enumerate(images, 1):
        new_name = f"{idx:02}{file_path.suffix}"
        file_path.rename(galery_path / new_name)


def landing_page(request):
    galery_path = Path(settings.STATIC_ROOT) / 'img' / 'galery'
    galery_images = [static('img/galery/' + f.name) for f in galery_path.iterdir() if f.suffix.lower() in ('.png', '.jpg', '.jpeg')][::-1]

    ctx = {
        'galery': galery_images,
            # 'https://dummyimage.com/600x400/000/fff',
            # 'https://dummyimage.com/600x400/111/fff',
            # 'https://dummyimage.com/600x400/222/fff',
            # 'https://dummyimage.com/600x400/333/fff',
            # 'https://dummyimage.com/600x400/444/fff',
            # 'https://dummyimage.com/600x400/555/fff',
            # 'https://dummyimage.com/600x400/666/fff',
    }
    return render(request, 'landing/landing.html', ctx)

def custom_404(request, exception):
    return render(request, "errors/404.html", status=404)

def custom_500(request):
    return render(request, "errors/500.html", status=500)


@require_POST
def set_language(request):
    """
    Set user's preferred language using Django's i18n framework.
    Activates the language and sets it in session and cookie.
    """
    lang_code = request.POST.get('language')
    if lang_code and lang_code in ['en', 'es', 'ja']:
        # Set language in session
        request.session['django_language'] = lang_code
        # Activate it immediately
        translation.activate(lang_code)
        # Create response with redirect
        response = HttpResponseRedirect(request.POST.get('next', '/'))
        # Set cookie on response
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            lang_code,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            samesite=settings.LANGUAGE_COOKIE_SAMESITE,
            httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
        )
        return response
    # If invalid language code, redirect to referer or home
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
