"use client"

import { motion } from "framer-motion"
import Link from "next/link"
import { ArrowRight, Check } from "lucide-react"
import Layout from "@/components/layout"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/hooks/useAuth"

export default function LandingPage() {
  useAuth(false) // Redirect to dashboard if user is already logged in

  return (
    <Layout requireAuth={false}>
      <div className="flex flex-col items-center justify-center min-h-screen text-center">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-4xl md:text-6xl font-bold text-orange-600 mb-6"
        >
          Welcome to HealthHub Connect
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-xl text-orange-800 mb-8 max-w-2xl"
        >
          Empowering you to take control of your healthcare journey with easy access to services, appointments, and
          community support.
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="flex flex-col md:flex-row gap-4"
        >
          <Button asChild size="lg" className="bg-orange-600 hover:bg-orange-700 text-white">
            <Link href="/auth">
              Get Started <ArrowRight className="ml-2" />
            </Link>
          </Button>
          <Button asChild size="lg" variant="outline" className="border-orange-600 text-orange-600 hover:bg-orange-50">
            <Link href="/about">Learn More</Link>
          </Button>
        </motion.div>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="mt-12 grid md:grid-cols-3 gap-8 text-left"
        >
          {[
            "Easy appointment booking",
            "Cost comparison tools",
            "Telehealth services",
            "Community support groups",
            "Personalized health insights",
            "Secure data protection",
          ].map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.8 + index * 0.1 }}
              className="flex items-center"
            >
              <Check className="text-green-500 mr-2" />
              <span>{feature}</span>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </Layout>
  )
}

