from django.shortcuts import render
from django.templatetags.static import static

def landing_page(request):
    ctx = {
        'galery': [static(f'img/galery/{x:02}.png') for x in range(1, 16)],
            # 'https://dummyimage.com/600x400/000/fff',
            # 'https://dummyimage.com/600x400/111/fff',
            # 'https://dummyimage.com/600x400/222/fff',
            # 'https://dummyimage.com/600x400/333/fff',
            # 'https://dummyimage.com/600x400/444/fff',
            # 'https://dummyimage.com/600x400/555/fff',
            # 'https://dummyimage.com/600x400/666/fff',
    }
    return render(request, 'landing/landing.html', ctx)
