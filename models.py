from enum import Enum
from datetime import datetime, date
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin
from sqlalchemy import or_
from sahara import app, bcrypt, db, login_manager

####################################################################################################
#                                            CONSTANTS                                             #
####################################################################################################


class Privileges(Enum):
    """
    Values for user privileges.
    """
    ADMIN = 1
    CUSTOMER = 2


class States(Enum):
    """
    Values for user states.
    """
    ACTIVE = 1
    INACTIVE = 2
    SUSPENDED = 3


class Categories(Enum):
    """
    Values for book categories.
    """
    ACTION = 1
    FICTION = 2
    GRAPHIC_NOVEL = 3
    HORROR = 4
    MYSTERY = 5
    NON_FICTION = 6
    SCI_FI = 7


class OrderStates(Enum):
    """
    Values for order states.
    """
    PROCESSING = 1
    SHIPPED = 2
    DELIVERED = 3


####################################################################################################
#                                        UTILITY FUNCTIONS                                         #
####################################################################################################


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


####################################################################################################
#                                          LINKING TABLES                                          #
####################################################################################################


# Table to link books to publishers
book_to_publisher = db.Table(
    'book_publisher',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('publisher_id', db.Integer, db.ForeignKey('publisher.id'), primary_key=True),
)


# Table to link books to authors
book_to_author = db.Table(
    'book_author',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('author.id'), primary_key=True),
)


# Table to link books to categories
book_to_category = db.Table(
    'book_category',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('bookcategory_id', db.Integer, db.ForeignKey('bookcategory.id'), primary_key=True),
)


# Table to link users to user priveleges
user_to_userprivilege = db.Table(
    'user_userprivilege',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('userprivilege_id', db.Integer, db.ForeignKey('userprivilege.id'), primary_key=True),
)


# Table to link users to user states
user_to_userstate = db.Table(
    'user_userstate',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('userstate_id', db.Integer, db.ForeignKey('userstate.id'), primary_key=True),
)


# Table to link users to payment cards
user_to_paymentcard = db.Table(
    'user_paymentcard',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('paymentcard_id', db.Integer, db.ForeignKey('paymentcard.id'), primary_key=True),
)


# Table to link users to addresses
user_to_address = db.Table(
    'user_address',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('address_id', db.Integer, db.ForeignKey('address.id'), primary_key=True),
)


# Table to link payment cards to addresses
paymentcard_to_address = db.Table(
    'paymentcard_address',
    db.Column('paymentcard_id', db.Integer, db.ForeignKey('paymentcard.id'), primary_key=True),
    db.Column('address_id', db.Integer, db.ForeignKey('address.id'), primary_key=True),
)

# Table to link books to images
book_to_image = db.Table(
    'book_image',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('image_id', db.Integer, db.ForeignKey('image.id'), primary_key=True),
)

