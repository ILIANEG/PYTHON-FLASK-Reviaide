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
* IMPORTANT: there is one manual configuration that has to be done
in order to fully test the system, namely, in app.py line 303 you need to 
substitute string '192.168.0.13' with your local public ipv4 (usually starts with 192.168..., for me it is 192.168.0.13, can be found using ipconfig in CMD or ). On stage of deployment this adress can be substituted with domain, but for now
it has to be hacked like that, i have not found any reliable way to adress it (most solutions work in particular OS, or with particular web configuration and so on)
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
    - More comprehensive registration system has to be developed. Right now it is merely exist for proof of concept and to add user to database

Tests:

TEST 01:
*start application and navigate to http://localhost:5000
- With empty user database (by default in github) try to login using 
  login: test
  password: test
* Expected result: redirected to login page with error message "login or password are not matching"

TEST 02:
- With empty user database (by default in github) navigate to Create Account link and put arbitrary login and password (in this case let's use login: test, password: test)
* Expected result: redirected to login page without any error messages

TEST 03:
- Login with wrong login and/or password while having at least one user in database (see TEST 02) (for example login: login, password: test)
* Expected result: redirected to login page with error message "login or password are not matching"

TEST 04: 
- Without being logged in into the system try to navigate to http://localhost:5000/profile
* Expected result: redirected to login page without any error message

TEST 05:
- Login into the system with valid credentials (if test cases followed, loggin: test password: test)
* expected result: redirected to profile page with "About this application, etc."

TEST 06:
- Logout of the system (presss square symbol and navigate to logout) and perform TEST 04
* same result expected

TEST 07:
- After logging back in and navigate to "Add Product". Add product under any name (under 100 symbols), any upc (under 12 digits) and any product description (under 1000 symbols)
* Expected result: product is added and user is automatically redirected back to adding product page (ready to add next product)

TEST 08:
- Add another product (Test 07) but this time put more then 100 characters name.
* Expected result: Characters beyond 100 are not being recorded

TEST 09:
- Add another product (Test 07) but this time put more then 1000 characters description.
* Expected result: Characters beyond 1000 are not being recorded

TEST 10:
- Add another product (Test 07) but this time put non-numeric UPC and press Add Item.
* Expected result: user is notified about numeric requirment for UPC field

TEST 11:
- Add another product (Test 07) but this time put UPC beyond 12 numbers.
* Expected result: user is notified about uper boundry for UPC entry

TEST 12:
- Add another product (Test 07) but this time leave name as a blank
* Expected result: Web browser is not accepting the form, informing user that product name is a required field

TEST 13:
- Add another product (Test 07) but this time leave Product UOC as a blank
* Expected result: same as Test 07 result

TEST 14:
- Add another product (Test 07) but this time leave description as a blank
* Expected result: Web browser is not accepting the form, informing user that product description is a required field

TEST 15:
- Navigate to "Manage Products". Beside one of the product click on "QR" link
* Expected result: new page with QR code picture was launched (you can return back by clicking on "Reviaide" logo)

TEST 16:
- Navigate to "Manage Products". Beside one of the product click on "Delete" link
* Expected result: Manage Product page should update and deleted product should disappear. If there was only one product in the system, table will be completely empty

TEST 17:
- While having at least one product in the system (Test 07) navigate to "Manage products" tab. Beside one of the product click on "Edit"
* Expected result: Redirected to a page similar to Add Product page, however all fields filled with current product information

TEST 18:
- Make sure that there is at least 1 product in the system. Navigate to manage product and press QR beside one of the products. Make sure that ip adress in your copy of software is presetted (see "How to build section", app.py line 303 that's where ip should be hardcoded). Take any mobile device (tested with android device), open camera point to the opened QR code and follow the link
* Expected result: Phone is redirected to page with buttons "Reviews" and "Feedback".

TEST 19:
- On mobile page (TEST 18) press REVIEWS, Press the button will redirect to the page (empty if no reviews currently present). Press Add Review, put Name, rating and review and Add Review
* Expected result: Redirected to Reviews page with new review added, and stars representing rating

Test 20.1:
- On mobile page (TEST 18) press "FEEDBACK". input all required information and press "SHARE"
* Expected result: redirected to main mobile page, feedback is recorded and can be accessed by peoduct owner

Test 20.2:
- After adding reviews on mobile device, navigate to Manage Products page and press "Reviews" link.
* Expected result: page with all reviews is opened

Test 20.3:
- After adding feedback on mobile device, navigate to Manage Products page and press "Feedback" link.
* Expected result: page with all feedback is opened with information about email and feedback content

***NOTE: Currently deletion is not working properly, i can not trouble shoot it right now, while i setted proper cascading, relationship database does not delete comments and feedback when product is deleted. It will be fixed later**