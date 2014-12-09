import xbmcaddon
import os
import xbmc
from Utils import *
import urllib
from urllib2 import Request, urlopen


moviedb_key = '34142515d9d23817496eeb4ff1d223d0'
__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__language__ = __addon__.getLocalizedString
Addon_Data_Path = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % __addonid__).decode("utf-8"))
base_url = ""
poster_size = ""
fanart_size = ""


def RateMovie(movieid, rating):
    if __addon__.getSetting("tmdb_username"):
        session_id_string = "session_id=" + get_session_id()
    else:
        session_id_string = "guest_session_id=" + get_guest_session_id()
    values = '{"value": %.1f}' % rating
    # values = '{"value": 5.5}'
    log(values)
    headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
    url = "http://api.themoviedb.org/3/movie/%s/rating?api_key=%s&%s" % (str(movieid), moviedb_key, session_id_string)
    request = Request(url, data=values, headers=headers)
    response = urlopen(request).read()
    results = simplejson.loads(response)
    # prettyprint(results)
    Notify("ExtendedInfo Script", results["status_message"])

def AddItemToFavourites(media_id=None, media_type="movie"):
      session_id = get_session_id()
      account_id = get_account_info()
      values = '{"media_type": "%s", "media_id": %s, "favorite": true}' % (media_type, str(media_id))
      # values = '{"value": 5.5}'
      log(values)
      headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
      url = "http://api.themoviedb.org/3/account/%s/favorite?session_id=%s&api_key=%s" % (str(account_id), str(session_id), moviedb_key)
      log(url)
      request = Request(url, data=values, headers=headers)
      response = urlopen(request).read()
      results = simplejson.loads(response)
      # prettyprint(results)
      Notify("ExtendedInfo Script", results["status_message"])

def CreateList():
    session_id = get_session_id()
    name = "Test"
    desctiption = ""
    values = '{"name": "%s", "description": "%s"}' % (name, description)
    log(values)
    headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
    url = "http://api.themoviedb.org/3/list?api_key=%s&session_id=%s" % (moviedb_key, session_id)
    request = Request(url, data=values, headers=headers)
    response = urlopen(request).read()
    results = simplejson.loads(response)
    # prettyprint(results)
    Notify("ExtendedInfo Script", results["status_message"])


def get_account_info():
    session_id = get_session_id()
    response = GetMovieDBData("account?session_id=%s&" % session_id, 999999)
    # prettyprint(response)
    return response["id"]

def get_guest_session_id():
    response = GetMovieDBData("authentication/guest_session/new?", 999999)
    # prettyprint(response)
    return response["guest_session_id"]

def get_session_id():
    request_token = auth_request_token()
    response = GetMovieDBData("authentication/session/new?request_token=%s&" % request_token, 0.1)
    # prettyprint(response)
    return response["session_id"]

def get_request_token():
    response = GetMovieDBData("authentication/token/new?", 0.1)
    # prettyprint(response)
    return response["request_token"]

def auth_request_token():
    request_token = get_request_token()
    username = __addon__.getSetting("tmdb_username")
    password = __addon__.getSetting("tmdb_password")
    response = GetMovieDBData("authentication/token/validate_with_login?request_token=%s&username=%s&password=%s&" % (request_token, username, password), 0.1)
    # prettyprint(response)
    if response["success"]:
      return response["request_token"]
    else:
      return "bla"




