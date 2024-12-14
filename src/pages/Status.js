import React, { useEffect, useState } from "react";
import { database } from "../firebase";
import { ref, onValue } from "firebase/database";

const Status = ({ user }) => {
  const [status, setStatus] = useState("");

  useEffect(() => {
    const statusRef = ref(database, `bookings`);
    onValue(statusRef, (snapshot) => {
      const data = snapshot.val();
      const userBooking = Object.values(data || {}).find((b) => b.userId === user.uid);
      setStatus(userBooking?.status || "No active booking.");
    });
  }, [user.uid]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white shadow-md rounded-lg p-6 w-96">
        <h2 className="text-2xl font-semibold mb-4 text-center">Ambulance Status</h2>
        <p className="text-lg text-center">{status}</p>
      </div>
    </div>
  );
};

export default Status;
