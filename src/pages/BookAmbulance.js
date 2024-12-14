import React, { useState } from "react";
import { database } from "../firebase";
import { ref, push } from "firebase/database";

const BookAmbulance = ({ user }) => {
  const [location, setLocation] = useState("");

  const handleBooking = async () => {
    if (!location) {
      alert("Please enter your location!");
      return;
    }
    try {
      await push(ref(database, "bookings"), {
        userId: user.uid,
        location,
        status: "pending",
      });
      alert("Ambulance booked successfully!");
      setLocation("");
    } catch (error) {
      alert("Error booking ambulance: " + error.message);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white shadow-md rounded-lg p-6 w-96">
        <h2 className="text-2xl font-semibold mb-4 text-center">Book an Ambulance</h2>
        <input
          type="text"
          placeholder="Your Location"
          className="w-full border border-gray-300 rounded px-3 py-2 mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
        />
        <button
          onClick={handleBooking}
          className="w-full bg-blue-500 text-white rounded py-2 font-semibold hover:bg-blue-600 transition"
        >
          Book Now
        </button>
      </div>
    </div>
  );
};

export default BookAmbulance;
