"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Bell } from "lucide-react"
import { useAuthState } from "react-firebase-hooks/auth"
import { collection, query, where, onSnapshot } from "firebase/firestore"
import { auth, db } from "@/lib/firebase"

export default function Notifications() {
  const [user] = useAuthState(auth)
  const [notifications, setNotifications] = useState([])

  useEffect(() => {
    if (user) {
      const today = new Date()
      const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)

      const q = query(
        collection(db, "appointments"),
        where("userId", "==", user.uid),
        where("date", ">=", today.toISOString()),
        where("date", "<=", nextWeek.toISOString()),
      )

      const unsubscribe = onSnapshot(q, (querySnapshot) => {
        const notificationsData = querySnapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }))
        setNotifications(notificationsData)
      })

      return () => unsubscribe()
    }
  }, [user])

  return (
    <div className="fixed bottom-4 right-4">
      <AnimatePresence>
        {notifications.map((notification: any) => (
          <motion.div
            key={notification.id}
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="bg-white shadow-lg rounded-lg p-4 mb-2 flex items-center"
          >
            <Bell className="text-orange-500 mr-2" />
            <div>
              <p className="font-semibold text-orange-700">Upcoming Appointment</p>
              <p className="text-sm text-orange-600">
                {notification.doctorName} - {new Date(notification.date).toLocaleString()}
              </p>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}