def HandleTMDBMovieResult(results):
    movies = []
    ids = []
    log("starting HandleTMDBMovieResult")
    for movie in results:
        tmdb_id = str(fetch(movie, 'id'))
        if ("backdrop_path" in movie) and (movie["backdrop_path"]):
            backdrop_path = base_url + fanart_size + movie['backdrop_path']
        else:
            backdrop_path = ""
        if ("poster_path" in movie) and (movie["poster_path"]):
            poster_path = base_url + poster_size + movie['poster_path']
            small_poster_path = base_url + "w342" + movie["poster_path"]
        else:
            poster_path = ""
            small_poster_path = ""
        release_date = fetch(movie, 'release_date')
        if release_date:
            year = release_date[:4]
        else:
            year = ""
        trailer = "plugin://script.extendedinfo/?info=playtrailer&&id=" + tmdb_id
        if False:
            path = 'plugin://script.extendedinfo/?info=extendedinfo&&id=%s' % tmdb_id
        else:
            path = trailer
        newmovie = {'Art(fanart)': backdrop_path,
                    'Art(poster)': small_poster_path,
                    'Thumb': small_poster_path,
                    'Poster': small_poster_path,
                    'fanart': backdrop_path,
                    'Title': fetch(movie, 'title'),
                    'Label': fetch(movie, 'title'),
                    'OriginalTitle': fetch(movie, 'original_title'),
                    'ID': tmdb_id,
                    'Path': path,
                    'Trailer': trailer,
                    'trailerimage': "http://i.ytimg.com/vi/" + tmdb_id + "/0.jpg",
                    'Play': "",
                    'DBID': "",
                    'Rating': fetch(movie, 'vote_average'),
                    'Votes': fetch(movie, 'vote_count'),
                    'User_Rating': fetch(movie, 'rating'),
                    'Year': year,
                    'Premiered': release_date}
        if not tmdb_id in ids:
            ids.append(tmdb_id)
            movies.append(newmovie)
    movies = CompareWithLibrary(movies)
    return movies


def HandleTMDBTVShowResult(results):
    tvshows = []
    ids = []
    log("starting HandleTMDBTVShowResult")
    for tv in results:
        tmdb_id = fetch(tv, 'id')
        if ("backdrop_path" in tv) and (tv["backdrop_path"]):
            backdrop_path = base_url + fanart_size + tv['backdrop_path']
        else:
            backdrop_path = ""
        if ("poster_path" in tv) and (tv["poster_path"]):
            poster_path = base_url + poster_size + tv['poster_path']
        else:
            poster_path = ""
        if "episode_run_time" in tv:
            runtimes = []
            for item in tv["episode_run_time"]:
                runtimes.append(str(item))
            duration = " / ".join(runtimes)
        else:
            duration = ""
        release_date = fetch(tv, 'first_air_date')
        if release_date:
            year = release_date[:4]
        else:
            year = ""
        newtv = {'Art(fanart)': backdrop_path,
                 'Art(poster)': poster_path,
                 'Thumb': poster_path,
                 'Poster': poster_path,
                 'fanart': backdrop_path,
                 'Title': fetch(tv, 'name'),
                 'OriginalTitle': fetch(tv, 'original_name'),
                 'Duration': duration,
                 'ID': tmdb_id,
                 'credit_id': fetch(tv, 'credit_id'),
                 'Path': "",
                 'Plot': fetch(tv, "overview"),
                 'Play': "",
                 'DBID': "",
                 'year': year,
                 'Rating': fetch(tv, 'vote_average'),
                 'Votes': fetch(tv, 'vote_count'),
                 'Release_Date': release_date,
                 'Premiered': release_date}
        if not tmdb_id in ids:
            ids.append(tmdb_id)
            tvshows.append(newtv)
    tvshows = CompareWithLibrary(tvshows)
    return tvshows


def HandleTMDBMiscResult(results):
    listitems = []
    for item in results:
        if ("poster_path" in item) and (item["poster_path"]):
            poster_path = base_url + poster_size + item['poster_path']
            small_poster_path = base_url + "w342" + item["poster_path"]
        else:
            poster_path = ""
            small_poster_path = ""
        listitem = {'Art(poster)': poster_path,
                   'Poster': poster_path,
                   'Thumb': small_poster_path,
                   'Title': fetch(item, 'name'),
                   'certification': fetch(item, 'certification'),
                   'release_date': fetch(item, 'release_date'),
                   'iso_3166_1': fetch(item, 'iso_3166_1'),
                   'author': fetch(item, 'author'),
                   'content': fetch(item, 'content'),
                   'ID': fetch(item, 'id'),
                   'url': fetch(item, 'url'),
                   'Description': fetch(item, 'description')}
        listitems.append(listitem)
    return listitems

def HandleTMDBVideoResult(results):
    listitems = []
    for item in results:
        image = "http://i.ytimg.com/vi/" + fetch(item, 'key') + "/0.jpg"
        listitem = {'Thumb': image,
                    'Title': fetch(item, 'name'),
                    'iso_639_1': fetch(item, 'iso_639_1'),
                    'type': fetch(item, 'type'),
                    'key': fetch(item, 'key'),
                    'site': fetch(item, 'site'),
                    'ID': fetch(item, 'id'),
                    'size': fetch(item, 'size')}
        listitems.append(listitem)
    return listitems

