import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pycaw.pycaw import AudioUtilities
import webbrowser
from random import choice
import os
import tkinter as tk
import time

# TODO tkinter

canvas_width = 750
ads = 0

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "2"
import pygame

joke = ["not", "got", "lot", "hot", "caught", "shot", "bought", "plot", "Scott", "pot", "forgot", "dot", "knot", "slot",
        "rot", "watt", "yacht", "clot", "cot", "blot", "tot", "wat", "squat", "trot", "astronaut", "swat", "alot",
        "bot", "scot", "mot", "jot", "allot"]
haha = choice(joke)

# - - - - - - - - - - - - - - - - - - - - - SETUP PYGAME - - - - - - - - - - - - - - - - - - - - -
pygame.mixer.init()
radio = os.listdir("./Music")
waitSong = choice(radio)
pygame.mixer.music.load("./Music./" + waitSong)

# - - - - - - - - - - - - - - - - - - - - - SETUP TKINTER - - - - - - - - - - - - - - - - - - - - -
master = tk.Tk()
master.title(haha.capitalize() + "ify")
w = tk.Canvas(master, width=canvas_width, height=40)
information = tk.Label(master, text="Logging In")
information.place(x=0, y=0)
average = tk.Label(master, text="")
average.place(x=0, y=20)
w.pack()

# - - - - - - - - - - - - - - - - - - - - - SETUP SPOTIPY - - - - - - - - - - - - - - - - - - - - -
os.environ["SPOTIPY_CLIENT_ID"] = "ID"
os.environ["SPOTIPY_CLIENT_SECRET"] = "SECRET"
os.environ["SPOTIPY_REDIRECT_URI"] = "http://google.com/"

client_id = os.environ.get("SPOTIPY_CLIENT_ID")
client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.environ.get("SPOTIPY_REDIRECT_URI")
scope = "user-read-playback-state,user-modify-playback-state"

f = open("Logged.txt", 'r')
username = f.read()
f.close()

# - - - - - - - - - - - - - - - - - - - - - SETUP MISC - - - - - - - - - - - - - - - - - - - - -
currentlyPlaying = ""
artist = ""
advertising = False
refreshRate = 100
valid = False


# Find and authenticate user in spotify to get data.
def authenticate():
    auth = SpotifyOAuth(client_id=client_id,
                        client_secret=client_secret,
                        redirect_uri=redirect_uri,
                        scope=scope,
                        username=username)

    return spotipy.Spotify(auth_manager=auth)


sp = authenticate()

# Attempt to log in user, checks if valid name. Saves username in Logged, and uses that next log in attempt.
while not valid:
    if username == "":
        username = input("Enter Spotify Username:\t")
    else:
        sp = authenticate()
        check = input("Login as " + sp.current_user()['display_name'] + "? (y/n) \t")
        if check.lower() == "y":
            valid = True
        if check.lower() == "n":
            username = input("Enter Spotify Username:\t")

    sp = authenticate()
    #     oauth_object = spotipy.SpotifyOAuth(client_id, client_secret, redirect_uri)
    #     user_name = sp.current_user()
    try:
        oauth_object = spotipy.SpotifyOAuth(client_id, client_secret, redirect_uri)
        valid = True
    except spotipy.oauth2.SpotifyOauthError:
        print("Please enter the correct url or a valid username.")
        username = ""
    except Exception as a:
        print(a)

# # To print the response in readable format.
# print(json.dumps(user_name, sort_keys=True, indent=4))

f = open("Logged.txt", "w")
f.write(username)
f.close()


def silence():
    global currentlyPlaying, artist, advertising, waitSong, sp, ads
    # w.config(width=randint(100, 500), height=randint(100, 500))
    try:
        trackInfo = sp.current_user_playing_track()
    except Exception as e:
        print(e)
        print("Token Expired")
        sp = authenticate()
        trackInfo = sp.current_user_playing_track()
    try:
        if trackInfo['currently_playing_type'] == 'ad' and not advertising:
            sessions = AudioUtilities.GetAllSessions()
            for s in sessions:
                if s.Process and s.Process.name() == "Spotify.exe":
                    s.SimpleAudioVolume.SetMute(1, None)
            pygame.mixer.music.play()
            advertising = True

        elif trackInfo['currently_playing_type'] != 'ad':
            sessions = AudioUtilities.GetAllSessions()
            for s in sessions:
                if s.Process and s.Process.name() == "Spotify.exe":
                    s.SimpleAudioVolume.SetMute(0, None)
            pygame.mixer.music.fadeout(500)
            waitSong = choice(radio)
            pygame.mixer.music.load("./Music./" + waitSong)
            advertising = False

        if (trackInfo['currently_playing_type'] != 'ad' and
                currentlyPlaying != sp.current_user_playing_track()['item']['name']):

            currentlyPlaying = sp.current_user_playing_track()['item']['name']
            artist = sp.current_user_playing_track()['item']['album']['artists'][0]['name']
            print("Now Playing:\t" + currentlyPlaying + " by " + artist)
            information.configure(text="Now Playing:\t" + currentlyPlaying + " by " + artist)
        elif (trackInfo['currently_playing_type'] == 'ad' and
              currentlyPlaying != trackInfo['currently_playing_type']):
            currentlyPlaying = "ad"
            artist = "Corp"
            print("AD AHH")
            information.configure(text="Ad Blocking in Progress")
            passedTime = (time.time() - start)
            ads += 1
            average.configure(text=str(ads) + " Blocked ad breaks in " + str(round(passedTime / 60)) + " Minutes")

        volume = sp.devices()['devices'][0]['volume_percent']
        pygame.mixer.music.set_volume(volume / 100)

    except Exception as e:
        print(e)
        pass

    master.after(refreshRate, silence)

while True:
    print("Welcome to " + haha.capitalize() + "ify, " + sp.current_user()['display_name'] + "!")
    print("0 - Exit the console")
    print("1 - Search for a Song")
    print("2 - Start muting ads")
    user_input = input("Enter Your Choice: ")
    if user_input == "2":
        print("Starting...")
        start = time.time()
        master.after(refreshRate, silence)
        break

    elif user_input == "1":
        search_song = input("Enter the song name: ")
        results = sp.search(search_song, 1, 0, "track")
        songs_dict = results['tracks']
        song_items = songs_dict['items']
        song = song_items[0]['external_urls']['spotify']
        webbrowser.open(song)
        print('Song has opened in your browser.')
    elif user_input == "0":
        print("Good Bye, Have a great day!")
        break
    else:
        print("Please enter valid user-input.")

master.mainloop()
