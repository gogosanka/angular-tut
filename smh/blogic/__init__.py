from smh import db
from smh.models.models import *
from flask import session, redirect, url_for
from datetime import datetime

default_titles = ['Lily', 'Jeanna', 'Angelika', 'Ronald', 'Brandie', 'Doreatha', 'Leann', 'Vivienne', 'Sabina', 'Elois', 'Bernita', 'Londa', 'Rosa',
'Alba', 'Blanche', 'Doug', 'Mana', 'Sherrill', 'Masako', 'Rod', 'Herb', 'Myriam', 'Ciara', 'Katy', 'Kisha', 'Kym', 'Xochitl', 'Flo',
 'Sherill', 'Anika', 'Jannie', 'Patti', 'Jamar', 'Delilah', 'Maris', 'Glenna', 'Ling', 'Roselyn', 'Beatris', 'Rae']

#post transactions

def update(body,author,postid,title="Untitled"):
    '''user and data scope is for the database to understand
        who the user is, and then create a Post db object
        containing the author of the post, and the body of
        the post.'''
    post_record = Post.query.filter_by(id=postid).first()
    post_record.body = body
    post_record.title = title
    db.session.commit()

def delete(post):
    '''delete a post.'''
    db.session.delete(post)
    db.session.commit()
    
def recycle(post):
    '''recycle a post'''
    if post.rebin == 'true':
        post.rebin = 'false'
    elif post.rebin == 'false':
        post.rebin = 'true'
    db.session.commit()

def new(post,author,title="Untitled"):
    '''create a new post.'''
    created_time = datetime.utcnow()
    user = User.query.filter_by(nickname=author).first()
    entry = Post(body=post, author=user, title=title, timestamp=created_time, rebin='false', public='true')
    db.session.add(entry)
    db.session.commit()

#user transactions

def check_username(username,password):
    user = User.query.filter_by(nickname=username).first()
    passw = user.password
    if passw == password:
        session['current_user'] = username
        return redirect(url_for('posts'))

def add_user(user):
    db.session.add(user)
    db.session.commit()
    #make user follow themself
    db.session.add(user.follow(user))
    db.session.commit()

#vibe transactions   
def send_vibe(sender, vibe, recipient):
    created_time = datetime.utcnow()
    vibe.created_by = sender.nickname
    vibe.created = created_time
    if vibe.private != True:
        sender.vibes_to_date += 1
    recipient.vibes.append(vibe)
    db.session.add(recipient, vibe)
    db.session.commit()

def delete_vibe(user, vibe):
    user.vibes.remove(vibe)
    db.session.add(user)
    db.session.commit()

#recipient is me, the one accepting the user's vibe
def accept_vibe(recipient, user, vibe):
    recipient.accept_vibe(user, vibe)
    recipient.follow_vibe(vibe)
    db.session.add(recipient)
    db.session.commit()

def push_vibe(self, user, vibe):
    creator = User.query.filter_by(nickname=user.nickname).first()
    note = (str(self.nickname) + " is vibing with you " + "<placeholder for 'with-for-on-during-etc>: " + vibe.message)
    message = Message(message=note, sent_by=self.nickname)
    creator.inbox.append(message)
    db.session.add(creator, message)
    db.session.commit()
            
#make sure that User objects are objects and not fields. specify the field FOR the transaction
#also make sure the message is a MESSAGE OBJECT
#also alter this to take in multiple recipients if need be. probably not, now that i think about it
def send_message(sender, message, recipient):
    message.sent_by = sender.nickname
    recipient.messages.append(message)
    db.session.add(recipient, message)
    db.session.commit()

def ask(body, author):
    timestamp = datetime.utcnow()
    user = User.query.filter_by(nickname=author).first()
    entry = Question(body=body, author=user, timestamp=timestamp)
    db.session.add(entry)
    db.session.commit()

def submit_a_question(body, author):
    timestamp = datetime.utcnow()
    user = User.query.filter_by(nickname=author).first()
    question = Question(body=body, author=user, timestamp=timestamp)
    db.session.add(question)
    db.session.commit()

