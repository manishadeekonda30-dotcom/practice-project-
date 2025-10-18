from flask import Flask, render_template, request, redirect, url_for, flash
from database_logic import create_db_connection, setup_initial_schema_and_data, execute_query

app = Flask(__name__)
app.secret_key = 'flight_secret'

# Global DB connection
conn = create_db_connection()
setup_initial_schema_and_data(conn)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/flights')
def view_flights():
    query = "SELECT flight_id, flight_number, departure_airport, arrival_airport, scheduled_departure, scheduled_arrival, status FROM Flights"
    flights = execute_query(conn, query, fetch=True)
    return render_template('flights.html', flights=flights)

@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        flight_id = request.form['flight_id']
        name = request.form['passenger_name']
        seat = request.form['seat_number']
        price = request.form['price']

        query = "INSERT INTO Bookings (flight_id, passenger_name, seat_number, price) VALUES (%s, %s, %s, %s)"
        execute_query(conn, query, (flight_id, name, seat, price))
        flash("Booking successful!", "success")
        return redirect(url_for('view_bookings'))

    # Show flight options for dropdown
    flights = execute_query(conn, "SELECT flight_id, flight_number FROM Flights", fetch=True)
    return render_template('book.html', flights=flights)

@app.route('/bookings')
def view_bookings():
    query = """
    SELECT b.booking_id, f.flight_number, b.passenger_name, b.seat_number, b.price
    FROM Bookings b
    JOIN Flights f ON b.flight_id = f.flight_id
    ORDER BY b.booking_id DESC
    """
    bookings = execute_query(conn, query, fetch=True)
    return render_template('bookings.html', bookings=bookings)

@app.route('/delete_booking/<int:booking_id>')
def delete_booking(booking_id):
    execute_query(conn, "DELETE FROM Bookings WHERE booking_id = %s", (booking_id,))
    flash("Booking deleted.", "info")
    return redirect(url_for('view_bookings'))

@app.route('/update_status', methods=['GET', 'POST'])
def update_status():
    if request.method == 'POST':
        flight_id = request.form['flight_id']
        new_status = request.form['status']
        query = "UPDATE Flights SET status = %s WHERE flight_id = %s"
        execute_query(conn, query, (new_status, flight_id))
        flash("Flight status updated!", "success")
        return redirect(url_for('view_flights'))

    flights = execute_query(conn, "SELECT flight_id, flight_number FROM Flights", fetch=True)
    return render_template('update_status.html', flights=flights)

if __name__ == '__main__':
    app.run(debug=True)
