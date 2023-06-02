import csv
from datetime import datetime
import PIL.Image
from os import path
import random
import requests
import sys
from sahara import app
from sahara.routes import STATIC_DIR, BOOK_IMAGE_DIR
from sahara.models import Book, Author, Publisher, Image, BookCategory


def generate_books(num_books=sys.maxsize):
    with open('main_dataset.csv', mode='r') as data_file:
        reader = csv.DictReader(data_file)

        line_count = 0
        for book in reader:
            if line_count > num_books:
                break

            '''
            image,name,author,format,book_depository_stars,price,currency,old_price,isbn,category,img_paths
            '''

            # Get ISBN
            isbn = book['isbn']

            # Get title
            title = book['name']

            # Get edition
            edition = 'Some Edition'

            # Get description
            description = ('Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do '
                           'eiusmod '
                           'tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim '
                           'veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex '
                           'ea commodo consequat. Duis aute irure dolor in reprehenderit in '
                           'voluptate '
                           'velit esse cillum dolore eu fugiat nulla pariatur.')

            # Get author(s)
            author_str = book['author']
            if not author_str or len(author_str.split()) < 2:
                author_str = "Some Author"
            author_dict = author_str.split()
            author_fn = author_dict[0]
            author_ln = author_dict[1]

            author = Author.by_name(author_fn, author_ln)

            # Get publisher
            publisher = Publisher.from_name("Sahara Media")

            # Get publishing year
            publishing_year_int = random.randint(1980, 2021)
            publishing_year = datetime(publishing_year_int, 1, 1)

            # Get cover image
            cover_image = None
            url = book['image']
            with PIL.Image.open(requests.get(url, stream=True).raw) as image_file:
                filename = path.join(
                    BOOK_IMAGE_DIR,
                    url.split('/')[-1]
                )
                image_file.save(path.join(
                    STATIC_DIR,
                    'img',
                    'books',
                    url.split('/')[-1]
                ))
                cover_image = Image.from_filename(filename)

            # Get category
            category_value = random.randint(1, 8)
            category = BookCategory.from_id(category_value)

            # Get price
            price = round(float(book['price']), 2)

            # Get quantity
            quantity = random.randint(10, 101)

            # Get rating
            rating = book['book_depository_stars']

            # Add book to database
            book = Book(
                isbn=isbn,
                title=title,
                edition=edition,
                description=description,
                authors=[author],
                publisher=publisher,
                publishing_year=publishing_year,
                cover_image=cover_image,
                category=category,
                price=price,
                quantity=quantity,
                rating=rating
            )
            book.commit_to_system()

            if num_books != sys.maxsize and line_count > 0:
                book_no = '{:0>2d}'.format(line_count)
                print(f'Generated book {book_no} of {num_books}')
            line_count = line_count + 1
