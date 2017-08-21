from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from database_setup import Base, Brewery, Beer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///localbreweries.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/delete"):
                breweryIDPath = self.path.split("/")[2]
                myBreweryQuery = session.query(Brewery).filter_by(id = breweryIDPath).one()
                if myBreweryQuery != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>Are you sure you want to delete %s" % myBreweryQuery.name
                    output += "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/breweries/%s/delete'>" % breweryIDPath
                    output += "<input type='submit' value='Delete'></form>"
                    output += "</body></html>"
                    self.wfile.write(output)
                    return

            if self.path.endswith("/edit"):
                breweryIDPath = self.path.split("/")[2]
                myBreweryQuery = session.query(Brewery).filter_by(id = breweryIDPath).one()
                if myBreweryQuery != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>"
                    output += myBreweryQuery.name
                    output += "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/breweries/%s/edit'>" % breweryIDPath
                    output += "<input name='newBreweryName' type='text' placeholder='%s'>" % myBreweryQuery.name
                    output += "<input type='submit' value='Rename'></form>"
                    output += "</body></html>"
                    self.wfile.write(output)
                    return

            if self.path.endswith("/breweries/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Brewery</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='/breweries/new'><input name='newBreweryName' type='text' placeholder='New Brewery Name'><input type='submit' value='Create'></form>"
                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/breweries"):
                breweries = session.query(Brewery).all()
                output = ""
                output += "<html><body>"
                output += "<a href='/breweries/new'>Make a New Brewery Here</a></br></br>"
                for brewery in breweries:
                    output += "<a href='/brewery/%s/beers'>" % brewery_id
                    output += brewery.name
                    output
                    output += "</br>"
                    output += "<a href='/breweries/%s/edit'>Edit </a>" % brewery.id
                    output += "</br>"
                    output += "<a href='/breweries/%s/delete'>Delete </a>" % brewery.id
                    output += "</br></br></br>"
                output += "</body></html>"
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(output)
                return

        except:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/delete"):
                    breweryIDPath = self.path.split("/")[2]

                    myBreweryQuery = session.query(Brewery).filter_by(id = breweryIDPath).one()
                    if myBreweryQuery:
                        session.delete(myBreweryQuery)
                        session.commit()

                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/breweries')
                        self.end_headers()

                        return

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newBreweryName')
                    breweryIDPath = self.path.split("/")[2]

                    myBreweryQuery = session.query(Brewery).filter_by(id = breweryIDPath).one()
                    if myBreweryQuery != []:
                        myBreweryQuery.name = messagecontent[0]
                        session.add(myBreweryQuery)
                        session.commit()

                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/breweries')
                        self.end_headers()

                        return

            if self.path.endswith("/breweries/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newBreweryName')

                newBrewery = Brewery(name = messagecontent[0])
                session.add(newBrewery)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/breweries')
                self.end_headers()

                return

        except:
            pass

def main():
    try:
        port = 8080
        server = HTTPServer(('',port), webserverHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()

if __name__ == '__main__':
    main()
