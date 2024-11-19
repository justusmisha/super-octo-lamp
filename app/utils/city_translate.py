import asyncio

import pandas as pd


def city_refractor(russian_city: str):
    cities_data = pd.read_csv('./app/database/data/cities.csv', header=None, names=['Russian', 'English'])
    city_translation_map = dict(zip(cities_data['Russian'], cities_data['English']))
    print(city_translation_map)
    selected_city_english = city_translation_map[russian_city].replace(" ", "_").capitalize()
    return selected_city_english
