# Home Grown Brews

This is the code to generate a website dedicated to local breweries and beers.  It allows users to create, read, edit, and delete both breweries and beers from the database.  Initially the database is populated with a few breweries and beers local to Austin, TX but the website is intended to be updated by users to include more breweries and beers from many cities.

## Structure

The code is written in python using SQLAlchemy and Flask.  It includes a python file, **database_setup.py** to create an initial database for the website.  This is only necessary if you want to start from scratch.  An initial database is included in the code, **localbreweries.db**. The source code also included a python file, **project.py** that creates and runs the Flask webserver connected to the **localbreweries.db** database file. The source code also includes several template html files, css files, and javascript files.

**database_setup.py** creates the structure for the database including two objects, **Brewery** and **Beer**, along with the initial code to create the database using SQLAlchemy.
**project.py** contains multiple methods resposible for responding the server requests based on the url address and method sent.

## Todo
Add more styling to webpage.
Move website to AWS along with assign to domain name.
Add image functionality.

## Usage
#### Required software
* Download and install [VirtualBox](https://www.virtualbox.org/). This is free software that will run the virtual machine
* Download and install [Vagrant](https://www.vagrantup.com/). This is an command line utility that makes it easy to manage and access your virtual machines

#### Setting Up Environment
* Create a new folder on your computer named **vagrant** where you’ll store your work for this course, then open that folder within your terminal
* Type `vagrant init` to tell Vagrant what kind of Linux virtual machine you would like to run
* Type `vagrant up` to download and start running the virtual machine

#### Running **project.py**
* Within your terminal, type `vagrant ssh` from your folder created in the previous steps
* Navigate to the Local-Brews folder within your vagrant vm, ex. `cd /vagrant/Local-Brews`
* Type `python project.py` to run the webserver
* Go to an internet browser and navigate to localhost:5000
* Enjoy the website

## License

The content of this repository is licensed under a [MIT License](https://opensource.org/licenses/MIT)