def HandleTMDBPeopleResult(results):
    people = []
    for person in results:
        description = "[B]Known for[/B]:[CR][CR]"
        if "known_for" in results:
            for movie in results["known_for"]:
                description = description + movie["title"] + " (%s)" % (movie["release_date"]) + "[CR]"
        builtin = 'RunScript(script.extendedinfo,info=extendedactorinfo,id=%s)' % str(person['id'])
        if "profile_path" in person and person["profile_path"]:
            image = base_url + poster_size + person["profile_path"]
            image_small = base_url + "w342" + person["profile_path"]
        else:
            image = ""
            image_small = ""
        alsoknownas = " / ".join(fetch(person, 'also_known_as'))
        newperson = {'adult': str(fetch(person, 'adult')),
                     'name': person['name'] ,
                     'title': person['name'],
                     'also_known_as': alsoknownas,
                     'alsoknownas': alsoknownas,
                     'biography': cleanText(fetch(person, 'biography')),
                     'birthday': fetch(person, 'birthday'),
                     'age': calculate_age(fetch(person, 'birthday')),
                     'character': fetch(person, 'character'),
                     'department': fetch(person, 'department'),
                     'job': fetch(person, 'job'),
                     'description': description,
                     'plot': description,
                     'id': str(person['id']),
                     'cast_id': str(fetch(person, 'cast_id')),
                     'credit_id': str(fetch(person, 'credit_id')),
                     'path': "plugin://script.extendedinfo/?info=action&&id=" + builtin,
                     'deathday': fetch(person, 'deathday'),
                     'place_of_birth': fetch(person, 'place_of_birth'),
                     'placeofbirth': fetch(person, 'place_of_birth'),
                     'homepage': fetch(person, 'homepage'),
                     'thumb': image_small,
                     'icon': image_small,
                     'poster': image}
        people.append(newperson)
    return people

def HandleTMDBPeopleImagesResult(results):
    images = []
    for item in results:
        image = {'aspectratio': item['aspect_ratio'],
                 'thumb': base_url + "w342" + item['file_path'],
                 'vote_average': fetch(item, "vote_average"),
                 'iso_639_1': fetch(item, "iso_639_1"),
                 'poster': base_url + poster_size + item['file_path']}
        images.append(image)
    return images

def HandleTMDBPeopleTaggedImagesResult(results):
    images = []
    if "tagged_images" in results:
        for item in results["tagged_images"]["results"]:
            image = {'aspectratio': item['aspect_ratio'],
                     'thumb': base_url + "w342" + item['file_path'],
                     'vote_average': fetch(item, "vote_average"),
                     'iso_639_1': fetch(item, "iso_639_1"),
                     'poster': base_url + poster_size + item['file_path']}
            images.append(image)
        return images
    else:
        return []



def HandleTMDBCompanyResult(results):
    companies = []
    log("starting HandleLastFMCompanyResult")
    for company in results:
        newcompany = {'parent_company': company['parent_company'],
                      'name': company['name'],
                      'description': company['description'],
                      'headquarters': company['headquarters'],
                      'homepage': company['homepage'],
                      'id': company['id'],
                      'logo_path': company['logo_path']}
        companies.append(newcompany)
    return companies


def SearchforCompany(Company):
  #  Companies = Company.split(" / ")
   # Company = Companies[0]
    import re
    regex = re.compile('\(.+?\)')
    Company = regex.sub('', Company)
    log(Company)
    response = GetMovieDBData("search/company?query=%s&" % urllib.quote_plus(Company), 30)
    try:
        return response["results"][0]["id"]
    except:
        log("could not find Company ID")
        return ""


def GetPersonID(person):
    persons = person.split(" / ")
    # if len(persons) > 1:
    #     personlist = []
    #     for item in persons:
    #         personlist.append(item["name"])
    #     dialog = xbmcgui.Dialog()
    #     selection = dialog.select("Select Actor", personlist)
    # else:
    person = persons[0]
    response = GetMovieDBData("search/person?query=%s&include_adult=true&" % urllib.quote_plus(person), 30)
    try:
        return response["results"][0]["id"]
    except:
        log("could not find Person ID")
        return ""


