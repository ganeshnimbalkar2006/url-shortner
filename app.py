
from flask import Flask, render_template, request, redirect
import mysql.connector
from hashids import Hashids

app = Flask(__name__)

# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'url_shortner'
}

# Initialize Hashids
hashids = Hashids(salt='asdfghjkl', min_length=6)


# Database connection function
def get_db_connection():
    return mysql.connector.connect(**db_config)


# Home route
@app.route("/", methods=['GET', 'POST'])
def Home():

    if request.method == 'POST':

        long_url = request.form['long_url'].strip()

        # Add protocol if missing
        if not long_url.startswith(('http://', 'https://')):
            long_url = 'https://' + long_url

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Insert long URL
            cursor.execute(
                'INSERT INTO url (long_url) VALUES (%s)',
                (long_url,)
            )

            conn.commit()

            # Get inserted ID
            url_id = cursor.lastrowid

            # Generate short code
            short_code = hashids.encode(url_id)

            # Update database
            cursor.execute(
                'UPDATE url SET short_code = %s WHERE id = %s',
                (short_code, url_id)
            )

            conn.commit()

        finally:
            cursor.close()
            conn.close()

        # Generate short URL
        short_url = request.host_url + short_code

        return render_template(
            'index.html',
            short_url=short_url
        )

    return render_template('index.html')


# Redirect route
@app.route('/<short_code>')
def redirect_to_long_url(short_code):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Decode short code
        decoded = hashids.decode(short_code)

        if not decoded:
            return "Invalid short URL", 404

        url_id = decoded[0]

        # Fetch original URL
        cursor.execute(
            'SELECT long_url FROM url WHERE id = %s',
            (url_id,)
        )

        result = cursor.fetchone()

        if result:
            return redirect(result[0])

        return "URL not found", 404

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)
