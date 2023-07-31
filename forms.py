from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileRequired, FileAllowed
from datetime import date
from wtforms import (BooleanField, PasswordField, StringField, SubmitField, DateField,
                     TextAreaField, SelectField, DecimalField, IntegerField, RadioField)
from wtforms.validators import (Email, EqualTo, InputRequired, Length, DataRequired, Optional,
                                ValidationError, NumberRange)
from sahara.models import User, Promotion

####################################################################################################
#                                        UTILITY FUNCTIONS                                         #
####################################################################################################


def raise_validation_error(error_message):
    raise ValidationError(error_message)

####################################################################################################
#                                              FORMS                                               #
####################################################################################################


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    # Constants
    MIN_PASSWORD_LENGTH = 8
    MIN_UNIQUE_CHARACTERS = 5

    # Fields
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    confirm_email = StringField('Confirm Email',
                                validators=[DataRequired(),
                                            Email(),
                                            EqualTo('email', message='Emails must match')])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=10)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(),
                                                 EqualTo('password',
                                                         message='Passwords must match')])
    subscribe = BooleanField('Sign up for our mailing list!')

    address1 = StringField('Address Line 1', validators=[Optional()])
    address2 = StringField('Address Line 2', validators=[Optional()])
    city = StringField('City', validators=[Optional()])
    state = SelectField('State', validators=[Optional()], choices=[
        ("Alabama", "AL"),
        ("Alaska", "AK"),
        ("Arizona", "AZ"),
        ("Arkansas", "AR"),
        ("California", "CA"),
        ("Colorado", "CO"),
        ("Connecticut", "CT"),
        ("Delaware", "DE"),
        ("District of Columbia", "DC"),
        ("Florida", "FL"),
        ("Georgia", "GA"),
        ("Hawaii", "HI"),
        ("Idaho", "ID"),
        ("Illinois", "IL"),
        ("Indiana", "IN"),
        ("Iowa", "IA"),
        ("Kansas", "KS"),
        ("Kentucky", "KY"),
        ("Louisiana", "LA"),
        ("Maine", "ME"),
        ("Montana", "MT"),
        ("Nebraska", "NE"),
        ("Nevada", "NV"),
        ("New Hampshire", "NH"),
        ("New Jersey", "NJ"),
        ("New Mexico", "NM"),
        ("New York", "NY"),
        ("North Carolina", "NC"),
        ("North Dakota", "ND"),
        ("Ohio", "OH"),
        ("Oklahoma", "OK"),
        ("Oregon", "OR"),
        ("Maryland", "MD"),
        ("Massachusetts", "MA"),
        ("Michigan", "MI"),
        ("Minnesota", "MN"),
        ("Mississippi", "MS"),
        ("Missouri", "MO"),
        ("Pennsylvania", "PA"),
        ("Rhode Island", "RI"),
        ("South Carolina", "SC"),
        ("South Dakota", "SD"),
        ("Tennessee", "TN"),
        ("Texas", "TX"),
        ("Utah", "UT"),
        ("Vermont", "VT"),
        ("Virginia", "VA"),
        ("Washington", "WA"),
        ("West Virginia", "WV"),
        ("Wisconsin", "WI"),
        ("Wyoming", "WY")])
    zip_code = StringField('Zip Code', validators=[Optional()])

    ctype = SelectField('Card Type', validators=[Optional()], choices=[
        ('visa', 'VISA'),
        ('mastercard', 'MasterCard'),
        ('amex', 'American Express'),
        ('discover', 'Discover')])
    card_num = StringField('Card Number', validators=[Optional()])
    card_name = StringField('Name On Card', validators=[Optional()])
    expdate = DateField('Expiration Date (MM/YY)', format='%m/%y', validators=[Optional()])
    sec_code = StringField('Security Code', validators=[Optional()])

    submit = SubmitField('Submit')

    def has_address_info(self):
        if self.address1.data:
            return True
        else:
            return False

    def has_card_info(self):
        if self.card_num.data:
            return True
        else:
            return False

    def any_addr_field_filled(self):
        return (self.address1.data or self.address2.data or self.city.data or self.state.data
                or self.zip_code.data)

    def all_addr_fields_filled(self):
        return (self.address1.data and self.city.data and self.state.data
                and self.zip_code.data)

    def any_card_field_filled(self):
        return (self.ctype.data or self.card_num.data or self.card_name.data
                or self.expdate.data or self.sec_code.data)

    def all_card_fields_filled(self):
        return (self.ctype.data and self.card_num.data and self.card_name.data
                and self.expdate.data and self.sec_code.data)

    def validate_email(self, email):
        # Ensure that the email isn't already taken
        msg = 'That email is already taken'
        if User.exists(self.email.data):
            raise ValidationError(msg)

    def validate_password(self, password):
        # Password must contain at least MIN_PASSWORD_LENGTH characters
        msg = f'Password must be at least {self.MIN_PASSWORD_LENGTH} characters long'
        if len(self.password.data) < self.MIN_PASSWORD_LENGTH:
            raise ValidationError(msg)

        # Password must have at least MIN_UNIQUE_CHARACTERS unique characters
        msg = f'Password must contain at least {self.MIN_UNIQUE_CHARACTERS} unique characters'
        if len(''.join(set(self.password.data))) < self.MIN_UNIQUE_CHARACTERS:
            raise ValidationError(msg)

    def validate_phone_number(self, phone_number):
        # Validate phone number
        msg = 'Please provide a valid 10-digit phone number'
        if not self.phone_number.data.isnumeric():
            raise ValidationError(msg)

    def validate_address1(self, address1):
        msg = 'All or no address fields must be filled'
        if self.any_addr_field_filled() and not self.all_addr_fields_filled():
            raise ValidationError(msg)

    def validate_address2(self, address2):
        msg = 'All or no address fields must be filled'
        if self.any_addr_field_filled() and not self.all_addr_fields_filled():
            raise ValidationError(msg)

    def validate_city(self, city):
        msg = 'All or no address fields must be filled'
        if self.any_addr_field_filled() and not self.all_addr_fields_filled():
            raise ValidationError(msg)

    def validate_zip_code(self, zip_code):
        msg = 'All or no address fields must be filled'
        if self.any_addr_field_filled() and not self.all_addr_fields_filled():
            raise ValidationError(msg)

    def validate_card_num(self, card_num):
        msg = 'All or no card fields must be filled'
        if self.any_card_field_filled() and not self.all_card_fields_filled():
            raise ValidationError(msg)

    def validate_card_name(self, card_name):
        msg = 'All or no card fields must be filled'
        if self.any_card_field_filled() and not self.all_card_fields_filled():
            raise ValidationError(msg)

    def validate_exp_date(self, exp_date):
        msg = 'All or no card fields must be filled'
        if self.any_card_field_filled() and not self.all_card_fields_filled():
            raise ValidationError(msg)

        msg = 'Card must not be expired'
        if exp_date.data < date.today():
            raise ValidationError(msg)

    def validate_sec_code(self, sec_code):
        msg = 'All or no card fields must be filled'
        if self.any_card_field_filled() and not self.all_card_fields_filled():
            raise ValidationError(msg)