def SearchForSet(setname):
    setname = setname.replace("[", "").replace("]", "").replace("Kollektion", "Collection")
    response = GetMovieDBData("search/collection?query=%s&language=%s&" % (urllib.quote_plus(setname.encode("utf-8")), __addon__.getSetting("LanguageID")), 14)
    try:
        return response["results"][0]["id"]
    except:
        return ""


def GetMovieDBData(url="", cache_days=14):
    url = "http://api.themoviedb.org/3/%sapi_key=%s" % (url, moviedb_key)
    global base_url
    global poster_size
    global fanart_size
    if not base_url:
        log("fetching base_url and size (MovieDB config)")
        base_url = True
        base_url, poster_size, fanart_size = GetMovieDBConfig()
    results = Get_JSON_response(url, cache_days)
    return results


def GetMovieDBConfig():
    return ("http://image.tmdb.org/t/p/", "w780", "w1280")
    response = GetMovieDBData("configuration?", 60)
    log("MovieDBConfig:")
  #  prettyprint(response)
    if response:
        return (response["images"]["base_url"], response["images"]["poster_sizes"][-2], response["images"]["backdrop_sizes"][-2])
    else:
        return ("", "", "")


def GetCompanyInfo(Id):
    response = GetMovieDBData("company/%s/movies?append_to_response=movies&" % (Id), 30)
    if response and "results" in response:
        return HandleTMDBMovieResult(response["results"])
    else:
        return []


def millify(n):
    import math
    millnames = ['', 'Thousand', 'Million', 'Billion', 'Trillion']
    # millnames = ['', 'k', 'm', 'b', 't']
    millidx = max(0, min(len(millnames) - 1, int(math.floor(math.log10(abs(n)) / 3.0))))
    return '%.0f %s' % (n / 10 ** (3 * millidx), millnames[millidx])


def GetSeasonInfo(tvshowname, seasonnumber):
    response = GetMovieDBData("search/tv?query=%s&language=%s&" % (urllib.quote_plus(tvshowname), __addon__.getSetting("LanguageID")), 30)
    tvshowid = str(response['results'][0]['id'])
    response = GetMovieDBData("tv/%s/season/%s?append_to_response=videos,images,external_ids,credits&language=%s&" % (tvshowid, seasonnumber, __addon__.getSetting("LanguageID")), 30)
    season = {'SeasonDescription': response["overview"],
              'AirDate': response["air_date"]}
    videos = []
    for item in response["videos"]["results"]:
        video = {'key': item["key"],
                 'name': item["name"],
                 'type': item["type"]}
        videos.append(video)
    return season, videos


def GetMovieDBID(imdbid):
    response = GetMovieDBData("find/tt%s?external_source=imdb_id&language=%s&" % (imdbid, __addon__.getSetting("LanguageID")), 30)
    return response["movie_results"][0]["id"]


def GetTrailer(movieid=None):
    response = GetMovieDBData("movie/%s?append_to_response=alternative_titles,credits,images,keywords,releases,videos,translations,similar,reviews,lists,rating&language=%s&" % (movieid, __addon__.getSetting("LanguageID")), 30)
    if not response:
        Notify("Could not get trailer")
        return ""
    if "videos" in results and len(response['videos']['results']) > 0:
        Trailer = response['videos']['results'][0]['key']
        return 'plugin://script.extendedinfo/?info=youtubevideo&&id=%s' % Trailer
    else:
        Trailer = ""
        Notify("Could not get trailer for movie with id " + str(movieid))


