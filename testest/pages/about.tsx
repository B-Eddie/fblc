"use client"

import { motion } from "framer-motion"
import Layout from "@/components/layout"

export default function About() {
  return (
    <Layout requireAuth={false}>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="max-w-4xl mx-auto"
      >
        <h1 className="text-3xl font-bold text-orange-600 mb-6">About HealthHub Connect</h1>
        <p className="text-lg text-orange-800 mb-4">
          HealthHub Connect is a comprehensive healthcare platform designed to empower patients and improve access to
          quality healthcare services.
        </p>
        {/* Add more content about the platform, its features, and benefits */}
      </motion.div>
    </Layout>
  )
}

