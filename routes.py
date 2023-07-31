from os import path
from flask import render_template, send_from_directory, Flask, flash, redirect, url_for, request
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from werkzeug.utils import secure_filename
from sahara import app, bcrypt, mail
from sahara.forms import (RegistrationForm, LoginForm, EditAddressInfoForm, EditPersonalInfoForm,
                          EditPaymentInfoForm, SearchForm, PasswordResetRequestForm,
                          PasswordResetForm, AddBook, AddPromoForm, CheckoutForm, AddToCartForm)
from sahara.models import (Address, PaymentCard, User, Privileges, States, Book, Promotion, Author,
                           Publisher, BookCategory, Categories, Image, CartItem)

####################################################################################################
#                                            CONSTANTS                                             #
####################################################################################################


STATIC_DIR = path.join(app.root_path, 'static')
BOOK_IMAGE_DIR = path.join('/', 'static', 'img', 'books')
SENDER = ("Sahara Devs", app.config['MAIL_USERNAME'])


####################################################################################################
#                                        UTILITY FUNCTIONS                                         #
####################################################################################################

def redirect_to_home():
    return redirect(url_for('home'))


def redirect_if_authenticated():
    if current_user.is_authenticated:
        flash('You cannot access this page as an authenticated user.')
        redirect_to_home()


def redirect_if_not_admin():
    if current_user.privilege.id != Privileges.ADMIN.value:
        flash('You are not authorized to access this page.')
        redirect_to_home()


def send_email(user, subject, body):
    message = Message(subject=subject, sender=SENDER, recipients=[user.email], body=body)
    mail.send(message)


def send_info_changed_email(user):
    body = (
        f'Hello, {user.first_name}!\n'
        '\n'
        'We have recently observed a change in your account information such as your account '
        'password, payment information, shipping address, or first and last name.\n'
        '\n'
        'Thanks for choosing Sahara!\n'
        '\n'
        'Sincerely,\n'
        'The Sahara Team'
    )
    send_email(user, 'Sahara Account Info Change', body)


####################################################################################################
#                                           MAIN ROUTES                                            #
####################################################################################################


