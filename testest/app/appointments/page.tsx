"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { GoogleMap, LoadScript, Marker } from "@react-google-maps/api"
import { useAuth } from "@/hooks/useAuth"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"

// Mock data for healthcare providers
const healthcareProviders = [
  {
    id: 1,
    name: "City General Hospital",
    lat: 40.7128,
    lng: -74.006,
    services: { "General Checkup": 100, "Blood Test": 50 },
  },
  {
    id: 2,
    name: "Downtown Medical Center",
    lat: 40.7282,
    lng: -73.9942,
    services: { "General Checkup": 120, "Blood Test": 60 },
  },
  {
    id: 3,
    name: "Uptown Health Clinic",
    lat: 40.7831,
    lng: -73.9712,
    services: { "General Checkup": 90, "Blood Test": 45 },
  },
]

const mapContainerStyle = {
  width: "100%",
  height: "400px",
}

const center = {
  lat: 40.7128,
  lng: -74.006,
}

export default function AppointmentsPage() {
  useAuth()
  const [selectedProvider, setSelectedProvider] = useState(null)
  const [showPriceComparison, setShowPriceComparison] = useState(false)
  const router = useRouter()

  const handleBookAppointment = (provider) => {
    setSelectedProvider(provider)
  }

  const handleConfirmBooking = () => {
    // Implement booking logic here
    console.log("Booking confirmed for", selectedProvider.name)
    setSelectedProvider(null)
    // Redirect to confirmation page or show confirmation message
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold text-orange-600 mb-6">Book an Appointment</h1>

      <div className="mb-6">
        <LoadScript googleMapsApiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}>
          <GoogleMap mapContainerStyle={mapContainerStyle} center={center} zoom={12}>
            {healthcareProviders.map((provider) => (
              <Marker
                key={provider.id}
                position={{ lat: provider.lat, lng: provider.lng }}
                onClick={() => handleBookAppointment(provider)}
              />
            ))}
          </GoogleMap>
        </LoadScript>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {healthcareProviders.map((provider) => (
          <Card key={provider.id}>
            <CardHeader>
              <CardTitle>{provider.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <Button onClick={() => handleBookAppointment(provider)}>Book Appointment</Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <Dialog open={selectedProvider !== null} onOpenChange={() => setSelectedProvider(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Book Appointment at {selectedProvider?.name}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <label htmlFor="name" className="text-right">
                Name
              </label>
              <Input id="name" className="col-span-3" />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <label htmlFor="date" className="text-right">
                Date
              </label>
              <Input id="date" type="date" className="col-span-3" />
            </div>
          </div>
          <Button onClick={handleConfirmBooking}>Confirm Booking</Button>
        </DialogContent>
      </Dialog>

      <div className="mt-8">
        <Button onClick={() => setShowPriceComparison(true)}>Compare Prices</Button>
      </div>

      <Dialog open={showPriceComparison} onOpenChange={setShowPriceComparison}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Price Comparison</DialogTitle>
          </DialogHeader>
          <table className="w-full">
            <thead>
              <tr>
                <th>Provider</th>
                <th>General Checkup</th>
                <th>Blood Test</th>
              </tr>
            </thead>
            <tbody>
              {healthcareProviders.map((provider) => (
                <tr key={provider.id}>
                  <td>{provider.name}</td>
                  <td>${provider.services["General Checkup"]}</td>
                  <td>${provider.services["Blood Test"]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </DialogContent>
      </Dialog>
    </div>
  )
}

