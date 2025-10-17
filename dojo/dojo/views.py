from django.shortcuts import render
from django.templatetags.static import static

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
    galery_images = [static('img/galery/' + f.name) for f in galery_path.iterdir() if f.suffix.lower() in ('.png', '.jpg', '.jpeg')]

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
