# Reviaide
Software that allows one to generate QR through which people can interact with products or marketing material

User Stories:
- As a business/brand owner i want to be able to collect cuastomer's reviews and feedback
  - I would like to be able to login into the system
  - I would like to be able to add product into the system using special menu
  - I would like to be able to delete product that i have added to the system
  - I would like to be able to edit the product that i have added to the system
  - I would like to be able to access QR code related to my product to add such QR on my product or marketing material
  - I would like to be able to display all reviews or feedbacks and read them
  
- As a customer who looking for reviews about the item and way to communicate with brand i would like to access commenting system easily
  - I would like to be able to scan QR code using my camera and being redirected to a website
  - I would like to be able to read comments
  - I would like to be able to wtire a review and submit it
  - I would like to be able to write feedback and submit it

How to Build (Version of Python used: Version 3.8.2, on Unix based system (tested in Ubuntu):
* In order to avoid installing all required libraries and frameworks globally 
* navigate to directory where project folder is located
* setup virtual environment:
  - sudo apt-get install python3-venv
* create virtual under name venv environment using:
  - python3 -m venv venv 
* start virtual environment with:
  - source venv/bin/activate
* now we entered virtual environment, let's install all required dependencies:
[list of required dependencies: Flask, SQLAlchemy, Flask-login, qrcode]
  - pip install Flask
  - pip install SQLAlchemy
  - pip install flask-login
  - pip install qrcode
* let's run application now; while being in virtual environemnt, in project directory:
  - python3 app.py 
  - start web application using http://localhost:5000/

Architecture:
Patterns or frameworks:
  In this multiple frameworks were used. First and foremost the application build using Flaks, which is a python web microframework. This framowork alows to route and handle http requests. As microframework, flask do not have many utilities uch as login handling. Despite login handling can be implemented using flask "sesion" capabilities it was decided to use lask-login library, to simplify login handling. Secondly, while UI seems as standart
  http and javascript, in fact no javascript (and almost no css) were used. All the look of ui is due to bootstrap framework. It is a simple front-end ramework, allowing one use bootstrap snippets and elements. In such way the use of JS and CSS was almost eliminated
Important Aspects:
  Application consist of main application (app.py) which contains all the functional code, as well as html templates that are rendered by application. This appplication have all routing as well as helper methods, the most important part is routing, this is how application knows what to do when particular request is made. Another important aspect is template system. Each template in our system is rendered by application depending on request. In such way each user can see unique or relevant content depending on their request. All templates use jinja system, its a way to pass varibales from flask to html templates as well as create logical and loop expressions in html. It is important to note that jinja does not add programming features to html, it just gives flask an instructions on what to write in html on rendering stage. In our system there are couple other miscalleneus design decisions that we have to mention
    - There is minimal amount of css in static/css folder. Present lines just make minor changes to couple type of forms therefore it is barely couple lines
    - QR codes that are generated are stored in static/images. this QR code store link and product number. In such way each product nmber that have unique code will have unique QR as long as product exists in the system
How to Mofidy:
  There are multiple ways in which this system can be modified:
    - First and foremost, registration and login system can be designed for parties that are writing reviews. In such way we can ensure that reviews are real and are not just coming from the same person or fake person
    - Product owner should have option to delete the feedback and claim review as fraudulant (but can not delete, it is feature for further investigation on our side). In addition, profile page (main page of product owner after login) can have dashboard showing how many people interacted with his/her products and maybe some highlights about review
    - Security-wise, the form handling should be changed, as of now it is vaunorable to sql injection attaks. Moreover, login system have to be enchaced with secured session. Those changes are crucial, and it can not be called an application until those security concerns are resolved
    - Dtatabse model can be enchanced through adding intermediate level between product, comment and feedback, and QR code. For exmaple unique token is attached to product, then this token can be attached to many same products with different owners. But this is mpore advanced development for scaling system (as ofnow we assume each product have one owner only)

Tests:

TEST 01:
- 