# Table to link carts to books
cart_to_book = db.Table(
    'cart_book',
    db.Column('cart_id', db.Integer, db.ForeignKey('cart.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
)

# Table to link orders to books
order_to_book = db.Table(
    'order_book',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
)

user_to_cart = db.Table(
    'user_cart',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('cart_id', db.Integer, db.ForeignKey('cart.id'), primary_key=True),
)

cart_to_cartitem = db.Table(
    'cart_cartitem',
    db.Column('cart_id', db.Integer, db.ForeignKey('cart.id'), primary_key=True),
    db.Column('cartitem_id', db.Integer, db.ForeignKey('cartitem.id'), primary_key=True),
)

cartitem_to_book = db.Table(
    'cartitem_book',
    db.Column('cartitem_id', db.Integer, db.ForeignKey('cartitem.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
)

order_to_orderstate = db.Table(
    'order_orderstate',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('orderstate_id', db.Integer, db.ForeignKey('orderstate.id'), primary_key=True),
)

order_to_cart = db.Table(
    'order_cart',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('cart_id', db.Integer, db.ForeignKey('cart.id'), primary_key=True),
)

order_to_paymentcard = db.Table(
    'order_paymentcard',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('paymentcard_id', db.Integer, db.ForeignKey('paymentcard.id'), primary_key=True),
)

order_to_address = order_to_address = db.Table(
    'order_address',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('address_id', db.Integer, db.ForeignKey('address.id'), primary_key=True),
)

user_to_order = db.Table(
    'user_order',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
)

order_to_promotion = db.Table(
    'order_promotion',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('promotion_id', db.Integer, db.ForeignKey('promotion.id'), primary_key=True),
)

####################################################################################################
#                                             DB MODELS                                            #
####################################################################################################


################################################################################
# User #########################################################################
class User(db.Model, UserMixin):
    __tablename__ = 'user'

    # Auth fields
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    # Subscription status
    is_subscribed = db.Column(db.Boolean, nullable=False)

    # Personal Info
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    address = db.relationship(
        'Address',
        secondary=user_to_address,
        backref=db.backref('users'),
        uselist=False
    )
    payment_cards = db.relationship(
        'PaymentCard',
        secondary=user_to_paymentcard,
        backref=db.backref('users')
    )
    privilege = db.relationship(
        'UserPrivilege',
        secondary=user_to_userprivilege,
        backref=db.backref('users'),
        uselist=False
    )
    state = db.relationship(
        'UserState',
        secondary=user_to_userstate,
        backref=db.backref('users'),
        uselist=False
    )
    cart = db.relationship(
        'Cart',
        secondary=user_to_cart,
        backref=db.backref('users'),
        uselist=False
    )
    previous_orders = db.relationship(
        'Order',
        secondary=user_to_order,
        backref=db.backref('user')
    )

    # Factory Constructors
    @staticmethod
    def from_email(email):
        """
        Returns the `User` corresponding to the inputted `email`, or `None` if such a User doesn't
        exist.

        While this function returns `None` if the User does not exist, the `User.exists()` function
        is recommended for checking the existence of a `User` in the database.
        """
        requested_user = User.query.filter_by(email=email).first()
        if requested_user:
            return requested_user
        else:
            return None

    @staticmethod
    def from_id(user_id):
        """
        Returns the `User` corresponding to the inputted `user_id`, or `None` if such a User doesn't
        exist.

        While this function returns `None` if the User does not exist, the `User.exists()` function
        is recommended for checking the existence of a `User` in the database.
        """
        requested_user = User.query.filter_by(id=user_id).first()
        if requested_user:
            return requested_user
        else:
            return None

    @staticmethod
    def from_timed_token(token):
        """
        Returns the `User` corresponding to the inputted `token`, or `None` if such a User doesn't
        exist or if the inputted token has expired.
        """
        s = Serializer(app.config['SECRET_KEY'])

        try:
            user_id = s.loads(token)['user_id']
            return User.from_id(user_id)
        except Exception:
            return None

    # Data Access
    @staticmethod
    def get_all():
        """
        Returns a list of all Users signed up for this application.

        Currently, this function does not load this list lazily, so it's not optimized for large
        numbers of Users.
        """
        return User.query.all()

    def __commit_to_database(self):
        """
        Commits this User to the database in its current state.
        """
        db.session.add(self)
        db.session.commit()

    def set_password(self, password, commit=True):
        """
        Changes the password of this User.

        A database action is only initiated on `commit=True`, so pass `commit=False` when making
        successive changes in order to avoid making unnecessary database calls.

        NOTE: This method should only be used on Users that are guaranteed to already be in the
        database.
        """
        self.password = password

        if commit:
            self.__commit_to_database()

    def set_subscription_status(self, new_status, commit=True):
        """
        Changes the subscription status of this User.

        A database action is only initiated on `commit=True`, so pass `commit=False` when making
        successive changes in order to avoid making unnecessary database calls.

        NOTE: This method should only be used on Users that are guaranteed to already be in the
        database.
        """
        self.is_subscribed = new_status

        if commit:
            self.__commit_to_database()

    def set_first_name(self, first_name, commit=True):
        """
        Changes the first name of this User.

        A database action is only initiated on `commit=True`, so pass `commit=False` when making
        successive changes in order to avoid making unnecessary database calls.

        NOTE: This method should only be used on Users that are guaranteed to already be in the
        database.
        """
        self.first_name = first_name

        if commit:
            self.__commit_to_database()

    def set_last_name(self, last_name, commit=True):
        """
        Changes the last name of this User.

        A database action is only initiated on `commit=True`, so pass `commit=False` when making
        successive changes in order to avoid making unnecessary database calls.

        NOTE: This method should only be used on Users that are guaranteed to already be in the
        database.
        """
        self.last_name = last_name

        if commit:
            self.__commit_to_database()

    def set_phone_number(self, phone_number, commit=True):
        """
        Changes the phone number of this User.

        A database action is only initiated on `commit=True`, so pass `commit=False` when making
        successive changes in order to avoid making unnecessary database calls.

        NOTE: This method should only be used on Users that are guaranteed to already be in the
        database.
        """
        self.phone_number = phone_number

        if commit:
            self.__commit_to_database()

    def set_address(self, address, commit=True):
        """
        Changes the address of this User.

        A database action is only initiated on `commit=True`, so pass `commit=False` when making
        successive changes in order to avoid making unnecessary database calls.

        NOTE: This method should only be used on Users that are guaranteed to already be in the
        database.
        """
        self.address = address

        if commit:
            self.__commit_to_database()

    def set_payment_cards(self, payment_cards, commit=True):
        """
        Changes the payment cards of this User.

        A database action is only initiated on `commit=True`, so pass `commit=False` when making
        successive changes in order to avoid making unnecessary database calls.

        NOTE: This method should only be used on Users that are guaranteed to already be in the
        database.
        """
        self.payment_cards = payment_cards

        if commit:
            self.__commit_to_database()

    def add_payment_card(self, payment_card, commit=True):
        """
        Changes the payment cards of this User.

        A database action is only initiated on `commit=True`, so pass `commit=False` when making
        successive changes in order to avoid making unnecessary database calls.

        NOTE: This method should only be used on Users that are guaranteed to already be in the
        database.
        """
        self.payment_cards.append(payment_card)

        if commit:
            self.__commit_to_database()

    def remove_payment_card(self, payment_card, commit=True):
        """
        Changes the payment cards of this User.

        A database action is only initiated on `commit=True`, so pass `commit=False` when making
        successive changes in order to avoid making unnecessary database calls.

        NOTE: This method should only be used on Users that are guaranteed to already be in the
        database.
        """
        self.payment_cards.remove(payment_card)

        if commit:
            self.__commit_to_database()

    def set_user_state(self, state_id, commit=True):
        """
        Changes the state of this User.

        A database action is only initiated on `commit=True`, so pass `commit=False` when making
        successive changes in order to avoid making unnecessary database calls.

        NOTE: This method should only be used on Users that are guaranteed to already be in the
        database.
        """
        self.state = UserState.from_id(state_id)

        if commit:
            self.__commit_to_database()

    def confirm_order(self, promotion_applied=None, payment_method=None, shipping_addr=None):
        subtotal = self.cart.subtotal
        if promotion_applied:
            subtotal *= ((100 - promotion_applied.discount) / 100)

        # Tax calculation
        order_total = subtotal + (subtotal * 0.07) + 3.99

        # Create order for db and add to previous orders list
        new_order = Order(
            user_id=self.id,
            total=order_total,
            cart=self.cart,
            promotion_applied=promotion_applied,
            payment_method=payment_method,
            shipping_address=shipping_addr,
            placed_datetime=datetime.now(),
            state=OrderState.from_id(OrderStates.PROCESSING.value),
        )

        self.previous_orders.append(new_order)

        self.cart = Cart.next_available()

        self.__commit_to_database()

    def commit_to_system(self):
        """
        Commits a new User to the database.
        """
        # Add privilege and state to user
        # The only admin for this website is identified by "admin@sahara.com", so we check the
        # User's email address to see whether or not this User should have admin privileges,
        # and assign privileges and states accordingly.
        if self.email == "admin@sahara.com":
            # User should be ADMIN and ACTIVE
            self.privilege = UserPrivilege.from_id(Privileges.ADMIN.value)
            self.state = UserState.from_id(States.ACTIVE.value)
        else:
            # User should be CUSTOMER and INACTIVE
            self.privilege = UserPrivilege.from_id(Privileges.CUSTOMER.value)
            self.state = UserState.from_id(States.INACTIVE.value)

            user_id = User.query.order_by('id').all()[-1].id + 1
            self.cart = Cart.next_available()

        # Add user to session
        self.__commit_to_database()

    # Utilities
    @staticmethod
    def exists(email):
        """
        Returns true if there is a User that exists by the inputted `email`.
        """
        if User.query.filter_by(email=email).first():
            return True
        else:
            return False

    def get_privilege_str(self):
        """
        Returns `'Admin'` if this User is the system administrator and `'Customer'` otherwise.
        """
        if self.privilege.id == Privileges.ADMIN.value:
            return "Admin"
        else:
            return "Customer"

    def get_state_str(self):
        """
        Returns a string based on the state of this User.
        'Active' if this User is active.
        'Inactive' if this User is inactive.
        'Suspended' if this User is suspended.
        """
        if self.state.id == States.INACTIVE.value:
            return 'Inactive'
        elif self.state.id == States.SUSPENDED.value:
            return 'Suspended'
        else:
            return 'Active'

    def get_timed_token(self, expires_sec=1800):
        """
        Returns a string representing a timed token that encapsulates this `User`'s id for
        `expires_sec` seconds.
        """
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def __repr__(self):
        """
        Returns a string representation of this object.
        """
        return f"User(ID = {self.id}, Email = {self.email})"

    # List of orders by ID
    def get_order_history(self):
        pass


################################################################################
# Address ######################################################################
class Address(db.Model):
    __tablename__ = 'address'

    # Properties
    id = db.Column(db.Integer, primary_key=True)
    street_1 = db.Column(db.String(50), nullable=False)
    street_2 = db.Column(db.String(50), nullable=True)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(15), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)

    # Constructors
    @staticmethod
    def dummy():
        """
        Returns a dummy address.

        Potential use for the system administrator.
        """
        return Address(
            street_1="123 Street Road",
            street_2="321",
            city="Athens",
            state="GA",
            zip_code="30602"
        )

    @staticmethod
    def exists(street_1="", street_2="", city="", state="", zip_code=""):
        addr = Address.query.filter_by(street_1=street_1,
                                       street_2=street_2,
                                       city=city,
                                       state=state,
                                       zip_code=zip_code).first()
        if addr:
            return True
        else:
            return False

    @staticmethod
    def get_by_info(street_1="", street_2="", city="", state="", zip_code=""):
        if Address.exists(street_1=street_1,
                          street_2=street_2,
                          city=city,
                          state=state,
                          zip_code=zip_code):
            return Address.query.filter_by(street_1=street_1,
                                           street_2=street_2,
                                           city=city,
                                           state=state,
                                           zip_code=zip_code).first()
        else:
            addr = Address(street_1=street_1,
                           street_2=street_2,
                           city=city,
                           state=state,
                           zip_code=zip_code)
            addr.commit_to_system()
            return addr

    def commit_to_system(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        """
        Returns a string representation of this object.
        """
        res = ''
        res += f'{self.street_1}, '
        if self.street_2:
            res += self.street_2
        res += f'{self.city}, {self.state} {self.zip_code}'
        return res

    def getStateNumber(self, state):
        state = str(state).strip()
        states = {
            "Alabama": 1,
            "Alaska": 2,
            "Arizona": 3,
            "Arkansas": 4,
            "California": 5,
            "Colorado": 6,
            "Connecticut": 7,
            "Delaware": 8,
            "District of Columbia": 9,
            "Florida": 10,
            "Georgia": 11,
            "Hawaii": 12,
            "Idaho": 13,
            "Illinois": 14,
            "Indiana": 15,
            "Iowa": 16,
            "Kansas": 17,
            "Kentucky": 18,
            "Louisiana": 19,
            "Maine": 20,
            "Montana": 21,
            "Nebraska": 22,
            "Nevada": 23,
            "New Hampshire": 24,
            "New Jersey": 25,
            "New Mexico": 26,
            "New York": 27,
            "North Carolina": 28,
            "North Dakota": 29,
            "Ohio": 30,
            "Oklahoma": 31,
            "Oregon": 32,
            "Maryland": 33,
            "Massachusetts": 34,
            "Michigan": 35,
            "Minnesota": 36,
            "Mississippi": 37,
            "Missouri": 38,
            "Pennsylvania": 39,
            "Rhode Island": 40,
            "South Carolina": 41,
            "South Dakota": 42,
            "Tennessee": 43,
            "Texas": 44,
            "Utah": 45,
            "Vermont": 46,
            "Virginia": 47,
            "Washington": 48,
            "West Virginia": 49,
            "Wisconsin": 50,
            "Wyoming": 51}

        return states.get(state)

################################################################################
# PaymentCard ##################################################################


class PaymentCard(db.Model):
    __tablename__ = 'paymentcard'

    # Properties
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    number = db.Column(db.String(60), nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)
    name_on_card = db.Column(db.String(60), nullable=False)
    security_code = db.Column(db.String(60), nullable=False)
    last_four_digits = db.Column(db.String(4), nullable=False)

    @staticmethod
    def from_id(card_id):
        card = PaymentCard.query.filter_by(id=card_id).first()
        if card:
            return card
        else:
            return None


################################################################################
# UserPrivilege ################################################################
class UserPrivilege(db.Model):
    __tablename__ = 'userprivilege'

    # Properties
    id = db.Column(db.Integer, primary_key=True)

    # Constructors
    @staticmethod
    def from_id(privilege_id):
        # Check for privilege type in db
        privilege = UserPrivilege.query.filter_by(id=privilege_id).first()
        if privilege:
            # It exists, return it
            return privilege
        else:
            # Make one and store it
            return UserPrivilege(id=privilege_id)


################################################################################
# UserState ####################################################################
class UserState(db.Model):
    __tablename__ = 'userstate'

    # Properties
    id = db.Column(db.Integer, primary_key=True)

    # Constructors
    @staticmethod
    def from_id(state_id):
        if UserState.query.filter_by(id=state_id).first():
            return UserState.query.filter_by(id=state_id).first()
        else:
            return UserState(id=state_id)


################################################################################
# Book  ########################################################################
class Book(db.Model):
    __tablename__ = 'book'

    # Properties
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(13), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    edition = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    authors = db.relationship(
        'Author',
        secondary=book_to_author,
        backref=db.backref('books')
    )
    publisher = db.relationship(
        'Publisher',
        secondary=book_to_publisher,
        backref=db.backref('books'),
        uselist=False
    )
    publishing_year = db.Column(db.Date, nullable=False)
    cover_image = db.relationship(
        'Image',
        secondary=book_to_image,
        backref=db.backref('books'),
        uselist=False
    )
    category = db.relationship(
        'BookCategory',
        secondary=book_to_category,
        backref=db.backref('books'),
        uselist=False
    )
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)

    # Data Access
    @staticmethod
    def get_all():
        """
        Returns a list of all Books kept track of by this application.

        Currently, this function does not load this list lazily, so it's not optimized for large
        numbers of Users.
        """
        return Book.query.all()

    def __commit_to_database(self):
        """
        Commits this Book to the database in its current state.
        """
        db.session.add(self)
        db.session.commit()

    def commit_to_system(self):
        db.session.add(self)
        db.session.commit()

    """
    @staticmethod
    def search_by_isbn(isbn):
        return Book.query.filter(Book.isbn.like(isbn))
    """

    """
    @staticmethod
    def search_by_title(title):
        return Book.query.filter(Book.title.like(title))
    """

    @staticmethod
    def search(search_term):
        term = search_term.strip()
        return Book.query.filter(or_(
            Book.title.like(f'%{term}%'),
            Book.publishing_year.like(f'%{term}%'),
            Book.isbn.like(f'%{term}%'))).all()
        # Book.authors[0].first_name.like(f'%{term}%'),
        # Book.authors[0].last_name.like(f'%{term}%')

    @staticmethod
    def search_by_category(category_id):
        return Book.query.filter_by(category=BookCategory.from_id(category_id)).all()

    @staticmethod
    def get_by_id(book_id):
        return Book.query.get(book_id)

    @staticmethod
    def search_by_quantity():
        return Book.query.order_by(Book.quantity)

    # Utilities
    def __repr__(self):
        return f'Book(ID = {self.id}, Title = {self.title})'


################################################################################
# Author #######################################################################
class Author(db.Model):
    __tablename__ = 'author'

    # Properties
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    @staticmethod
    def by_name(first_name, last_name):
        authors_by_first = Author.query.filter_by(first_name=first_name)
        author = authors_by_first.filter_by(first_name=last_name).first()

        if author:
            return author
        else:
            return Author(first_name=first_name, last_name=last_name)

    def __repr__(self):
        return f'{self.first_name} {self.last_name}'


################################################################################
# BookCategory #################################################################
class BookCategory(db.Model):
    __tablename__ = 'bookcategory'

    # Properties
    id = db.Column(db.Integer, primary_key=True)

    # Constructors
    @staticmethod
    def from_id(category_id):
        category = BookCategory.query.filter_by(id=category_id).first()
        if category:
            return category
        else:
            return BookCategory(id=category_id)

    def __repr__(self):
        if self.id == Categories.ACTION.value:
            return 'Action'
        elif self.id == Categories.FICTION.value:
            return 'Fiction'
        elif self.id == Categories.GRAPHIC_NOVEL.value:
            return 'Graphic Novel'
        elif self.id == Categories.HORROR.value:
            return 'Horror'
        elif self.id == Categories.MYSTERY.value:
            return 'Mystery'
        elif self.id == Categories.NON_FICTION.value:
            return 'Non-Fiction'
        elif self.id == Categories.SCI_FI.value:
            return 'Sci-Fi'
        else:
            return 'Uncategorized'


################################################################################
# Publisher ####################################################################
class Publisher(db.Model):
    __tablename__ = 'publisher'

    # Properties
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    # Constructors
    @staticmethod
    def from_name(publisher_name):
        publisher = Publisher.query.filter_by(name=publisher_name).first()
        if publisher:
            return publisher
        else:
            return Publisher(name=publisher_name)


################################################################################
# Image ########################################################################
class Image(db.Model):
    __tablename__ = 'image'

    # Properties
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)

    @staticmethod
    def from_filename(filename):
        image = Image.query.filter_by(filename=filename).first()
        if image:
            return image
        else:
            return Image(filename=filename)


################################################################################
# Promotion ####################################################################
class Promotion(db.Model):
    __tablename__ = 'promotion'

    # Properties
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)
    discount = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_sent = db.Column(db.Boolean, nullable=False)

    def send(self):
        self.is_sent = True
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def delete(promo_id):
        promo = Promotion.from_id(promo_id)
        if promo:
            db.session.delete(promo)
            db.session.commit()

    # Data Access
    @staticmethod
    def exists(promo_code):
        if Promotion.query.filter_by(code=promo_code).first():
            return True
        else:
            return False

    @staticmethod
    def from_code(promo_code):
        promo = Promotion.query.filter_by(code=promo_code).order_by('start_date').first()
        if promo:
            return promo
        else:
            return None
    
    @staticmethod
    def from_id(promo_id):
        promo = Promotion.query.filter_by(id=promo_id).first()
        if promo:
            return promo
        else:
            return None

    @property
    def is_active(self):
        return (self.start_date <= date.today()) and (date.today() < self.end_date)

    @staticmethod
    def get_all():
        """
        Returns a list of all Promotions kept track of by this application.

        Currently, this function does not load this list lazily, so it's not optimized for large
        numbers of Users.
        """
        return Promotion.query.all()

    def commit_to_system(self):
        """
        Commits this Promotion to the database in its current state.
        """
        if not Promotion.query.filter_by(id=self.id).first():
            db.session.add(self)
            db.session.commit()


class Cart(db.Model):
    __tablename__ = 'cart'

    id = db.Column(db.Integer, primary_key=True)
    cart_items = db.relationship(
        'CartItem',
        secondary=cart_to_cartitem,
        backref=db.backref('cart'),
    )
    subtotal = db.Column(db.Float, nullable=False)

    @staticmethod
    def next_available():
        return Cart(subtotal=0.0)

    def __commit_to_database(self):
        db.session.add(self)
        db.session.commit()

    def add_book(self, book):
        cart_item = CartItem.from_cart_id(self.id, book.id)

        if cart_item not in self.cart_items:
            self.cart_items.append(cart_item)

        cart_item.quantity += 1
        self.subtotal = self.subtotal + book.price


        self.__commit_to_database()

    def remove_book(self, book):
        cart_item = CartItem.from_cart_id(self.id, book.id)
        cart_item.quantity -= 1

        if cart_item.quantity == 0:
            self.cart_items.remove(cart_item)

        self.subtotal = self.subtotal - book.price


        if self.subtotal <= 0.0:
            self.subtotal = 0.0

        self.__commit_to_database()

    def clear(self):
        for cart_item in self.cart_items:
            cart_item.quantity = 0

        self.cart_items.clear()
        self.subtotal = 0.0

        self.__commit_to_database()


class CartItem(db.Model):
    __tablename__ = 'cartitem'

    id = db.Column(db.Integer, primary_key=True)
    book = db.relationship(
        'Book',
        secondary=cartitem_to_book,
        backref=db.backref('cart_item'),
        uselist=False
    )
    book_id = db.Column(db.Integer, nullable=False)
    cart_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    @staticmethod
    def from_cart_id(cart_id, book_id):
        cart_item = CartItem.query.filter_by(book_id=book_id, cart_id=cart_id).first()
        if cart_item:
            return cart_item
        else:
            return CartItem(book=Book.get_by_id(book_id),
                            book_id=book_id,
                            cart_id=cart_id,
                            quantity=0)

    def __repr__(self):
        return f'CartItem(book={self.book}, quantity={self.quantity})'


class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    cart = db.relationship(
        'Cart',
        secondary=order_to_cart,
        backref=db.backref('order'),
        uselist=False
    )
    promotion_applied = db.relationship(
        'Promotion',
        secondary=order_to_promotion,
        backref=db.backref('order'),
        uselist=False
    )
    payment_method = db.relationship(
        'PaymentCard',
        secondary=order_to_paymentcard,
        backref=db.backref('order'),
        uselist=False
    )
    shipping_address = db.relationship(
        'Address',
        secondary=order_to_address,
        backref=db.backref('order'),
        uselist=False
    )
    placed_datetime = db.Column(db.DateTime, nullable=False)

    state = db.relationship(
        'OrderState',
        secondary=order_to_orderstate,
        backref=db.backref('order'),
        uselist=False
    )


################################################################################
# OrderState ####################################################################
class OrderState(db.Model):
    __tablename__ = 'orderstate'

    # Properties
    id = db.Column(db.Integer, primary_key=True)

    # Constructors
    @staticmethod
    def from_id(state_id):
        if OrderState.query.filter_by(id=state_id).first():
            return OrderState.query.filter_by(id=state_id).first()
        else:
            return OrderState(id=state_id)
