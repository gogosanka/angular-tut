from flask import render_template, flash, redirect, session, url_for, request, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from smh import app, db, lm, blogic
from smh.forms import LoginForm, NameForm, SignupForm
from smh.models.models import User, Post
from datetime import datetime
from smh.auth import *
import time
#application specific imports (non-boilerplate)
from smh.stopwords import stops
from collections import Counter
from bs4 import BeautifulSoup
import requests
import operator
import re
import nltk
from smh.models.models import Result

#boilerplate
@app.route('/admin', methods=['GET'])
def jeffadmin():
    return render_template('admindashboard.html')

#boilerplate
@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        try:
            user = current_user.nickname
        except:
            user = "Anonymous"
    errors = []
    results = {}
    if request.method == "POST":
        #grab the url that was entered on the form here
        try:
            url = request.form['url']
            r = requests.get(url)
            #make sure to use .encode("utf-8") on r.text otherwise the object won't actually print to the terminal
        except:
            errors.append("Unable to grab da URL doe. Make sure it's valid.")
            return render_template('smh/index.html',
                                title="Querying Application",
                                user=user,
                                results=results,
                                errors=errors)
        if r:
            # text processing
            r = r.text.encode('utf-8')
            raw = BeautifulSoup(r).get_text()
            nltk.data.path.append('smh/nltk_data/')  # set the path
            tokens = nltk.word_tokenize(raw)
            text = nltk.Text(tokens)

            # remove punctuation, count raw words
            nonPunct = re.compile('.*[A-Za-z].*')
            raw_words = [w for w in text if nonPunct.match(w)]
            raw_word_count = Counter(raw_words)

            # stop words
            no_stop_words = [w for w in raw_words if w.lower() not in stops]
            no_stop_words_count = Counter(no_stop_words)

            # save the results
            results = sorted(
                no_stop_words_count.items(),
                key=operator.itemgetter(1),
                reverse=True
            )
            try:
                result = Result(
                    url=url,
                    result_all=raw_word_count,
                    result_no_stop_words=no_stop_words_count
                )
                db.session.add(result)
                db.session.commit()
            except:
                errors.append("Unable to add item to database.")
    return render_template('smh/index.html', user=user, errors=errors, results=results)



#boilerplate
@app.route('/login', methods=['GET', 'POST'])
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    user = 'Stranger'
    if form.validate_on_submit():
        user = User.query.filter_by(nickname=form.nickname.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            if request.args.get('next') is url_for('auth.login'):
                return redirect(url_for('index'))
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid username or password.')
        return render_template('auth/login.html',
                                title="Log In",
                                form=form,
                                user=user)
    return render_template('auth/login.html',
                                title="Log In",
                                form=form,
                                user=user)

#boilerplate    
@app.route('/logout')
@auth.route('/logout')
def logout():
    logout_user()
    flash('You are now logged out.')
    return redirect(url_for('index'))

#boilerplate
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    user = 'Stranger'
    created_time = datetime.utcnow()
    check_email = User.query.filter_by(email=form.email.data).first()
    check_nickname = User.query.filter_by(nickname=form.nickname.data).first()
    if form.validate_on_submit():
        if not check_email and not check_nickname:
            user = User(nickname=form.nickname.data, created=created_time, email=form.email.data, password=form.password.data, catchphrase=form.catchphrase.data)
            blogic.add_user(user)
            login_user(user, form.remember_me.data)
            flash('Account created successfully!')
            return redirect(request.args.get('next') or url_for('index'))
        flash('Username or password is already taken. If this is you please sign in.')
    return render_template('signup.html',
                                title="Log In",
                                form=form,
                                user=user)

#boilerplate
@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    #user is the db object of the nickname argument
    user = User.query.filter_by(nickname=nickname).first()
    #current is the db object of the current logged in user
    current = User.query.filter_by(nickname=current_user.nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('discover'))
    #check if the current logged in user is the same as the one we are trying to follow
    if user.id == current_user.id:
        flash('You can\'t follow yourself!')
        return redirect(url_for('profile', nickname=nickname))
    #otherwise, let's follow the user!
    u = current.follow(user)
    if u is None:
        flash('Already following ' + nickname + '.')
        return redirect(url_for('profile', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!')
    return redirect(url_for('profile', nickname=nickname))

#boilerplate
@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    #current is the db object of the current logged in user
    current = User.query.filter_by(id=current_user.id).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('discover'))
    if user.id == current_user.id:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('profile', nickname=nickname))
    u = current.unfollow(user)
    if u is None:
        flash('You are not following ' + nickname + '.')
        return redirect(url_for('profile', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('profile', nickname=nickname))

if __name__ == '__main__':
    app.run()