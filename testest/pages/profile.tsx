"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useRouter } from "next/router"
import { motion } from "framer-motion"
import { useAuthState } from "react-firebase-hooks/auth"
import { doc, getDoc, updateDoc } from "firebase/firestore"
import { auth, db } from "@/lib/firebase"
import Layout from "@/components/layout"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function Profile() {
  const [user] = useAuthState(auth)
  const router = useRouter()
  const [name, setName] = useState("")
  const [phone, setPhone] = useState("")
  const [address, setAddress] = useState("")

  useEffect(() => {
    if (user) {
      const fetchUserData = async () => {
        const docRef = doc(db, "users", user.uid)
        const docSnap = await getDoc(docRef)
        if (docSnap.exists()) {
          const data = docSnap.data()
          setName(data.name || "")
          setPhone(data.phone || "")
          setAddress(data.address || "")
        }
      }
      fetchUserData()
    }
  }, [user])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (user) {
      const userRef = doc(db, "users", user.uid)
      await updateDoc(userRef, {
        name,
        phone,
        address,
      })
      router.push("/")
    }
  }

  if (!user) {
    router.push("/auth")
    return null
  }

  return (
    <Layout>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-orange-600">Profile</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-orange-700">
                  Name
                </label>
                <Input id="name" type="text" value={name} onChange={(e) => setName(e.target.value)} className="mt-1" />
              </div>
              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-orange-700">
                  Phone
                </label>
                <Input
                  id="phone"
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="mt-1"
                />
              </div>
              <div>
                <label htmlFor="address" className="block text-sm font-medium text-orange-700">
                  Address
                </label>
                <Input
                  id="address"
                  type="text"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  className="mt-1"
                />
              </div>
              <Button type="submit" className="w-full bg-orange-600 hover:bg-orange-700 text-white">
                Update Profile
              </Button>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </Layout>
  )
}

