from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from database_setup import Base, Brewery, Beer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///localbreweries.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/breweries/<int:brewery_id>/beers/JSON')
def breweryBeersJSON(brewery_id):
    brewery = session.query(Brewery).filter_by(id = brewery_id).one()
    items = session.query(Beer).filter_by(brewery_id = brewery_id).all()
    return jsonify(Beers=[i.serialize for i in items])

@app.route('/breweries/<int:brewery_id>/beers/<int:beer_id>/JSON')
def breweryBeerJSON(brewery_id, beer_id):
    item = session.query(Beer).filter_by(id = beer_id).one()
    return jsonify(Beer=item.serialize)

@app.route('/')
@app.route('/breweries')
def breweries():
    breweries = session.query(Brewery).order_by(Brewery.name).all()
    return render_template('breweries.html', breweries=breweries)

@app.route('/breweries/new', methods=['GET', 'POST'])
def newBrewery():
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

@app.route('/breweries/<int:brewery_id>/')
def brewery(brewery_id):
    brewery = session.query(Brewery).filter_by(id = brewery_id).one()
    beers = session.query(Beer).filter_by(brewery_id = brewery.id)
    return render_template('brewery.html', brewery=brewery, beers=beers)

@app.route('/breweries/<int:brewery_id>/edit/', methods = ['GET', 'POST'])
def editBrewery(brewery_id):
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

@app.route('/breweries/<int:brewery_id>/delete', methods = ['GET', 'POST'])
def deleteBrewery(brewery_id):
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

@app.route('/breweries/<int:brewery_id>/<int:beer_id>')
def beer(brewery_id, beer_id):
    brewery = session.query(Brewery).filter_by(id = brewery_id).one()
    beer = session.query(Beer).filter_by(id = beer_id).one()
    return render_template('beer.html', beer=beer, brewery=brewery)

@app.route('/breweries/<int:brewery_id>/new/', methods = ['GET', 'POST'])
def newBeer(brewery_id):
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

@app.route('/breweries/<int:brewery_id>/<int:beer_id>/edit/', methods = ['GET', 'POST'])
def editBeer(brewery_id, beer_id):
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
        return redirect(url_for('beer', brewery_id = brewery_id, beer_id = beer.id))
    else:
        return render_template('editbeer.html', brewery_id = brewery_id, beer = beer)

@app.route('/breweries/<int:brewery_id>/<int:beer_id>/delete', methods = ['GET', 'POST'])
def deleteBeer(brewery_id, beer_id):
    beer = session.query(Beer).filter_by(id = beer_id).one()
    if request.method == 'POST':
        session.delete(beer)
        session.commit()
        flash("Beer deleted!")
        return redirect(url_for('brewery', brewery_id = brewery_id))
    else:
        return render_template('deletebeer.html', brewery_id = brewery_id, beer = beer)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
