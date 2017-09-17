from flask import Flask, render_template, request, redirect, \
    url_for, flash, jsonify
app = Flask(__name__)

from database_setup import Base, Brewery, Beer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Home Grown Brews"

engine = create_engine('postgresql://postgres@localhost:5432/brews')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    login_session['credentials'] = credentials.access_token
    access_token = login_session.get('credentials')
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

    # DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        flash("You have successfully logged out")
        return redirect(url_for('breweries'))
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# JSON method to return all brewery information
@app.route('/breweries/JSON')
def breweriesJSON():
    breweries = session.query(Brewery).order_by(Brewery.name).all()
    breweriesSerialized = []
    for brewery in breweries:
        breweriesSerialized.append(brewery.serialize)
    return jsonify(Breweries=breweriesSerialized)

# JSON methods to return information about a specific brewery
@app.route('/breweries/<int:brewery_id>/JSON')
def breweryJSON(brewery_id):
    brewery = session.query(Brewery).filter_by(id = brewery_id).one()
    return jsonify(Brewery=brewery.serialize)

# JSON method to return information about a specific beer
@app.route('/breweries/<int:brewery_id>/<int:beer_id>/JSON')
def beerJSON(brewery_id, beer_id):
    beer = session.query(Beer).filter_by(id = beer_id).one()
    return jsonify(Beer=beer.serialize)

# JSON method to return beer information for a specific brewery
@app.route('/breweries/<int:brewery_id>/beers/JSON')
def beersJSON(brewery_id):
    beers = session.query(Beer).filter_by(brewery_id = brewery_id).all()
    beersSerialized = []
    for beer in beers:
        beersSerialized.append(beer.serialize)
    return jsonify(Beers=beersSerialized)

# Web method to get a list of all breweries
@app.route('/')
@app.route('/breweries')
def breweries():
    breweries = session.query(Brewery).order_by(Brewery.name).all()
    if 'username' not in login_session:
        logged_in = "false"
    else:
        logged_in = "true"
    return render_template('breweries.html', breweries=breweries, logged_in=logged_in)

# Web method to create a new brewery
@app.route('/breweries/new', methods=['GET', 'POST'])
def newBrewery():
    if 'username' not in login_session:
        return redirect('login')
    if request.method == 'POST':
        brewery = Brewery(name = request.form['name'],
            created_date = request.form['created_date'],
            city = request.form['city'],
            state = request.form['state'],
            website = request.form['website'],
            image_link = request.form['image_link'],
            description = request.form['description'])
        session.add(brewery)
        session.commit()
        flash("New Brewery Created")
        return redirect(url_for('breweries'))
    else:
        return render_template('newbrewery.html')

# Web method to return information on a brewery
@app.route('/breweries/<int:brewery_id>/')
def brewery(brewery_id):
    brewery = session.query(Brewery).filter_by(id = brewery_id).one()
    beers = session.query(Beer).filter_by(brewery_id = brewery.id)
    return render_template('brewery.html', brewery=brewery, beers=beers)

# Web method to edit a brewery
@app.route('/breweries/<int:brewery_id>/edit/', methods = ['GET', 'POST'])
def editBrewery(brewery_id):
    if 'username' not in login_session:
        return redirect('login')
    brewery = session.query(Brewery).filter_by(id = brewery_id).one()
    if request.method == 'POST':
        brewery.name = request.form['name']
        brewery.created_date = request.form['created_date']
        brewery.website = request.form['website']
        brewery.city = request.form['city']
        brewery.state = request.form['state']
        brewery.image_link = request.form['image_link']
        brewery.description = request.form['description']
        session.add(brewery)
        session.commit()
        flash("Brewery edited!")
        return redirect(url_for('brewery', brewery_id = brewery.id))
    else:
        return render_template('editbrewery.html', brewery = brewery)

# Web method to delete a brewery
@app.route('/breweries/<int:brewery_id>/delete', methods = ['GET', 'POST'])
def deleteBrewery(brewery_id):
    if 'username' not in login_session:
        return redirect('login')
    brewery = session.query(Brewery).filter_by(id = brewery_id).one()
    beers = session.query(Beer).filter_by(brewery_id = brewery.id).all()
    if request.method == 'POST':
        for beer in beers:
            session.delete(beer)
        session.delete(brewery)
        session.commit()
        flash("Brewery deleted!")
        return redirect(url_for('breweries'))
    else:
        return render_template('deletebrewery.html', brewery = brewery)

# Web method to return information on a beer
@app.route('/breweries/<int:brewery_id>/<int:beer_id>')
def beer(brewery_id, beer_id):
    brewery = session.query(Brewery).filter_by(id = brewery_id).one()
    beer = session.query(Beer).filter_by(id = beer_id).one()
    return render_template('beer.html', beer=beer, brewery=brewery)

# Web method to create a new beer
@app.route('/breweries/<int:brewery_id>/new/', methods = ['GET', 'POST'])
def newBeer(brewery_id):
    if 'username' not in login_session:
        return redirect('login')
    if request.method == 'POST':
        newItem = Beer(name = request.form['name'],
                    style = request.form['style'],
                    description = request.form['description'],
                    abv = request.form['abv'],
                    ibu = request.form['ibu'],
                    ingredients = request.form['ingredients'],
                    image_link = request.form['link'],
                    brewery_id = brewery_id)
        session.add(newItem)
        session.commit()
        flash("new beer created!")
        return redirect(url_for('brewery', brewery_id = brewery_id))
    else:
        return render_template('newbeer.html', brewery_id = brewery_id)

# Web method to edit a beer
@app.route('/breweries/<int:brewery_id>/<int:beer_id>/edit/',
    methods = ['GET', 'POST'])
def editBeer(brewery_id, beer_id):
    if 'username' not in login_session:
        return redirect('login')
    beer = session.query(Beer).filter_by(id = beer_id).one()
    if request.method == 'POST':
        beer.name = request.form['name']
        beer.style = request.form['style']
        beer.description = request.form['description']
        beer.abv = request.form['abv']
        beer.ibu = request.form['ibu']
        beer.ingredients = request.form['ingredients']
        session.add(beer)
        session.commit()
        flash("Beer edited!")
        return redirect(url_for('beer', brewery_id = brewery_id,
            beer_id = beer.id))
    else:
        return render_template('editbeer.html', brewery_id = brewery_id,
            beer = beer)

# Web method to delete a beer
@app.route('/breweries/<int:brewery_id>/<int:beer_id>/delete',
    methods = ['GET', 'POST'])
def deleteBeer(brewery_id, beer_id):
    if 'username' not in login_session:
        return redirect('login')
    beer = session.query(Beer).filter_by(id = beer_id).one()
    if request.method == 'POST':
        session.delete(beer)
        session.commit()
        flash("Beer deleted!")
        return redirect(url_for('brewery', brewery_id = brewery_id))
    else:
        return render_template('deletebeer.html', brewery_id = brewery_id,
            beer = beer)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run()
