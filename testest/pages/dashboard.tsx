"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Calendar } from "lucide-react"
import { collection, query, where, getDocs } from "firebase/firestore"

import { db } from "@/lib/firebase"
import Layout from "@/components/layout"
import { useAuth } from "@/hooks/useAuth"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function Dashboard() {
  const { user } = useAuth()
  const [appointments, setAppointments] = useState([])

  useEffect(() => {
    const fetchAppointments = async () => {
      if (user) {
        const q = query(collection(db, "appointments"), where("userId", "==", user.uid))
        const querySnapshot = await getDocs(q)
        setAppointments(querySnapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() })))
      }
    }

    fetchAppointments()
  }, [user])

  return (
    <Layout>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8"
      >
        <Input type="search" placeholder="Search for doctors, services, or health topics..." className="w-full" />
      </motion.div>

      <div className="grid md:grid-cols-2 gap-8">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card className="bg-white shadow-lg border-orange-200">
            <CardHeader>
              <CardTitle className="text-lg font-semibold flex items-center text-orange-700">
                <Calendar className="h-5 w-5 mr-2" />
                Upcoming Appointments
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {appointments.map((appointment: any) => (
                  <motion.li
                    key={appointment.id}
                    className="flex justify-between items-center"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <span>
                      {appointment.doctorName} - {appointment.type}
                    </span>
                    <span className="text-sm text-orange-600">{new Date(appointment.date).toLocaleString()}</span>
                  </motion.li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </motion.div>

        {/* ... (rest of the dashboard content) ... */}
      </div>
    </Layout>
  )
}

