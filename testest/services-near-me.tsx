"use client"

import { useState } from "react"
import { MapPin, Star } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

const sectors = [
  "All Services",
  "Dental",
  "General Checkup",
  "Specialist",
  "Mental Health",
  "Pediatrics",
  "Physical Therapy",
]

const mockServices = [
  { id: 1, name: "City Dental Clinic", type: "Dental", distance: 0.5, rating: 4.5 },
  { id: 2, name: "Family Care Center", type: "General Checkup", distance: 1.2, rating: 4.2 },
  { id: 3, name: "Mind Wellness Therapy", type: "Mental Health", distance: 2.0, rating: 4.8 },
  { id: 4, name: "Pediatric Partners", type: "Pediatrics", distance: 1.5, rating: 4.6 },
  { id: 5, name: "PhysioFit Rehab", type: "Physical Therapy", distance: 0.8, rating: 4.3 },
  { id: 6, name: "Heart Health Specialists", type: "Specialist", distance: 3.0, rating: 4.7 },
]

export default function ServicesNearMe() {
  const [selectedSector, setSelectedSector] = useState("All Services")
  const [sortBy, setSortBy] = useState("distance")

  const filteredServices = mockServices
    .filter((service) => selectedSector === "All Services" || service.type === selectedSector)
    .sort((a, b) => {
      if (sortBy === "distance") return a.distance - b.distance
      if (sortBy === "rating") return b.rating - a.rating
      return 0
    })

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-teal-600">Services Near Me</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <Input type="search" placeholder="Search for services..." className="flex-grow" />
          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="distance">Sort by Distance</SelectItem>
              <SelectItem value="rating">Sort by Rating</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="mb-6 flex flex-wrap gap-2">
          {sectors.map((sector) => (
            <Button
              key={sector}
              variant={selectedSector === sector ? "default" : "outline"}
              onClick={() => setSelectedSector(sector)}
              className="mb-2"
            >
              {sector}
            </Button>
          ))}
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredServices.map((service) => (
            <Card key={service.id}>
              <CardContent className="p-4">
                <h3 className="text-lg font-semibold mb-2">{service.name}</h3>
                <p className="text-sm text-gray-500 mb-2">{service.type}</p>
                <div className="flex justify-between items-center">
                  <span className="flex items-center text-sm">
                    <MapPin className="h-4 w-4 mr-1 text-teal-500" />
                    {service.distance} miles
                  </span>
                  <span className="flex items-center text-sm">
                    <Star className="h-4 w-4 mr-1 text-yellow-400" />
                    {service.rating}
                  </span>
                </div>
                <Button className="w-full mt-4">Book Appointment</Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </div>
  )
}