class EditPersonalInfoForm(FlaskForm):
    first_name = StringField('Firstname', validators=[DataRequired(), Length(min=1, max=20)])
    last_name = StringField('Lastname', validators=[DataRequired(), Length(min=1, max=20)])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    promotion_subscription = BooleanField('Sign up for our mailing list?')
    submit = SubmitField('Submit')


class EditAddressInfoForm(FlaskForm):
    address1 = StringField('Address Line 1', validators=[DataRequired()])
    address2 = StringField('Address Line 2', validators=[Optional()])
    city = StringField('City', validators=[DataRequired()])
    state = SelectField('State', validators=[DataRequired()], choices=[
        ("Alabama", "AL"),
        ("Alaska", "AK"),
        ("Arizona", "AZ"),
        ("Arkansas", "AR"),
        ("California", "CA"),
        ("Colorado", "CO"),
        ("Connecticut", "CT"),
        ("Delaware", "DE"),
        ("District of Columbia", "DC"),
        ("Florida", "FL"),
        ("Georgia", "GA"),
        ("Hawaii", "HI"),
        ("Idaho", "ID"),
        ("Illinois", "IL"),
        ("Indiana", "IN"),
        ("Iowa", "IA"),
        ("Kansas", "KS"),
        ("Kentucky", "KY"),
        ("Louisiana", "LA"),
        ("Maine", "ME"),
        ("Montana", "MT"),
        ("Nebraska", "NE"),
        ("Nevada", "NV"),
        ("New Hampshire", "NH"),
        ("New Jersey", "NJ"),
        ("New Mexico", "NM"),
        ("New York", "NY"),
        ("North Carolina", "NC"),
        ("North Dakota", "ND"),
        ("Ohio", "OH"),
        ("Oklahoma", "OK"),
        ("Oregon", "OR"),
        ("Maryland", "MD"),
        ("Massachusetts", "MA"),
        ("Michigan", "MI"),
        ("Minnesota", "MN"),
        ("Mississippi", "MS"),
        ("Missouri", "MO"),
        ("Pennsylvania", "PA"),
        ("Rhode Island", "RI"),
        ("South Carolina", "SC"),
        ("South Dakota", "SD"),
        ("Tennessee", "TN"),
        ("Texas", "TX"),
        ("Utah", "UT"),
        ("Vermont", "VT"),
        ("Virginia", "VA"),
        ("Washington", "WA"),
        ("West Virginia", "WV"),
        ("Wisconsin", "WI"),
        ("Wyoming", "WY")])
    zip_code = StringField('Zip Code', validators=[DataRequired()])
    submit = SubmitField('Submit')


