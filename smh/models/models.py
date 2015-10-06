#boilerplate
from smh import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from smh import lm
from smh.blogic import *#imports depend on where you're importing from, specifically if it's from the app or within another folder
from hashlib import md5

#boilerplate
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

'''the db.Model class has a all() method which queries the db
   and returns all the db rows created. For example,
   users = User.query.get(1) #returns the 1st user object
   users.posts.all() #will return all the posts associated with user 1
   the Post class is defined below, and has a relationship within
   the User class, which is why this works.'''

#boilerplate
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

#boilerplate
messages = db.Table('messages',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('message_id', db.Integer, db.ForeignKey('message.id'))
)

#boilerplate
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(32), index=True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    post = db.relationship('Post', backref='author', lazy='dynamic')
    catchphrase = db.Column(db.String(32))
    created = db.Column(db.DateTime)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    followed = db.relationship('User',
                                secondary=followers,
                                primaryjoin=(followers.c.follower_id == id),
                                secondaryjoin=(followers.c.followed_id == id),
                                backref=db.backref('followers', lazy='dynamic'),
                                lazy='dynamic')
    inbox = db.relationship('Message',
                            secondary=messages,
                            backref=db.backref('recipient_inbox', lazy='dynamic'),
                            lazy='dynamic')
    
    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc()) #read this thoroughly to understand it
    password_hash = db.Column(db.String(128))
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
    def is_anonymous():
        return False
    def get_id(self):
        return (self.id)
    def __repr__(self):
        return (self.nickname)
    #handle following a user
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self
    #handle unfollowing a user
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self
    #handle checking if a user is being followed
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    #handle if a vibe is to be followed
    def follow_vibe(self, vibe):
        if not self.is_following_vibe(vibe):
            self.vibes.append(vibe)
            return self
    def unfollow_vibe(self, vibe):
        if self.is_following_vibe(vibe):
            self.vibes.remove(vibe)
            self.vibes_accepted.remove(vibe)
            return self
    def is_following_vibe(self, vibe):
        return self.vibes.filter(vibes.c.vibe_id == vibe.id).count() > 0
    #takes in a user so that the message shows who accepted the vibe
    def alert_watchers(self, user, vibe):
        if not self.has_accepted_vibe(vibe):
            creator = User.query.filter_by(nickname=vibe.created_by.nickname).first()
            #message should check if a message label is created, and return the label as a placeholder instead
            self.vibes_accepted.append(vibe)
            blogic.push_vibe(self, user, vibe)
            return self
    def send_message(self, message):
        self.messages.append(message)
        return self
    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)

#boilerplate
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    sent_by = db.Column(db.String(32))
    created_timestamp = db.Column(db.DateTime)
    seen_timestamp = db.Column(db.DateTime)
    #be cute! randomize the <says> to say other things like "vibes, explains, announces, mumbles, bellows" etc.
    #I left a placeholder for now, but try randomizing those words and replace <says> with a variable
    def __repr__(self):
        return (self.sent_by + " <says>: "+ self.message)

#boilerplate
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rebin = db.Column(db.String(5))
    public = db.Column(db.String(8))
    body = db.Column(db.String(500))
    title = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rating = db.Column(db.Boolean)
    def hide(self):
        self.public = 'false'
        db.session.commit()
    def unhide(self):
        self.public = 'true'
        db.session.commit()
    def __repr__(self):
        repre = "%r" % self.body
        return str(repre)

#application models (non-boilerplate)
from sqlalchemy.dialects.postgresql import JSON

class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String())
    result_all = db.Column(db.String())
    result_no_stop_words = db.Column(db.String())

    def __init__(self, url, result_all, result_no_stop_words):
        self.url = url
        self.result_all = result_all
        self.result_no_stop_words = result_no_stop_words

    def __repr__(self):
        return '<id {}>'.format(self.id)
