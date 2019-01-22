from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
CLIENT_ID = json.loads(
                open('client_secret.json', 'r').read()
            )['web']['client_id']
# APPLICATION_NAME = "Item Catalog"
# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
categories = session.query(Category).all()
# 1


@app.route('/')
def displayMain():
    return redirect(url_for('displayCatalog'))
# 2


@app.route('/catalog')
def displayCatalog():
    # display recent 10 items
    items = session.query(Item).order_by(
                                    Item.created_date.desc()
                                ).limit(10).all()

    return render_template(
                'index.html',
                recentItems=items
            )
# 3
# JSON
# All categories with its items (JSON format)


@app.route('/catalog/JSON')
def catalogJSON():
    data = {}
    data['categories'] = [i.serialize for i in categories]
    for category in data['categories']:
        items = session.query(Item).filter_by(category_id=category['id'])
        category['items'] = [i.serialize for i in items]
    return jsonify(data)
# Specific Category with its item (JSON format)


@app.route('/catalog/<string:category_name>/JSON')
def categoryJSON(category_name):
    try:
        category = session.query(Category).filter_by(name=category_name).one()
    except NoResultFound:
        flash('Category NOT Found!', 'error')
        return redirect(url_for('displayCatalog'))


@app.route('/catalog/<string:category>/<int:item_id>/JSON')
def itemJSON(category, item_id):
    try:
        item = session.query(Item).filter_by(id=item_id).one()
    except NoResultFound:
        flash('Item NOT Found!', 'error')
        return redirect(url_for('displayCatalog'))

    data = item.serialize
    return jsonify(data)
# JSON ends
# 4
# Authentication


@app.route('/login')
def Login():
    if isLogged():
        flash('You are Logged in already!', 'error')
        return redirect(url_for('displayCatalog'))

    state = ''.join(random.choice(string.ascii_uppercase + string.
                    digits) for x in xrange(32))

    login_session['state'] = state
    return render_template("login.html", STATE=state)
# bla bla bla


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if isLogged():
        flash('You are Logged in already!', 'error')
        return redirect(url_for('displayCatalog'))
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
                        json.dumps(
                            'Failed to upgrade the authorization code.',
                            401,
                        )
                    )
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?'
    url += 'token_type=Bearer&expires_in=604800&access_token=%s' % access_token

    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                json.dumps('Current user is already connected.'), 200
            )
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # User
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo?alt=json"
    userinfo_url += "&access_token=%s" % credentials.access_token
    answer = requests.get(userinfo_url)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(data['email'])
    if not user_id:
        createUser()
    login_session['user_id'] = user_id

    output = '<div class="d-flex mb-3 align-items-center">'
    output += '<h5 class="p-2 display-5">Welcome, '
    output += login_session['username']
    output += ' &hearts;!</h5>'
    output += '<img class="ml-auto p-2" src="'
    output += login_session['picture']
    output += '" style = "width: 100px; height: 100px;border-radius: 150px;" '
    output += 'alt"profile image" '
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    output += '</div>'
    flash("you are now logged in as %s" % login_session['username'], "success")
    return output
# bla bla bla


@app.route('/gdisconnect', methods=['POST'])
def gdisconnect():
    if not isLogged():
        return makeLogin()

    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
                        json.dumps('Current user not connected.'),
                        401
                    )
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke'
    url += '?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # delete user
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']

        flash('Successfully logged out!', 'success')
        return redirect(url_for('displayCatalog'))
    else:
        flash('Could not logout, please try again later.', 'error')
        return redirect(url_for('displayCatalog'))
# Authentication ends
# 5


@app.route('/catalog/<string:category_name>')
def displayCategory(category_name):
    try:
        category = session.query(Category).filter_by(name=category_name).one()
    except NoResultFound:
        flash('Category NOT Found!', 'error')
        return redirect(url_for('displayCatalog'))

    items = session.query(Item).filter_by(category_id=category.id).all()

    return render_template(
            'displayCategories.html',
            items=items,
            category_name=category_name,
        )
    items = session.query(Item).filter_by(category_id=category.id)
    data = {}
    data['category'] = category.serialize
    data['category']['items'] = [i.serialize for i in items]
    return jsonify(data)
# 6
# [ CRUD ]
# [ Create ] New Item


@app.route('/catalog/new', methods=["GET", "POST"])
def newItem():
    if not isLogged():
        return makeLogin()

    if request.method == "POST":
        newItem = Item(
            name=request.form['name'],
            description=request.form['description'],
            category_id=request.form['category'],
            user_id=login_session['user_id']
        )
        session.add(newItem)
        session.commit()

        flash("Item Successfully added.", "success")
        return redirect(url_for("displayCatalog"))

    return render_template('new.html')
# [ Read ] Display Item


@app.route('/catalog/<string:category>/<int:item_id>')
def displayItem(category, item_id):
    try:
        item = session.query(Item).filter_by(id=item_id).one()
    except NoResultFound:
        flash('Item NOT Found!', 'error')
        return redirect(url_for('displayCatalog'))

    return render_template('show.html', item=item)
# [ Update ] Edit Item


@app.route('/catalog/<string:category>/<int:item_id>/edit', methods=[
    "GET", "POST"])
def editItem(category, item_id):
    if not isLogged():
        return makeLogin()

    try:
        item = session.query(Item).filter_by(id=item_id).one()
    except NoResultFound:
        flash('Item NOT Found!.', 'error')
        return redirect(url_for('displayCatalog'))

    if not isCreator(item.user_id):
        return notAuthorized()

    if request.method == "POST":
        if (request.form['name']
                and request.form['description']
                and request.form['category']):

            item.name = request.form['name']
            item.description = request.form['description']
            item.category_id = request.form['category']

            flash("Item Successfully Edited.", 'success')
            return redirect(url_for(
                    "displayItem",
                    category=item.category.name,
                    item_id=item.id
                )
            )
        else:
            flash("""Item information NOT correct!,
            please fill the form Again!""", """error""")
            return redirect(
                        url_for(
                            'editItem',
                            category=category,
                            item_id=item_id
                        )
                    )

    return render_template('edit.html', item=item)
# [ Delete ] Delete Item


@app.route('/catalog/<string:category>/<int:item_id>/delete', methods=[
    "GET", "POST"])
def deleteItem(category, item_id):
    if not isLogged():
        return makeLogin()

    try:
        item = session.query(Item).filter_by(id=item_id).one()
    except NoResultFound:
        flash('Item NOT Found!.', 'error')
        return redirect(url_for('displayCatalog'))

    if not isCreator(item.user_id):
        return notAuthorized()

    if request.method == "POST":
        session.delete(item)
        session.commit()
        flash("Item Successfully Deleted.", "success")
        return redirect(url_for("displayCatalog"))

    return render_template('delete.html', item=item)
# 7
# Helper Functions


def isLogged():
    return 'username' in login_session


def makeLogin():
    flash('You have to login', 'error')
    return redirect(url_for('Login'))


def createUser():
    newUser = User(
                name=login_session['username'],
                email=login_session['email'],
                picture=login_session['picture'],
            )
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()

    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except NoResultFound:
        return None


def isCreator(creator_id):
    return creator_id == login_session['user_id']


def notAuthorized():
    flash('You are NOT Authorized for this', 'error')
    return redirect(url_for('displayCatalog'))
# Helper Functions ends here
# 8


@app.context_processor
def context_processor():
    username = None
    if 'username' in login_session:
        username = login_session['username']

    return dict(
        categories=categories,
        isLogged=isLogged,
        isCreator=isCreator,
        username=username
    )


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
