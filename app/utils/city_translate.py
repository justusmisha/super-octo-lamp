import pandas as pd

def city_refractor(russian_city: str):
    try:
        cities_data = pd.read_csv('./app/database/data/cities.csv', header=None, names=['Russian', 'English'])
        city_translation_map = dict(zip(cities_data['Russian'], cities_data['English']))
                selected_city_english = city_translation_map[russian_city].replace(" ", "_").capitalize()
        return selected_city_english
    except KeyError:
        raise KeyError(f"City '{russian_city}' is not in the translation map. Please add it to the CSV.")
    except FileNotFoundError:
        raise FileNotFoundError("The file './app/database/data/cities.csv' was not found.")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")
