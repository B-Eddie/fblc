"use client"

import type React from "react"
import Link from "next/link"
import { useRouter } from "next/router"
import { motion } from "framer-motion"
import { Home, MapPin, Calendar, DollarSign, Users, Video, LogOut } from "lucide-react"
import { auth } from "@/lib/firebase"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/hooks/useAuth"

const navItems = [
  { icon: Home, label: "Dashboard", href: "/" },
  { icon: MapPin, label: "Services Near Me", href: "/services-near-me" },
  { icon: Calendar, label: "Appointments", href: "/appointments" },
  { icon: DollarSign, label: "Cost Compare", href: "/cost-compare" },
  { icon: Users, label: "Community", href: "/community" },
  { icon: Video, label: "Telehealth", href: "/telehealth" },
]

export default function Layout({ children, requireAuth = true }: { children: React.ReactNode; requireAuth?: boolean }) {
  const { user, loading } = useAuth(requireAuth)
  const router = useRouter()

  const handleLogout = () => {
    auth.signOut()
    router.push("/")
  }

  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>
  }

  return (
    <div className="min-h-screen bg-orange-50">
      <motion.header
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="bg-white shadow-md"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold text-orange-600">
            HealthHub Connect
          </Link>
          <nav>
            <ul className="flex space-x-4">
              {user &&
                navItems.map((item) => (
                  <motion.li key={item.href} whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
                    <Link href={item.href} className="text-orange-600 hover:text-orange-800 flex items-center">
                      <item.icon className="h-5 w-5 mr-1" />
                      <span className="hidden md:inline">{item.label}</span>
                    </Link>
                  </motion.li>
                ))}
              {user ? (
                <motion.li whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
                  <Button onClick={handleLogout} variant="ghost" className="text-orange-600 hover:text-orange-800">
                    <LogOut className="h-5 w-5 mr-1" />
                    <span className="hidden md:inline">Logout</span>
                  </Button>
                </motion.li>
              ) : (
                <motion.li whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
                  <Link href="/auth" className="text-orange-600 hover:text-orange-800 flex items-center">
                    <LogOut className="h-5 w-5 mr-1" />
                    <span className="hidden md:inline">Login</span>
                  </Link>
                </motion.li>
              )}
            </ul>
          </nav>
        </div>
      </motion.header>

      <motion.main
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
      >
        {children}
      </motion.main>

      <motion.footer
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="bg-orange-100 mt-auto"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 text-center text-orange-600">
          © 2023 HealthHub Connect. All rights reserved.
        </div>
      </motion.footer>
    </div>
  )
}