def GetExtendedMovieInfo(movieid=None, dbid=None):
    response = GetMovieDBData("movie/%s?append_to_response=alternative_titles,credits,images,keywords,releases,videos,translations,similar,reviews,lists,rating&language=%s&" % (movieid, __addon__.getSetting("LanguageID")), 30)
    authors = []
    directors = []
    genres = []
    prettyprint(response)
    if not response:
        Notify("Could not get movie information")
        return {}, [], [], [], [], [], [], [], [], []
    for item in response['genres']:
        genres.append(item["name"])
    for item in response['credits']['crew']:
        if item["job"] == "Author":
            authors.append(item["name"])
        if item["job"] == "Director":
            directors.append(item["name"])
    Trailer = ""
    trailerimage = ""
    if "videos" in response:
      for item in response['videos']['results']:
          if item["type"] == "Trailer" and item["site"] == "YouTube":
              Trailer = item["key"]
              trailerimage = "http://i.ytimg.com/vi/" + Trailer + "/0.jpg"
              break
    if len(response['releases']['countries']) > 0:
        mpaa = response['releases']['countries'][0]['certification']
    else:
        mpaa = ""
    if len(response['production_countries']) > 0:
        Country = response['production_countries'][0]["name"]
    else:
        Country = ""
    Studio = []
    for item in response['production_companies']:
        Studio.append(item["name"])
    Studio = " / ".join(Studio)
    Set = fetch(response, "belongs_to_collection")
    if Set:
        SetName = fetch(Set, "name")
        SetID = fetch(Set, "id")
    else:
        SetName = ""
        SetID = ""
    if 'release_date' in response and fetch(response, 'release_date') is not None:
        year = fetch(response, 'release_date')[:4]
    else:
        year = ""
    BudgetValue = fetch(response, 'budget')
    if not BudgetValue in [0, 1, ""]:
        Budget = millify(float(BudgetValue))
    else:
        Budget = ""
    RevenueValue = fetch(response, 'revenue')
    if not RevenueValue in [0, 1, ""]:
        Revenue = millify(float(RevenueValue))
    else:
        Revenue = ""
    if ("backdrop_path" in response) and (response["backdrop_path"]):
        backdrop_path = base_url + fanart_size + response['backdrop_path']
    else:
        backdrop_path = ""
    if ("poster_path" in response) and (response["poster_path"]):
        poster_path = base_url + poster_size + response['poster_path']
        poster_path_small = base_url + "w342" + response['poster_path']
    else:
        poster_path = ""
        poster_path_small = ""
    path = 'plugin://script.extendedinfo/?info=youtubevideo&&id=%s' % str(fetch(response, "id"))
    movie = {'Art(fanart)': backdrop_path,
             'Art(poster)': poster_path,
             'Thumb': poster_path_small,
             'Poster': poster_path,
             'fanart': backdrop_path,
             'Title': fetch(response, 'title'),
             'Label': fetch(response, 'title'),
             'Tagline': fetch(response, 'tagline'),
             'Duration': fetch(response, 'runtime'),
             'mpaa': mpaa,
             'Director': " / ".join(directors),
             'Writer': " / ".join(authors),
             'Budget': Budget,
             'Revenue': Revenue,
             'Homepage': fetch(response, 'homepage'),
             'Set': SetName,
             'SetId': SetID,
             'ID': fetch(response, 'id'),
             'Plot': fetch(response, 'overview'),
             'OriginalTitle': fetch(response, 'original_title'),
             'Genre': " / ".join(genres),
             'Rating': fetch(response, 'vote_average'),
             'Votes': fetch(response, 'vote_count'),
             'Popularity': fetch(response, 'popularity'),
             'Status': fetch(response, 'status'),
             'Play': '',
             'Trailer': 'plugin://script.extendedinfo/?info=youtubevideo&&id=%s' % Trailer,
             'trailerimage': trailerimage,
             'Path': path,
             'ReleaseDate': fetch(response, 'release_date'),
             'Premiered': fetch(response, 'release_date'),
             'Country': Country,
             'Studio': Studio,
             'DiscArt': "",
             'VideoResolution': "",
             'AudioChannels': "",
             'VideoCodec': "",
             'VideoAspect': "",
             'Logo': "",
             'DBID': "",
             'FilenameAndPath': "",
             'Banner': "",
             'DiscArt': "",
             'Logo': "",
             'Studio': Studio,
             'Year': year}
    movie = CompareWithLibrary([movie])[0]
   # prettyprint(response)
    actors = HandleTMDBPeopleResult(response["credits"]["cast"])
    crew = HandleTMDBPeopleResult(response["credits"]["crew"])
    similar_movies = HandleTMDBMovieResult(response["similar"]["results"])
    lists = HandleTMDBMiscResult(response["lists"]["results"])
    reviews = HandleTMDBMiscResult(response["reviews"]["results"])
    genres = HandleTMDBMiscResult(response["genres"])
    production_companies = HandleTMDBMiscResult(response["production_companies"])
    releases = HandleTMDBMiscResult(response["releases"]["countries"])
    keywords = HandleTMDBMiscResult(response["keywords"]["keywords"])
    if "videos" in response:
        videos = HandleTMDBVideoResult(response["videos"]["results"])
    else:
        videos = []
    return movie, actors, similar_movies, lists, production_companies, releases, crew, genres, keywords, reviews, videos


