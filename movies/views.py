from django.shortcuts import render
from django.core.paginator import Paginator

from .models import Movies, MovieGenres
import load_env
from bot.utils.send_movie import send_movie_task_async
import json


def movies_list(request):
    # Get filter parameters
    search_title = request.GET.get('search', '')
    genre = request.GET.get('genre', '')
    min_rating = request.GET.get('rating', 0)
    
    # Base queryset
    movies = Movies.objects.all().order_by("-rating")
    
    # Apply filters
    if search_title:
        movies = movies.filter(title__icontains=search_title).order_by("-rating")
    if genre:
        movies = movies.filter(genres__title=genre).order_by("-rating")
    if min_rating:
        movies = movies.filter(rating__gte=float(min_rating)).order_by("rating")
    
    # Pagination
    paginator = Paginator(movies, 14)  # 10 movies per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get all unique genres for the filter dropdown
    all_genres = MovieGenres.objects.all().values_list("title", flat=True)
    
    context = {
        'page_obj': page_obj,
        'all_genres': all_genres,
        'search_title': search_title,
        'selected_genre': genre,
        'min_rating': min_rating or 4.0,
    }

    return render(request, 'movies-list.html', context)



def movie_detail(request, slug):
    movie = Movies.objects.get(slug=slug)
    related_movies = (
        Movies.objects.filter(genres__in=movie.genres.all())
        .exclude(id=movie.id)
        .distinct()
        .order_by('-rating')[:10]
    )
    link = f"https://t.me/{load_env.BOT}?startapp={movie.slug}"
    share_link = f"https://t.me/share/url?url={link}&text=Check out this movie!"
    context = {
        "movie":movie,
        "related_movies":related_movies,
        "share_link":share_link,
        "copy_link":link
    }
    return render(request, 'movie-detail.html', context=context)

# views.py
import requests
from django.http import JsonResponse
from django.conf import settings
import hashlib
import hmac
from urllib.parse import parse_qsl
from django.views.decorators.csrf import csrf_exempt


def verify_telegram_web_app_data(init_data):
    from urllib.parse import parse_qsl
    import hmac, hashlib
    parsed_data = dict(parse_qsl(init_data))
    received_hash = parsed_data.pop('hash', None)

    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(parsed_data.items())])
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=load_env.TOKEN.encode(),
        digestmod=hashlib.sha256
    ).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    return hmac.compare_digest(calculated_hash, received_hash)

@csrf_exempt
def check_subscription(request):
    """Check if user is subscribed to the channel"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    data = json.loads(request.body)
    user_id = data.get('userId')
    init_data = data.get('initData')
    
    # Verify the request is from Telegram (optional but recommended)
    # if not verify_telegram_web_app_data(init_data):
    #     return JsonResponse({'error': 'Invalid request'}, status=403)
    
    if not user_id:
        return JsonResponse({'error': 'User ID required'}, status=400)
    
    if not verify_telegram_web_app_data(init_data):
        return JsonResponse({'error': 'Invalid request'}, status=403)
    
    try:
        # Check channel membership
        bot_token = load_env.TOKEN
        channel_id = "@english_kinolar_y"
        
        response = requests.get(
            f'https://api.telegram.org/bot{bot_token}/getChatMember',
            params={
                'chat_id': channel_id,
                'user_id': user_id
            },
            timeout=5
        )
        
        result = response.json()
        
        if result.get('ok'):
            print("Subscription checked - status ok")
            status = result['result']['status']
            is_subscribed = status in ['creator', 'administrator', 'member']
            return JsonResponse({'isSubscribed': is_subscribed})
        else:
            print("Subscription checked - status error")
            return JsonResponse({'error': 'Failed to check subscription'}, status=500)
            
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def send_movie(request):
    if request.method != "POST":
        return JsonResponse({'status': 'error'}, status=400)
    
    data = json.loads(request.body)
    user_id = data.get("user_id")
    movie_id = data.get("movie_id")

    if not (user_id and movie_id):
        return JsonResponse({'status': 'error'})
    
    try:
        movie_obj = Movies.objects.get(id=int(movie_id))
    except Movies.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Movie not found'}, status=404)
    
    movie_link = movie_obj.telegram_link
    message_id = int(movie_link.rstrip("/").split("/")[-1])
    # Queue async task
    send_movie_task_async.delay(message_id, int(user_id))

    
    return JsonResponse({"status":"ok"})