# TODO add billing addr
class EditPaymentInfoForm(FlaskForm):
    card_type = SelectField('Card Type', validators=[Optional()], choices=[
        ('visa', 'VISA'),
        ('mastercard', 'MasterCard'),
        ('amex', 'American Express'),
        ('discover', 'Discover')])
    card_num = StringField('Card Number', validators=[DataRequired()])
    card_name = StringField('Name On Card', validators=[DataRequired()])
    exp_date = DateField('Expiration Date (MM/YY)', format='%m/%y', validators=[DataRequired()])
    sec_code = StringField('Card Security Code', validators=[DataRequired()])
    submit = SubmitField('Log In')

    def validate_exp_date(self, exp_date):
        msg = 'Card must not be expired'
        if exp_date.data < date.today():
            raise ValidationError(msg)


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password')
    submit = SubmitField('Submit')

    def validate_email(self, email):
        if not User.exists(email.data):
            raise ValidationError("A user with that email does not exist.")

    def validate_password(self, password):
        if current_user.is_authenticated:
            if not bcrypt.check_password_hash(user.password, form.password.data):
                raise ValidationError("Please enter your current password")
            if not password.data:
                raise ValidationError('This field is required')


class PasswordResetForm(FlaskForm):
    new_password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    search_term = StringField('Search Term')
    submitSearch = SubmitField('Search')