def GetExtendedTVSHowInfo(tvshow_id):
    response = GetMovieDBData("tv/%s?append_to_response=content_ratings,credits,external_ids,images,keywords,rating,similar,translations,videos&language=%s&" % (str(tvshow_id), __addon__.getSetting("LanguageID")), 2)
    # prettyprint(response)
    tvshow = HandleTMDBTVShowResult([response])
    actors = HandleTMDBPeopleResult(response["credits"]["cast"])
    crew = HandleTMDBPeopleResult(response["credits"]["crew"])
    similar_shows = HandleTMDBMovieResult(response["similar"]["results"])
    genres = HandleTMDBMiscResult(response["genres"])
    production_companies = HandleTMDBMiscResult(response["production_companies"])
    # releases = HandleTMDBMiscResult(response["releases"]["countries"])
    keywords = HandleTMDBMiscResult(response["keywords"]["results"])
    keywords = HandleTMDBMiscResult(response["keywords"]["results"])
    return tvshow[0], actors, crew, similar_shows, genres, production_companies, keywords


def GetExtendedActorInfo(actorid):
    response = GetMovieDBData("person/%s?append_to_response=tv_credits,movie_credits,combined_credits,images,tagged_images&" % (actorid), 1)
    person = HandleTMDBPeopleResult([response])
    # prettyprint(response)
    images = HandleTMDBPeopleImagesResult(response["images"]["profiles"])
    if "tagged_images" in response:
        tagged_images = HandleTMDBPeopleImagesResult(response["tagged_images"]["results"])
    else:
        tagged_images = []
 #   prettyprint(response)
    movie_roles = HandleTMDBMovieResult(response["movie_credits"]["cast"])
    tvshow_roles = HandleTMDBTVShowResult(response["tv_credits"]["cast"])
    combined_roles = HandleTMDBMovieResult(response["combined_credits"]["cast"])
    return person[0], movie_roles, tvshow_roles, images, tagged_images


def GetMovieLists(Id):
    response = GetMovieDBData("movie/%s?append_to_response=alternative_titles,credits,images,keywords,releases,videos,translations,similar,reviews,lists,rating&language=%s&" % (Id, __addon__.getSetting("LanguageID")), 30)
    return HandleTMDBMiscResult(response["lists"]["results"])

def GetMoviesWithKeyword(keywordid):
    response = GetMovieDBData("discover/movie?sort_by=release_date.desc&vote_count.gte=10&with_keywords=%s&language=%s&" % (str(keywordid), __addon__.getSetting("LanguageID")), 30)
    return HandleTMDBMovieResult(response["results"])

def GetMoviesWithGenre(genreid):
    response = GetMovieDBData("discover/movie?sort_by=release_date.desc&vote_count.gte=10&with_genres=%s&language=%s&" % (str(genreid), __addon__.getSetting("LanguageID")), 30)
    return HandleTMDBMovieResult(response["results"])

def GetMoviesWithCertification(country, rating):
    response = GetMovieDBData("discover/movie?sort_by=release_date.desc&vote_count.gte=10&certification_country=%s&certification=%s&language=%s&" % (country, str(rating), __addon__.getSetting("LanguageID")), 30)
    return HandleTMDBMovieResult(response["results"])

def GetRatedMovies():
    if __addon__.getSetting("tmdb_username"):
        session_id = get_session_id()
        account_id = get_account_info()
        response = GetMovieDBData("account/%s/rated/movies?session_id=%s&language=%s&" % (str(account_id), str(session_id), __addon__.getSetting("LanguageID")), 0)
    else:
        session_id = get_guest_session_id()
        response = GetMovieDBData("guest_session/%s/rated_movies?language=%s&" % (str(session_id), __addon__.getSetting("LanguageID")), 0)
    return HandleTMDBMovieResult(response["results"])

