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
    breweries = session.query(Brewery).all()
    return render_template('breweries.html', breweries=breweries)

@app.route('/breweries/new', methods=['GET', 'POST'])
def newBrewery():
    if request.method == 'POST':
        brewery = Brewery(name = request.form['name'])
        session.add(brewery)
        session.commit()
        flash("New Brewery Created")
        return redirect(url_for('breweries'))
    else:
        return render_template('newbrewery.html')

@app.route('/breweries/<int:brewery_id>/')
def breweryBeers(brewery_id):
    brewery = session.query(Brewery).filter_by(id = brewery_id).one()
    items = session.query(Beer).filter_by(brewery_id = brewery.id)
    return render_template('beers.html', brewery=brewery, beers=items)

@app.route('/breweries/<int:brewery_id>/new/', methods = ['GET', 'POST'])
def newBeer(brewery_id):
    if request.method == 'POST':
        newItem = Beer(name = request.form['name'],
                    style = request.form['style'],
                    availibility = request.form['availibility'],
                    description = request.form['description'],
                    abv = request.form['abv'],
                    ibu = request.form['ibu'],
                    ingredients = request.form['ingredients'],
                    image_link = request.form['link'],
                    brewery_id = brewery_id)
        session.add(newItem)
        session.commit()
        flash("new beer created!")
        return redirect(url_for('breweryBeers', brewery_id = brewery_id))
    else:
        return render_template('newbeer.html', brewery_id = brewery_id)

@app.route('/breweries/<int:brewery_id>/<int:beer_id>/edit/', methods = ['GET', 'POST'])
def editBeer(brewery_id, beer_id):
    editedItem = session.query(Beer).filter_by(id = beer_id).one()
    if request.method == 'POST':
        editedItem.name = request.form['name']
        editedItem.style = request.form['style']
        editedItem.availibility = request.form['availibility']
        editedItem.description = request.form['description']
        editedItem.abv = request.form['abv']
        editedItem.ibu = request.form['ibu']
        editedItem.ingredients = request.form['ingredients']
        editedItem.image_link = request.form['image_link']
        session.add(editedItem)
        session.commit()
        flash("Beer edited!")
        return redirect(url_for('breweryBeers', brewery_id = brewery_id))
    else:
        return render_template('editbeer.html', brewery_id = brewery_id, beer_id = beer_id, i = editedItem)

@app.route('/breweries/<int:brewery_id>/<int:beer_id>/delete', methods = ['GET', 'POST'])
def deleteBeer(brewery_id, beer_id):
    deletedItem = session.query(Beer).filter_by(id = beer_id).one()
    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        flash("Beer deleted!")
        return redirect(url_for('breweryBeers', brewery_id = brewery_id))
    else:
        return render_template('deletebeer.html', brewery_id = brewery_id, i = deletedItem)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