class AddBook(FlaskForm):
    isbn = StringField('ISBN', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    edition = StringField('Edition', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    author_fname = StringField('Author', validators=[DataRequired()])
    author_lname = StringField('Author', validators=[DataRequired()])
    publisher = StringField('Publisher', validators=[DataRequired()])
    publishing_year = DateField('Publishing Year', format='%Y', validators=[DataRequired()])
    cover_image = FileField('Cover Image', validators=[FileRequired(), FileAllowed(['jpg', 'png'])])
    category = SelectField('Category',
                           choices=[
                               ('action', 'Action'),
                               ('fiction', 'Fiction'),
                               ('graphic_novel', 'Graphic Novel'),
                               ('horror', 'Horror'),
                               ('mystery', 'Mystery'),
                               ('non_fiction', 'Non-Fiction'),
                               ('sci_fi', 'Sci-Fi')
                           ], validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    rating = DecimalField('Rating', validators=[DataRequired()])
    submit = SubmitField('Add Book')


class AddPromoForm(FlaskForm):
    code = StringField('Promo Code', validators=[DataRequired()])
    discount = IntegerField('Discount %', validators=[DataRequired(), NumberRange(min=0, max=100)])
    start_date = DateField('Starting Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('Ending Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Create Promotion')

    def validate_start_date(self, start_date):
        msg = 'The end date must be later than the start date'
        if self.start_date.data > self.end_date.data:
            raise ValidationError(msg)

        msg = 'You can only add promotions for the future'
        if start_date.data < date.today():
            raise ValidationError(msg)


class CheckoutForm(FlaskForm):
    card_type = SelectField('Card Type', validators=[Optional()], choices=[
        ('visa', 'VISA'),
        ('mastercard', 'MasterCard'),
        ('amex', 'American Express'),
        ('discover', 'Discover')])
    card_num = StringField('Card Number', validators=[DataRequired()])
    card_name = StringField('Name On Card', validators=[DataRequired()])
    exp_date = DateField('Expiration Date (MM/YY)', format='%m/%y', validators=[DataRequired()])
    sec_code = StringField('Card Security Code', validators=[DataRequired()])

    address1 = StringField('Address Line 1', validators=[DataRequired()])
    address2 = StringField('Address Line 2', validators=[Optional()])
    city = StringField('City', validators=[DataRequired()])
    state = SelectField('State', validators=[Optional()], choices=[
        ("Alabama", "AL"),
        ("Alaska", "AK"),
        ("Arizona", "AZ"),
        ("Arkansas", "AR"),
        ("California", "CA"),
        ("Colorado", "CO"),
        ("Connecticut", "CT"),
        ("Delaware", "DE"),
        ("District of Columbia", "DC"),
        ("Florida", "FL"),
        ("Georgia", "GA"),
        ("Hawaii", "HI"),
        ("Idaho", "ID"),
        ("Illinois", "IL"),
        ("Indiana", "IN"),
        ("Iowa", "IA"),
        ("Kansas", "KS"),
        ("Kentucky", "KY"),
        ("Louisiana", "LA"),
        ("Maine", "ME"),
        ("Montana", "MT"),
        ("Nebraska", "NE"),
        ("Nevada", "NV"),
        ("New Hampshire", "NH"),
        ("New Jersey", "NJ"),
        ("New Mexico", "NM"),
        ("New York", "NY"),
        ("North Carolina", "NC"),
        ("North Dakota", "ND"),
        ("Ohio", "OH"),
        ("Oklahoma", "OK"),
        ("Oregon", "OR"),
        ("Maryland", "MD"),
        ("Massachusetts", "MA"),
        ("Michigan", "MI"),
        ("Minnesota", "MN"),
        ("Mississippi", "MS"),
        ("Missouri", "MO"),
        ("Pennsylvania", "PA"),
        ("Rhode Island", "RI"),
        ("South Carolina", "SC"),
        ("South Dakota", "SD"),
        ("Tennessee", "TN"),
        ("Texas", "TX"),
        ("Utah", "UT"),
        ("Vermont", "VT"),
        ("Virginia", "VA"),
        ("Washington", "WA"),
        ("West Virginia", "WV"),
        ("Wisconsin", "WI"),
        ("Wyoming", "WY")])
    zip_code = StringField('Zip Code', validators=[DataRequired()])

    promo_code = StringField('Promo Code:', validators=[Optional()])
    submit = SubmitField('Confirm Order')

    # Validation
    def all_addr_fields_filled(self):
        return (self.address1.data and self.city.data and self.state.data
                and self.zip_code.data)

    def all_card_fields_filled(self):
        return (self.card_type.data and self.card_num.data and self.card_name.data
                and self.exp_date.data and self.sec_code.data)

    def validate_address1(self, address1):
        msg = 'All or no address fields must be filled'
        if not self.all_addr_fields_filled():
            raise ValidationError(msg)

    def validate_address2(self, address2):
        msg = 'All or no address fields must be filled'
        if not self.all_addr_fields_filled():
            raise ValidationError(msg)

    def validate_city(self, city):
        msg = 'All or no address fields must be filled'
        if not self.all_addr_fields_filled():
            raise ValidationError(msg)

    def validate_zip_code(self, zip_code):
        msg = 'All or no address fields must be filled'
        if not self.all_addr_fields_filled():
            raise ValidationError(msg)

    def validate_card_num(self, card_num):
        msg = 'All or no card fields must be filled'
        if not self.all_card_fields_filled():
            raise ValidationError(msg)

        msg = 'Card number must be 16 digits long'
        if len(self.card_num.data) != 16:
            raise ValidationError(msg)

    def validate_card_name(self, card_name):
        msg = 'All or no card fields must be filled'
        if not self.all_card_fields_filled():
            raise ValidationError(msg)

    def validate_exp_date(self, exp_date):
        msg = 'All or no card fields must be filled'
        if not self.all_card_fields_filled():
            raise ValidationError(msg)

        msg = 'Card must not be expired'
        if exp_date.data < date.today():
            raise ValidationError(msg)

    def validate_sec_code(self, sec_code):
        msg = 'All or no card fields must be filled'
        if not self.all_card_fields_filled():
            raise ValidationError(msg)

    def validate_promo_code(self, promo_code):
        if promo_code.data:
            print(promo_code.data)
            msg = 'There are no active promotions with this promo code'
            if not Promotion.exists(promo_code.data):
                print("promo does not exist")
                raise ValidationError(msg)

            promo = Promotion.from_code(promo_code.data)
            if not promo.is_active:
                print("promo is not active")
                raise ValidationError(msg)


class AddToCartForm(FlaskForm):
    quantity = IntegerField('Quantity:', validators=[DataRequired()])
    addToCart = SubmitField('Add to Cart')