def GetFavMovies():
    session_id = get_session_id()
    account_id = get_account_info()
    response = GetMovieDBData("account/%s/favorite/movies?session_id=%s&language=%s&" % (str(account_id), str(session_id), __addon__.getSetting("LanguageID")), 0)
    return HandleTMDBMovieResult(response["results"])


def GetMoviesFromList(listid):
    response = GetMovieDBData("list/%s?language=%s&" % (str(listid), __addon__.getSetting("LanguageID")), 30)
  #  prettyprint(response)
    return HandleTMDBMovieResult(response["items"])

def GetPopularActorList():
    response = GetMovieDBData("person/popular?", 1)
    return HandleTMDBPeopleResult(response["results"])


def GetActorMovieCredits(actorid):
    response = GetMovieDBData("person/%s/movie_credits?" % (actorid), 1)
    return HandleTMDBMovieResult(response["cast"])


def GetActorTVShowCredits(actorid):
    response = GetMovieDBData("person/%s/tv_credits?" % (actorid), 1)
    return HandleTMDBMovieResult(response["cast"])


def GetMovieKeywords(Id):
    response = GetMovieDBData("movie/%s?append_to_response=alternative_titles,credits,images,keywords,releases,videos,translations,similar,reviews,lists,rating&language=%s&" % (Id, __addon__.getSetting("LanguageID")), 30)
    keywords = []
    if "keywords" in response:
        for keyword in response["keywords"]["keywords"]:
            newkeyword = {'id': fetch(keyword, 'id'),
                          'name': keyword['name']}
            keywords.append(newkeyword)
        return keywords
    else:
        log("No Keywords in JSON answer")
        return []


def GetSimilarMovies(Id):
    response = GetMovieDBData("movie/%s?append_to_response=alternative_titles,credits,images,keywords,releases,videos,translations,similar,reviews,lists,rating&language=%s&" % (Id, __addon__.getSetting("LanguageID")), 30)
    if "similar_movies" in response:
        return HandleTMDBMovieResult(response["similar_movies"]["results"])
    else:
        log("No JSON Data available")


def GetMovieDBTVShows(tvshowtype):
    response = GetMovieDBData("tv/%s?language=%s&" % (tvshowtype, __addon__.getSetting("LanguageID")), 2)
    if "results" in response:
        return HandleTMDBTVShowResult(response["results"])
    else:
        log("No JSON Data available for GetMovieDBMovies(%s)" % tvshowtype)
        log(response)


def GetMovieDBMovies(movietype):
    response = GetMovieDBData("movie/%s?language=%s&" % (movietype, __addon__.getSetting("LanguageID")), 2)
    if "results" in response:
        return HandleTMDBMovieResult(response["results"])
    else:
        log("No JSON Data available for GetMovieDBMovies(%s)" % movietype)
        log(response)


def GetSetMovies(Id):
    response = GetMovieDBData("collection/%s?language=%s&" % (Id, __addon__.getSetting("LanguageID")), 14)
    if "parts" in response:
        return HandleTMDBMovieResult(response["parts"])
    else:
        log("No JSON Data available")


def GetDirectorMovies(Id):
    response = GetMovieDBData("person/%s/credits?language=%s&" % (Id, __addon__.getSetting("LanguageID")), 14)
    # return HandleTMDBMovieResult(response["crew"]) + HandleTMDBMovieResult(response["cast"])
    if "crew" in response:
        return HandleTMDBMovieResult(response["crew"])
    else:
        log("No JSON Data available")


def search_movie(medianame, year=''):
    log('TMDB API search criteria: Title[''%s''] | Year[''%s'']' % (medianame, year))
    medianame = urllib.quote_plus(medianame.encode('utf8', 'ignore'))
    response = GetMovieDBData("search/movie?query=%s+%s&language=%s&" % (medianame, year, __addon__.getSetting("LanguageID")), 1)
    tmdb_id = ''
    try:
        if response == "Empty":
            tmdb_id = ''
        else:
            for item in response['results']:
                if item['id']:
                    tmdb_id = item['id']
                    log(tmdb_id)
                    break
    except Exception as e:
        log(e)
    if tmdb_id == '':
        log('TMDB API search found no ID')
    else:
        log('TMDB API search found ID: %s' % tmdb_id)
    return tmdb_id
