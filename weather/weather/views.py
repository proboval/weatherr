from django.shortcuts import render
import requests as req
from django.contrib import messages
import json


def index(request):
    if request.method == 'POST':
        city = request.POST.get('city')
        if city != '':
            try:
                url = (f'http://api.openweathermap.org/data/2.5/weather?q={city}'
                       f'&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347')
                print(url)
                weather_data = req.get(url).json()
                print(weather_data)

                icon = weather_data['weather'][0]['icon']
                temperature = round(weather_data['main']['temp'])
                temperature_feels = round(weather_data['main']['feels_like'])
                min_temp = round(weather_data['main']['temp_min'])
                max_temp = round(weather_data['main']['temp_max'])

                search_history = json.loads(request.COOKIES.get('search_history', '{}'))
                print(search_history)
                cnt = search_history.get(city, 0)
                cnt += 1
                search_history[city] = cnt
                print(search_history)
                sort_history = sorted(search_history.items(), key=lambda item: item[1], reverse=True)

                context = {'icon': icon, 'temperature': temperature, 'temperature_feels': temperature_feels,
                           'min_temp': min_temp, 'max_temp': max_temp, 'city': city, 'search_history': sort_history}

                response = render(request, 'weather/index.html', context)
                response.set_cookie('search_history', json.dumps(search_history))

                return response
            except Exception as e:
                print(e)
                messages.error(request, f'Города {city} не существует, введите информацию заново')

    search_history = json.loads(request.COOKIES.get('search_history', '{}'))
    sort_history = sorted(search_history.items(), key=lambda item: item[1], reverse=True)
    context = {'search_history': sort_history}

    return render(request, 'weather/index.html', context=context)