################################################################################
# Favicon ######################################################################
@app.route('/favicon.ico')
def favicon():
    """
    I mean... what would Sahara be without the cactus favicon?
    """
    return send_from_directory(STATIC_DIR, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


################################################################################
# Home #########################################################################
@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    """
    Main entry point for this website.
    Renders the "homepage.html" template if it exists, and the demo success page
    "setup_success.html" page otherwise.
    """
    books = Book.get_all()
    almost_gone = Book.search_by_quantity()
    mystery = Book.search_by_category(Categories.MYSTERY.value)

    search_form = SearchForm()
    if path.exists("sahara/templates/homepage.html"):
        return render_template("homepage.html",
                               search_form=search_form,
                               books=books,
                               len=len(books),
                               almost_gone=almost_gone,
                               mystery=mystery,
                               len_myst=len(mystery))
    else:
        return render_template("setup_success.html")


################################################################################
# Book View ####################################################################
@app.route("/book/", defaults={'id': '1'}, methods=['GET', 'POST'])
@app.route("/book/<int:id>", methods=['GET', 'POST'])
def book(id):
    book = Book.get_by_id(id)
    search_form = SearchForm()
    form = AddToCartForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            # Add the book to their cart if they're logged in
            for i in range(0, form.quantity.data):
                current_user.cart.add_book(Book.get_by_id(id))
            flash('This book has been added to your cart!')
        else:
            # Otherwise, ask user to log in
            flash('Please log in or sign up to add this book to your cart')
            return redirect(url_for('login'))

    return render_template('bookPage.html',
                           search_form=search_form,
                           book=book,
                           form=form)


####################################################################################################
#                                           AUTH ROUTES                                            #
####################################################################################################


################################################################################
# Login ########################################################################
@app.route("/login", methods=['GET', 'POST'])
def login():
    """
    On GET: Renders the login form for the user to see.
    On POST: Validates the form and begins the session for the user requested.
    """
    redirect_if_authenticated()
    form = LoginForm()
    search_form = SearchForm()
    if form.validate_on_submit():
        if User.exists(form.email.data):
            user = User.from_email(form.email.data)

            if bcrypt.check_password_hash(user.password, form.password.data):

                if user.privilege.id == Privileges.ADMIN.value:
                    remember_me = form.remember_me.data
                    login_user(user, remember=remember_me)
                    flash(f'Login successful for {form.email.data}!')
                    return redirect(url_for('admin'))
                else:
                    if user.state.id == States.INACTIVE.value:
                        flash('Please verify your account before trying to log in!')
                    elif user.state.id == States.SUSPENDED.value:
                        flash('Your account is currently suspended from the platform.')
                    else:
                        remember_me = form.remember_me.data
                        login_user(user, remember=remember_me)
                        flash(f'Login successful for {form.email.data}!')
                        return redirect(url_for('home'))
            else:
                flash(f'Unsuccesful login. Please try again.')
        else:
            flash(f'Unsuccesful login. Please try again.')

    return render_template('Login.html', form=form, search_form=search_form)


################################################################################
# Register #####################################################################
@app.route("/register", methods=['GET', 'POST'])
def register():
    redirect_if_authenticated()
    form = RegistrationForm()
    search_form = SearchForm()
    if form.validate_on_submit():
        # Hash password
        pass_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # Get address data if applicable
        addr = None
        if form.has_address_info():
            addr = Address(street_1=form.address1.data,
                           street_2=form.address2.data,
                           city=form.city.data,
                           state=form.state.data,
                           zip_code=form.zip_code.data)

        # Get card info
        card_info = []
        if form.has_card_info():
            card_num = bcrypt.generate_password_hash(form.card_num.data).decode('utf-8')

            card_info.append(PaymentCard(
                type=form.ctype.data,
                number=card_num,
                expiration_date=form.expdate.data,
                name_on_card=form.card_name.data,
                security_code=form.sec_code.data,
                last_four_digits=form.card_num.data[-4:]
            ))

        # Add user to database
        user = User(
            email=form.email.data,
            password=pass_hash,
            is_subscribed=form.subscribe.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone_number=form.phone_number.data,
            address=addr,
            payment_cards=card_info,
        )
        user.commit_to_system()

        # Send confirmation email
        token = user.get_timed_token()
        body = (
            f'Welcome to Sahara, {user.first_name}!\n'
            '\n'
            'To validate your account and access our services, please visit the following link '
            'within the next 20 minutes:\n'
            '\n'
            f'{url_for("validate_account", token=token, _external=True)}\n'
            '\n'
            'Thanks for choosing us!\n'
            '\n'
            'Sincerely,\n'
            'The Sahara Team'
        )
        send_email(user, 'Sahara Account Verificaiton', body)

        return redirect(url_for('regconfirm'))

    return render_template('Signup.html', form=form, search_form=search_form)


################################################################################
# Confirm Registration #########################################################
@app.route("/regconfirm", methods=['GET', 'POST'])
def regconfirm():
    redirect_if_authenticated()
    search_form = SearchForm()
    return render_template('registrationConfirm.html', search_form=search_form)


################################################################################
# Validate Account #############################################################
@app.route('/validate/<token>')
def validate_account(token):
    redirect_if_authenticated()
    search_form = SearchForm()
    user = User.from_timed_token(token)

    if user is None:
        flash('This token is expired.')
        return redirect(url_for('home'))

    user.set_user_state(States.ACTIVE.value)
    return render_template("VerifyAccountSuccess.html", search_form=search_form)


################################################################################
# Logout #######################################################################
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've been logged out.")
    return redirect(url_for('home'))


####################################################################################################
#                                         ACCOUNT ROUTES                                           #
####################################################################################################


################################################################################
# Account Home #################################################################
@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    orders = current_user.previous_orders
    search_form = SearchForm()
    return render_template('profile.html',
                           current_user=current_user,
                           search_form=search_form,
                           orders=orders)


################################################################################
# Account Home #################################################################
@app.route("/edit/address", methods=['GET', 'POST'])
@login_required
def edit_address():
    search_form = SearchForm()
    form = EditAddressInfoForm()

    if form.validate_on_submit():
        # Get new address
        new_address = Address(
            street_1=form.address1.data,
            street_2=form.address2.data,
            city=form.city.data,
            state=form.state.data,
            zip_code=form.zip_code.data)

        # Load logged in user
        user = current_user

        # Change logged in user's address
        user.set_address(new_address)

        # Send info change email
        send_info_changed_email(user)

        flash('Address updated!')

        # Redirect to account page
        return redirect(url_for('profile'))

    # Display the form
    # stateNum = current_user.address.state
    if current_user.address:
        form.state.data = current_user.address.state
    return render_template("EditAddress.html",
                           search_form=search_form,
                           form=form,
                           current_user=current_user)


################################################################################
# Edit Payment Info ############################################################
@app.route("/edit/cards", methods=['GET', 'POST'])
@login_required
def edit_payment_cards():
    # See if form has been validated
    form = EditPaymentInfoForm()
    search_form = SearchForm()
    if form.validate_on_submit():
        # Get new payment card
        card_num = bcrypt.generate_password_hash(form.card_num.data).decode('utf-8')
        card = PaymentCard(
            type=form.card_type.data,
            number=card_num,
            expiration_date=form.exp_date.data,
            name_on_card=form.card_name.data,
            security_code=form.sec_code.data,
            last_four_digits=form.card_num.data[-4:]
        )
        current_user.add_payment_card(card)

        # Send info change email
        send_info_changed_email(current_user)

        flash('Payment info updated!')

        # Redirect to account page
        return redirect(url_for('profile'))

    # Display the form
    return render_template('EditPaymentCards.html',
                           search_form=search_form,
                           form=form,
                           current_user=current_user)


################################################################################
# Edit Personal Info ###########################################################
@app.route("/edit/personal_info", methods=['GET', 'POST'])
@login_required
def edit_personal_info():
    # See if form has been validated
    form = EditPersonalInfoForm()
    search_form = SearchForm()
    if form.validate_on_submit():
        # Get new form data
        first_name = form.first_name.data
        last_name = form.last_name.data
        phone_number = form.phone_number.data
        sub_status = form.promotion_subscription.data

        # Load logged in user
        user = current_user

        # Change logged in user's info
        user.set_first_name(first_name, commit=False)
        user.set_last_name(last_name, commit=False)
        user.set_phone_number(phone_number, commit=False)
        user.set_subscription_status(sub_status, commit=True)

        # Send info change email
        send_info_changed_email(user)

        flash('Personal info updated!')

        # Redirect to account page
        return redirect(url_for('profile'))

    # Display the form
    return render_template('EditPersonalInfo.html',
                           search_form=search_form,
                           form=form,
                           current_user=current_user)


################################################################################
# Reset Password Request #######################################################
@app.route("/reset_password_request", methods=['GET', 'POST'])
def reset_password_request():
    search_form = SearchForm()
    # See if form has been validated
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        # Get form data
        email = form.email.data

        # Get user associated with email
        user = User.from_email(email)

        # Get token for user
        token = user.get_timed_token()

        # Send password reset email
        body = (
            f'Hello, {user.first_name}!\n'
            '\n'
            'We have received a request to change the password associated with this account.\n'
            '\n'
            'If you did not make this request, simply ignore this email and nothing will change.'
            'Otherwise, please visit the following link (within the next 20 minutes) to change '
            'your password:\n'
            '\n'
            f'{url_for("reset_password", token=token, _external=True)}\n'
            '\n'
            'Thanks for choosing Sahara!\n'
            '\n'
            'Sincerely,\n'
            'The Sahara Team'
        )
        send_email(user, 'Sahara Password Reset Request', body)

        # Flash message to check email
        flash('A password reset request has been sent to the email specified.')

        if current_user.is_authenticated:
            logout_user()

        return redirect(url_for('login'))

    return render_template('ResetPasswordRequest.html',
                           form=form,
                           search_form=search_form,
                           current_user=current_user)


################################################################################
# Password Reset ###############################################################
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    search_form = SearchForm()

    form = PasswordResetForm()
    if form.validate_on_submit():
        # Get form data
        new_password_hash = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')

        # Get user associated with token
        user = User.from_timed_token(token)

        # If such a user exists, change their password
        if user is None:
            flash('This token is expired.')
            return redirect(url_for('home'))
        else:
            user.set_password(new_password_hash, commit=True)

        # Flash confirmation message
        flash('Password reset! Try logging in.')

        # Send confirmation email
        send_info_changed_email(user)

        return redirect(url_for('login'))

    return render_template('ResetPassword.html', form=form, search_form=search_form)


####################################################################################################
#                                          ADMIN ROUTES                                            #
####################################################################################################


##############################################################################
# Admin Home #################################################################
@app.route("/admin", methods=['GET', 'POST'])
def admin():
    search_form = SearchForm()
    return render_template('adminPage.html', search_form=search_form)


##############################################################################
# Modify Books ###############################################################
@app.route("/books", methods=['GET', 'POST'])
def books():
    books = Book.get_all()
    search_form = SearchForm()
    return render_template('modifyBooks.html', books=books, len=len(books), search_form=search_form)


@app.route("/addBook", methods=['GET', 'POST'])
def addBook():
    redirect_if_not_admin()
    form = AddBook()
    if form.validate_on_submit():

        author_fn = form.author_fname.data
        author_ln = form.author_lname.data
        author = Author.by_name(author_fn, author_ln)

        publisher = Publisher.from_name(form.publisher.data)

        category_to_enum = {
            'action': Categories.ACTION.value,
            'fiction': Categories.FICTION.value,
            'graphic_novel': Categories.GRAPHIC_NOVEL.value,
            'horror': Categories.HORROR.value,
            'mystery': Categories.MYSTERY.value,
            'non_fiction': Categories.NON_FICTION.value,
            'sci_fi': Categories.SCI_FI.value
        }

        book_category = BookCategory.from_id(category_to_enum[form.category.data])

        cover_image = form.cover_image.data
        filename = path.join(
            BOOK_IMAGE_DIR,
            secure_filename(cover_image.filename)
        )

        cover_image.save(path.join(
            STATIC_DIR,
            'img',
            'books',
            secure_filename(cover_image.filename)
        ))

        image = Image.from_filename(filename)

        book = Book(
            isbn=form.isbn.data,
            title=form.title.data,
            edition=form.edition.data,
            description=form.description.data,
            authors=[author],
            publisher=publisher,
            publishing_year=form.publishing_year.data,
            cover_image=image,
            category=book_category,
            price=form.price.data,
            quantity=form.quantity.data,
            rating=form.rating.data
        )
        book.commit_to_system()
        return redirect(url_for('books'))
    search_form = SearchForm()
    return render_template('addBook.html', form=form, search_form=search_form)


@app.route("/promos", methods=['GET', 'POST'])
def promos():
    form = AddPromoForm()
    if form.validate_on_submit():
        new_promo = Promotion(
            code=form.code.data,
            discount=form.discount.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_sent=False
        )
        new_promo.commit_to_system()

        flash('Promotion created!')

    search_form = SearchForm()
    promos = Promotion.get_all()

    return render_template('addPromo.html',
                           search_form=search_form,
                           form=form,
                           promos=promos,
                           len=len(promos))


@app.route("/send_promo/<promo_id>", methods=['GET', 'POST'])
def send_promo(promo_id):
    new_promo = Promotion.from_id(promo_id)

    for user in User.get_all():
        if user.is_subscribed:
            body = (
                f'Hello, {user.first_name}!\n'
                '\n'
                'We have started a new promotion!\n'
                '\n'
                f'Use code {new_promo.code} to get {new_promo.discount}% off of your next '
                'order!'
                '\n'
                '\n'
                f'(Valid from {new_promo.start_date} until {new_promo.end_date})'
                '\n'
                '\n'
                'Thanks for choosing Sahara!\n'
                '\n'
                'Sincerely,\n'
                'The Sahara Team'
            )

            send_email(user, 'Lucky You! New Promo!', body)
    new_promo.send()
    flash('Promotion sent to users!')
    return redirect(url_for('promos'))


@app.route("/delete_promo/<promo_id>", methods=['GET', 'POST'])
def delete_promo(promo_id):
    new_promo = Promotion.from_id(promo_id)
    Promotion.delete(new_promo.id)
    flash('Promotion has been deleted!')
    return redirect(url_for('promos'))


@app.route("/users", methods=['GET', 'POST'])
def users():
    redirect_if_not_admin()
    users = User.get_all()
    search_form = SearchForm()
    return render_template('modifyUsers.html', users=users, len=len(users), search_form=search_form)


@app.route("/suspend_user/<user_id>")
def suspend_user(user_id):
    redirect_if_not_admin()
    user = User.from_id(user_id)
    user.set_user_state(States.SUSPENDED.value)
    return redirect(url_for('users'))


@app.route("/unsuspend_user/<user_id>")
def unsuspend_user(user_id):
    redirect_if_not_admin()
    user = User.from_id(user_id)
    user.set_user_state(States.ACTIVE.value)
    return redirect(url_for('users'))

####################################################################################################
#                                          UNCATEGORIZED                                           #
####################################################################################################


@app.route("/search/", defaults={'term': ''}, methods=['GET', 'POST'])
@app.route("/search/<string:term>", methods=['GET', 'POST'])
def search(term):
    search_form = SearchForm()

    if search_form.validate_on_submit():
        term = request.args.get('term')
        if search_form.search_term.data:
            term = search_form.search_term.data
        else:
            term = ""
        return redirect(url_for("search", term=term))

    results = Book.search(term)

    return render_template('searchResults.html',
                           term=term,
                           search_form=search_form,
                           results=results)


@login_required
@app.route("/cart", methods=['GET', 'POST'])
def cart():
    search_form = SearchForm()
    return render_template('Cart.html',
                           search_form=search_form,
                           current_user=current_user)


@login_required
@app.route('/add_to_cart/<book_id>')
def add_to_cart(book_id):
    book_to_add = Book.get_by_id(book_id)
    current_user.cart.add_book(book_to_add)
    flash('This book has been added to your cart!')
    return redirect(url_for('book', id=book_id))


@login_required
@app.route('/remove_from_cart/<book_id>')
def remove_from_cart(book_id):
    book_to_remove = Book.get_by_id(book_id)

    current_amount = CartItem.from_cart_id(current_user.cart.id, book_to_remove.id).quantity

    for i in range(0, current_amount):
        current_user.cart.remove_book(book_to_remove)

    flash('This book has been removed to your cart!')
    return redirect(url_for('cart'))


@login_required
@app.route('/update_quantity/<book_id>/<new_quantity>')
def update_quantity(book_id, new_quantity):
    book_to_update = Book.get_by_id(book_id)
    cart_item = CartItem.from_cart_id(current_user.cart.id, book_to_update.id)

    new_quantity = int(new_quantity)

    # Get difference btwn old quantity and new one
    difference = cart_item.quantity - new_quantity

    # Update entry to match
    if difference > 0:
        # new quantity is smaller, remove books until it is reached
        while cart_item.quantity > new_quantity:
            current_user.cart.remove_book(book_to_update)

    else:
        # new quantity is larger, add books until it is reached
        while cart_item.quantity < new_quantity:
            current_user.cart.add_book(book_to_update)

    flash('The quantity has been updated!')
    return redirect(url_for('cart'))


@login_required
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    year = ''
    if len(current_user.payment_cards) > 0:
        year = abs(current_user.payment_cards[0].expiration_date.year) % 100

    search_form = SearchForm()
    form = CheckoutForm()
    if current_user.address:
        form.state.data = current_user.address.state
    if current_user.payment_cards:
        form.card_type.data = current_user.payment_cards[0].type
    if form.validate_on_submit():
        # Get address data if applicable
        addr = Address.get_by_info(street_1=form.address1.data,
                                   street_2=form.address2.data,
                                   city=form.city.data,
                                   state=form.state.data,
                                   zip_code=form.zip_code.data)

        # Get card info
        card_num = bcrypt.generate_password_hash(form.card_num.data).decode('utf-8')
        payment_card = PaymentCard(
            type=form.card_type.data,
            number=card_num,
            expiration_date=form.exp_date.data,
            name_on_card=form.card_name.data,
            security_code=form.sec_code.data,
            last_four_digits=form.card_num.data[-4:]
        )

        # Get promo info
        promo = None
        if form.promo_code.data:
            promo = Promotion.from_code(form.promo_code.data)
            flash(f'Promotion accepted! You saved {promo.discount}% on your order')

        for cart_item in current_user.cart.cart_items:
            if cart_item.quantity <= cart_item.book.quantity:
                cart_item.book.quantity -= cart_item.quantity
            else:
                flash('Uh oh! Looks like someone took your book out from under you!\n'
                      f'We only have {cart_item.book.quantity} copies of {cart_item.book.title}\n'
                      ' left to sell.')
                return redirect(url_for('checkout'))

        current_user.confirm_order(
            promotion_applied=promo,
            payment_method=payment_card,
            shipping_addr=addr
        )

        order = current_user.previous_orders[-1]
        cart_items = ''
        for cart_item in order.cart.cart_items:
            res = ''
            res += f'{cart_item.book.title} x{cart_item.quantity}\n'
            price_str = '{:.2f}'.format(cart_item.book.price * cart_item.quantity)
            res += f'${price_str}\n'
            res += f'ISBN: {cart_item.book.isbn}\n\n'
            cart_items += res

        subtotal_str = '{:.2f}'.format(order.cart.subtotal)
        tax_str = '{:.2f}'.format(order.cart.subtotal * 0.07)
        total_str = '{:.2f}'.format(order.total)
        body = (f'Hello, {current_user.first_name}!\n'
                '\n'
                'Thank you for shopping at Sahara! Here is your receipt.\n'
                '\n'
                f'Order ID: {order.id}\n'
                f'Confirmation ID: {current_user.id}{order.id}\n'
                f'Order Date/Time: {order.placed_datetime.strftime("%m/%d/%y - %H:%M")}\n'
                f'Shipping Address: {order.shipping_address}\n'
                '\n'
                f'{cart_items}\n'
                '\n'
                f'Subtotal: ${subtotal_str}\n'
                f'Shipping and Handling: $3.99\n'
                f'Tax: ${tax_str}\n'
                f'Order Total: ${total_str}\n'
                '\n'
                'Thanks for choosing Sahara!\n'
                '\n'
                'Sincerely,\n'
                'The Sahara Team')
        send_email(current_user, 'Purchase Confirmation', body)

        return redirect(url_for('confirmation'))
    return render_template('Checkout.html', form=form, search_form=search_form, year=year)

@app.route("/confirmation/", defaults={'promo_id': '-1'}, methods=['GET', 'POST'])
@app.route("/confirmation/<promo_id>", methods=['GET', 'POST'])
def confirmation(promo_id):
    
    order = current_user.previous_orders[-1]
    promo = order.promotion_applied
    search_form = SearchForm()

    return render_template('OrderConfirmation.html', search_form=search_form, order=order, promo=promo)


@login_required
@app.route('/remove_payment_card/<card_id>')
def remove_payment_card(card_id):
    card = PaymentCard.from_id(card_id)
    if card:
        current_user.remove_payment_card(card)
        flash(f'Your card ending in {card.last_four_digits} has been removed')
    else:
        flash('An error has occured')
    return redirect(url_for('profile'))


@login_required
@app.route('/order_history')
def order_history():
    orders = current_user.previous_orders
    search_form = SearchForm()
    return render_template('orderHistory.html', orders=orders, search_form=search_form)
