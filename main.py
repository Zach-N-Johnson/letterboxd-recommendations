from bs4 import BeautifulSoup
import urllib.request
import numpy as np
import re
import time
import os

clear = lambda: os.system('cls')


def main():
    clear()
    start = time.time()
    print("Enter your username:")

    # get url of user
    url = "https://letterboxd.com/" + input() + "/"

    try:
        user = urllib.request.urlopen(url)
    except:
        print("Username not found")
        return

    # enter number of fans to recommend against
    while(True):
        print("\nEnter the number of users to compare against")
        print("(higher number means better recommendations but longer time)")
        num = int(input())
        if num > 0:
            num = np.ceil(num/25)
            break
        else:
            print("Number must be greater than 0\n")

    clear()
    # get user page
    soup = BeautifulSoup(user, features="html.parser")
    text = soup.find("meta", property="og:description")
    film = soup.find_all("div", class_="film-poster")


    # get favorites of user
    favorites = []
    count = 0
    for i in film:
        if(count == 4): # gross but works
            break
        favorites.append(i["data-target-link"][6:])
        count += 1
    favorites = np.array(favorites)
    print("Favorites loaded")

    # find number of films watched with regex
    # probably a more efficient way to do this
    film_num = [int(s) for s in re.findall(r'-?\d+\.?\d*', text["content"])][0]
    
    # get number of films watched pages 
    pages = int(np.ceil(film_num/72))

    # get all films watched by user
    films_watched = np.array(get_films_watched(url, pages))
    print("\nFilms watched loaded")

    # get list of similar fans
    fans_list = []
    for i in range(0, 4):

        count = 0
        while(True):
            if(count == num):
                break
            fan = "https://letterboxd.com/film/" + favorites[i] + "fans/page/" + str(count)
            fans_url = urllib.request.urlopen(fan)
            fans_soup = BeautifulSoup(fans_url, features="html.parser")

            fans = fans_soup.find_all(class_="name")

            if not fans:
                break
            for j in fans:
                if j["href"] not in fans_list:
                    fans_list.append(j["href"])
            count += 1
    fans_list = np.array(fans_list)
    print("\nFans list loaded")

    rec_list = []
    rec_weights = []
    total = fans_list.size
    iteration = 1

    print("\nGetting Recommendations:\n")
    # get list of movies to recommend from fans of same movies
    for i in fans_list:
        fan_url = "https://letterboxd.com" + i
        fan_page_soup = BeautifulSoup(urllib.request.urlopen(fan_url), features="html.parser")
        fan_favs = fan_page_soup.find_all("div", class_="film-poster")
        count = 0
        for i in fan_favs:
            if(count == 4): # still gross but still works
                break
            
            # this is bad code
            movie_name = i["data-target-link"][6:]
            if movie_name not in films_watched and movie_name not in favorites and "film" not in movie_name:
                if movie_name not in rec_list:
                    rec_list.append(movie_name)
                    rec_weights.append(1)
                else:
                    rec_weights[rec_list.index(movie_name)] += 1
                count += 1
        printProgressBar(iteration=iteration, total=total)
        iteration += 1

    rec_weights, rec_list = zip(*sorted(zip(rec_weights, rec_list)))


    # print top 5
    clear()
    rec_length = len(rec_list)-1
    count = 1
    print("\n\nTop 5 Recomendations:\n")
    while(rec_length > len(rec_list) - 6):
        film_name = form(rec_list[rec_length])
        print(f"{count}. {film_name}, weight = {rec_weights[rec_length]}")
        rec_length -= 1
        count += 1
        

    print("\n")
    end = time.time()
    print(f"time taken: {end - start}")



def get_films_watched(url, pages):
    # add all films the user has seen to user_films
    films_watched = []
    for i in range(1, pages+1):
        all_films = urllib.request.urlopen(url + "films/page/" + str(i))
        page_soup = BeautifulSoup(all_films, features="html.parser")
        film = page_soup.find_all("div", class_="film-poster")
        for j in film:
            films_watched.append(j["data-target-link"][6:])
    return films_watched

# format film title
def form(film_link):
    url = "https://letterboxd.com/film/" + film_link
    soup = BeautifulSoup(urllib.request.urlopen(url), features="html.parser")
    film_name = soup.select("h1.headline-1")[0].text.strip()
    return film_name

# Print Command Line Progress Bar
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


main()