from django.shortcuts import render
from .forms import LoginForm, RegisterForm, NewMonumentForm, AddMonumentImgForm, SearchForm
from .models import users_collection, monuments_collection, cities_collection, contributions_collection
import bson
from datetime import datetime, timedelta


def login(request):
    error=''
    data = {}
    isLogged = False
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                data = users_collection.find_one({'email': email})
                if data.get('password') == password:
                    data['userId'] = str(data['_id'])
                    isLogged = True
                
                else:
                    form = LoginForm()
                    error = 'Wrong credientials. Please try again.'
                    
            except:
                form = LoginForm()
                error = 'User not found!! Please try again.'
        else:
            form = LoginForm()
            error = 'Wrong credientials. Please try again.'
    else:
        form = LoginForm()
    
    context = {'form': form, 'isLogged': isLogged, 'data': data, 'error': error}
    return render(request, 'login.html', context)



def register(request):
    error=''
    data = {}
    isLogged = False
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = {"username": username, "email": email, "password": password}
            result = users_collection.insert_one(user)
            isLogged = True
            data = {
            'userId': str(result.inserted_id),
            'username': username,
            'email': email,
            'password': password,
            }
            
        else:
            form = RegisterForm()
            error = 'Invalid form data. Please try again.'
    else:
        form = RegisterForm()
    
    context = {'form': form, 'isLogged': isLogged, 'data': data, 'error': error}
    return render(request, 'register.html', context)

def landing(request):
    allMonuments = [monument for monument in monuments_collection.find()]
    for m in allMonuments:
        m["id"] = str(m["_id"])

    monuments = []
    for i in range(len(allMonuments)):
        if(i < 4):
            monuments.append(allMonuments[i])
    
    return render(request, 'landing.html', {"monuments": monuments})

def loadAddLocation(request):
    return render(request, "loadAddLocation.html")

def addLocation(request, id):
    success = False
    error = ''
    if request.method == 'POST':
        form = NewMonumentForm(request.POST)
        objId = bson.ObjectId(id)
        user = users_collection.find_one({'_id': objId})

        if form.is_valid():

            contributorId = id
            contributor = user['username']
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            bannerImage = form.cleaned_data['bannerImg']
            city = form.cleaned_data['city']
            address = form.cleaned_data['address']
            otherThings = form.cleaned_data['otherThings']

            monument = {"contributorId":contributorId, "contributor":contributor, "title": title, "description": description, "bannerImage": bannerImage,
                        "city":city, "address":address, "otherThings":otherThings, "images": [] }
  
            result = monuments_collection.insert_one(monument)

            date = datetime.now()
            date = str(date.strftime('%d-%m-%y'))

            contribution = {
                'monumentId': str(result.inserted_id),
                'contributor': contributor,
                'contributorId': contributorId,
                'title': title,
                'city': city,
                'address': address,
                'contribution': "New monument added!",
                "date": date
            }

            res = contributions_collection.insert_one(contribution)

            success = True

        else:
            form = NewMonumentForm()    
            success = False
            error = 'Invalid form data. Please try again.'
    else:
        form = NewMonumentForm()
    
    context = {'form': form, 'success': success, 'error': error}
    return render(request, 'newLocation.html', context)


def search(request):
    form = SearchForm()
    monuments = []
    isResults = False
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            monuments = [monument for monument in monuments_collection.find({'$or': [{'city': search}, {'title': search}]})]
            for monument in monuments:
                monument['id'] = str(monument['_id'])

            isResults = True
            print(monuments)
    return render(request, 'search.html', {"monuments": monuments, "isResults": isResults, "form": form})

def loadContributions(request):
    return render(request, "loadContributions.html")

def contributions(request, id):
    objId = bson.ObjectId(id)
    user = users_collection.find_one({'_id': objId})

    contributions = [contribution for contribution in contributions_collection.find({'contributorId': id})]
    contributions.reverse()
    contriLen = len(contributions)
 
    return render(request, 'Contributions.html', {"contributions": contributions, "contriLen": contriLen, "username": user['username']})

def city(request, id):
    monuments = [monument for monument in monuments_collection.find({"city": id})]

    for m in monuments:
        m["id"] = str(m["_id"])

    return render(request, 'cityLocations.html', {"monuments": monuments, "city": id})

def loadLocation(request, id):
    return render(request, "loadLocation.html", {"id": id})

def location(request, locId, userId):

    success = False
    error = False
    locationId = bson.ObjectId(locId)
    monument = monuments_collection.find_one({"_id": locationId})

    monumentImgsLen = len(monument['images'])

    if request.method == 'POST':
        form = AddMonumentImgForm(request.POST)
        objId = bson.ObjectId(userId)
        user = users_collection.find_one({'_id': objId})
        print(monument)
        if form.is_valid():
            image = form.cleaned_data['image']

            images = monument['images']
            images.append(image)

            monuments_collection.update_one({'_id': locationId}, {"$set": {"images": images}})

            date = datetime.now()
            date = str(date.strftime('%d-%m-%y'))

            contribution = {
                'monumentId': locId,
                'contributor': user['username'],
                'contributorId': userId,
                'title': monument['title'],
                'city': monument['city'],
                'address': monument['address'],
                'contribution': "New Image added!",
                "date": date
            }

            print(contribution)
            res = contributions_collection.insert_one(contribution)

            success = True

        else:
            error = True
    else:
        form = AddMonumentImgForm()
        success = False

    context = {'form': form, 'success': success, "error": error, "monument": monument, "locId": locId, "monumentImgsLen": monumentImgsLen}

    return render(request, 'location.html', context)