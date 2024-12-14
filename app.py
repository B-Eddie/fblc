from flask import Flask, request, jsonify
from flask_cors import CORS
from firebase_config import get_database_ref

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Ambulance Booking App API!"})

@app.route("/book", methods=["POST"])
def book_ambulance():
    data = request.json
    user_id = data.get("userId")
    location = data.get("location")
    
    if not user_id or not location:
        return jsonify({"error": "Missing userId or location"}), 400

    bookings_ref = get_database_ref("bookings")
    booking = bookings_ref.push({
        "userId": user_id,
        "location": location,
        "status": "pending"
    })

    return jsonify({"message": "Ambulance booked successfully!", "bookingId": booking.key})

# booking status
@app.route("/status/<user_id>", methods=["GET"])
def get_status(user_id):
    bookings_ref = get_database_ref("bookings")
    bookings = bookings_ref.get()
    user_booking = None

    if bookings:
        for booking_id, booking in bookings.items():
            if booking["userId"] == user_id:
                user_booking = {**booking, "id": booking_id}
                break

    if user_booking:
        return jsonify(user_booking)
    return jsonify({"message": "No bookings found for this user"}), 404

# update booking status
@app.route("/update/<booking_id>", methods=["PATCH"])
def update_status(booking_id):
    data = request.json
    new_status = data.get("status")

    if not new_status:
        return jsonify({"error": "Missing status"}), 400

    booking_ref = get_database_ref(f"bookings/{booking_id}")
    if booking_ref.get():
        booking_ref.update({"status": new_status})
        return jsonify({"message": "Status updated successfully"})
    
    return jsonify({"error": "Booking not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
