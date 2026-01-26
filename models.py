from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from flask_login import UserMixin

db = SQLAlchemy()

class TokenBlocklist(db.Model):
    __tablename__ = 'token_blocklist'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<TokenBlocklist {self.jti}>'
    
favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('ad_id', db.Integer, db.ForeignKey('ad.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255), nullable=False)
    created_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    ads = db.relationship('Ad', backref='author', lazy=True, cascade='all, delete-orphan')
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    messages_received = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic')
    reviews_written = db.relationship('Review', foreign_keys='Review.author_id', backref='author', lazy='dynamic')
    reviews_received = db.relationship('Review', foreign_keys='Review.target_user_id', backref='target_user', lazy='dynamic', cascade='all, delete-orphan')
    saved_ads = db.relationship(
        'Ad', 
        secondary=favorites, 
        backref=db.backref('favorited_by', lazy='dynamic'), 
        lazy='dynamic'
    )

    @property
    def average_rating(self):
        reviews = self.reviews_received.all()
        if not reviews:
            return 0
        total = sum([r.rating for r in reviews])
        return round(total / len(reviews), 1)

    def __repr__(self):
        return f'<User {self.name}>'

    def like(self, ad):
        if not self.has_liked(ad):
            self.saved_ads.append(ad)

    def unlike(self, ad):
        if self.has_liked(ad):
            self.saved_ads.remove(ad)

    def has_liked(self, ad):
        return self.saved_ads.filter(favorites.c.ad_id == ad.id).count() > 0

class Ad(db.Model):
    __tablename__ = 'ad'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=True)
    price_unit = db.Column(db.String(20), default='rub')
    ad_type = db.Column(db.String(20), nullable=False, default='item') 
    condition = db.Column(db.String(20), nullable=True)
    district = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), nullable=True)
    views = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')
    category = db.Column(db.String(100), nullable=True)
    created_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    photos = db.relationship('AdPhoto', backref='ad', lazy=True, cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='ad', lazy=True)

    def __repr__(self):
        return f'<Ad {self.title} ({self.ad_type})>'

class AdPhoto(db.Model):
    __tablename__ = 'ad_photo'
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(255), nullable=False) # Имя файла или URL
    ad_id = db.Column(db.Integer, db.ForeignKey('ad.id'), nullable=False)

    def __repr__(self):
        return f'<Photo {self.image_filename}>'

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ad_id = db.Column(db.Integer, db.ForeignKey('ad.id'), nullable=True)

    def __repr__(self):
        return f'<Message {self.id} from {self.sender_id} to {self.recipient_id}>'
    
class Review(db.Model):
    __tablename__ = 'review'
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  
    text = db.Column(db.Text, nullable=True)        
    created_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    target_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    ad_id = db.Column(db.Integer, db.ForeignKey('ad.id'), nullable=True)

    def __repr__(self):
        return f'<Review {self.rating} stars for user {self.target_user_id}>'
    
