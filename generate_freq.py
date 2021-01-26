import spotipy.util as util
from progress.bar import Bar
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import json, requests, urllib.parse, re, time, sys, click, spotipy

def auth():
    username = 'default'
    scope = 'user-read-private user-read-playback-state user-modify-playback-state user-library-read'

    token = util.prompt_for_user_token(username,
                            scope,
                            client_id='', # CHANGE
                            client_secret='', # CHANGE
                            redirect_uri='http://localhost:8000/')

    if token:
        sp = spotipy.Spotify(auth=token)
        # print('Authenticated')
        return sp
    else:
        print("Failed to get token")
        exit()

def get_lyric(artist, name, idx):
    try:
        query = urllib.parse.quote_plus(artist + ' ' + name)
        # print(idx, query)
        url = "https://genius.com/api/search/multi?per_page=5&q=" + query

        response = requests.get(url)

        result = json.loads(response.text)

        try:
            for i in result['response']['sections']:
                if i['type'] == 'song':
                    lyric_url = i['hits'][0]['result']['url']
        except:
            return np.NaN

        lyric_response = requests.get(lyric_url)

        soup = BeautifulSoup(lyric_response.content, 'html.parser')

        lyric_divs = soup.find_all('div', class_='lyrics')

        lyrics = ''
        if lyric_divs:
            for i in lyric_divs:
                lyrics += i.text.replace('\n', ' ').replace('"', "' ")
        else:
            lyrics += soup.find('div', class_='Lyrics__Container-sc-1ynbvzw-2 jgQsqn').getText(separator=" ").replace('"', "' ")

        rules = [r'\[.*?\]', r'\(.*?\)', r'[?,.]']

        for rule in rules:
            lyrics = re.sub(rule, '', lyrics)

        # lyrics = re.sub(r'la.', '', lyrics)
        # lyrics = re.sub(r'[ \t]{2,}', '', lyrics)


        return lyrics
    except:
        return -1

def generate_lyrics(URI):
    sp = auth()
    df = pd.DataFrame(columns=['uri', 'name', 'artist', 'lyrics'])

    data = []

    try:
        results = sp.playlist_items(URI)
        for t in results['items']:
            data.append({'uri': t['track']['uri'], 'name': t['track']['name'], 'artist': t['track']['artists'][0]['name']})

    except spotipy.exceptions.SpotifyException:
        print('The URI does not exist')
        exit()

    while results['next']:
        results = sp.next(results)
        for t in results['items']:
            data.append({'uri': t['track']['uri'], 'name': t['track']['name'], 'artist': t['track']['artists'][0]['name']})

    df = df.append(data, ignore_index=True)

    bar = Bar('Getting Lyrics', max=len(df))

    for idx, row in df.iterrows():
        for attempt in range(10):
            lyrics = get_lyric(row['artist'], row['name'], idx)
            if lyrics != -1:
                row['lyrics'] = lyrics
                break
            else:
                print('sleeping', attempt)
                time.sleep(5)
        bar.next()

    bar.finish()

    print('Could not find lyrics for: {} songs'.format(df['lyrics'].isna().sum()))
    df = df.dropna()

    df.to_csv(URI[-22:] + '_lyrics.csv', index=False)
    print("Saved lyrics to file")


def create_database(URI):
    print("Gettng songs this may take a while...")
    generate_lyrics(URI)

def generate_freq(URI):
    df = pd.read_csv(URI[-22:] + '_lyrics.csv')
    all_words = []

    for i in df['lyrics'].values:
        all_words += str(i).lower().split()
    
    word_freq = WordCloud().process_text(' '.join(all_words))

    with open(URI[-22:] + '.txt', 'w') as f:
        json.dump(word_freq, f)
    
    print("Saved frequencies to " + URI[-22:] + '.txt')


def look_for_lyrics(URI):
    try:
        open(URI[-22:] + '_lyrics.csv')
        return -1
    except IOError:
        print("New Playlist...")
        return

def validate_uri(URI_maybe):
    URI = re.findall(r"spotify:playlist:[A-Za-z0-9]{22}", URI_maybe)
    if URI:
        return URI[0]
    else:
        print("Not a valid URI")
        exit()

def main():
    argv = sys.argv
    if len(argv) > 1:
        URI_maybe = argv[1]
        print('\n' + URI_maybe)
        URI = validate_uri(URI_maybe)
        response = look_for_lyrics(URI)
        if response == -1:
            if click.confirm("You have alread created a lyrics file, create another?", default=True):
                create_database(URI)
                generate_freq(URI)
            else:
                generate_freq(URI)
        else:
            print("Creating a new database...")
            create_database(URI)
            generate_freq(URI)
    else:
        print("Usage: python generat_freq.py <URI>")


if __name__ == "__main__":
    main()


# command = 'blender -b --python WordPile.py <URI>'