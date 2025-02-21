"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Calendar, DollarSign, Users, Bell } from "lucide-react"
import { useAuthState } from "react-firebase-hooks/auth"
import { collection, query, where, onSnapshot } from "firebase/firestore"

import { auth, db } from "@/lib/firebase"
import Layout from "@/components/layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function Dashboard() {
  const [user] = useAuthState(auth)
  const [appointments, setAppointments] = useState([])

  useEffect(() => {
    if (user) {
      const q = query(collection(db, "appointments"), where("userId", "==", user.uid))
      const unsubscribe = onSnapshot(q, (querySnapshot) => {
        const appointmentsData = querySnapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }))
        setAppointments(appointmentsData)
      })

      return () => unsubscribe()
    }
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

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card className="bg-white shadow-lg border-orange-200">
            <CardHeader>
              <CardTitle className="text-lg font-semibold flex items-center text-orange-700">
                <DollarSign className="h-5 w-5 mr-2" />
                Cost Comparison
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                <motion.li
                  className="flex justify-between items-center"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <span>Annual Physical</span>
                  <span className="font-semibold text-orange-600">$50 - $200</span>
                </motion.li>
                <motion.li
                  className="flex justify-between items-center"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <span>Dental Cleaning</span>
                  <span className="font-semibold text-orange-600">$75 - $150</span>
                </motion.li>
              </ul>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="md:col-span-2"
        >
          <Card className="bg-white shadow-lg border-orange-200">
            <CardHeader>
              <CardTitle className="text-lg font-semibold flex items-center text-orange-700">
                <Users className="h-5 w-5 mr-2" />
                Community Support
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid sm:grid-cols-2 gap-4">
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button
                    variant="outline"
                    className="w-full justify-start border-orange-300 text-orange-700 hover:bg-orange-100"
                  >
                    <Users className="h-4 w-4 mr-2" />
                    Join Diabetes Support Group
                  </Button>
                </motion.div>
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button
                    variant="outline"
                    className="w-full justify-start border-orange-300 text-orange-700 hover:bg-orange-100"
                  >
                    <Bell className="h-4 w-4 mr-2" />
                    Volunteer as Health Advocate
                  </Button>
                </motion.div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </Layout>
  )
}

