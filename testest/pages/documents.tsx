"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useRouter } from "next/router"
import { motion } from "framer-motion"
import { useAuthState } from "react-firebase-hooks/auth"
import { collection, addDoc, query, where, onSnapshot } from "firebase/firestore"
import { ref, uploadBytes, getDownloadURL, deleteObject } from "firebase/storage"
import { auth, db, storage } from "@/lib/firebase"
import Layout from "@/components/layout"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function Documents() {
  const [user] = useAuthState(auth)
  const router = useRouter()
  const [file, setFile] = useState<File | null>(null)
  const [documents, setDocuments] = useState([])

  useEffect(() => {
    if (user) {
      const q = query(collection(db, "documents"), where("userId", "==", user.uid))
      const unsubscribe = onSnapshot(q, (querySnapshot) => {
        const documentsData = querySnapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }))
        setDocuments(documentsData)
      })

      return () => unsubscribe()
    }
  }, [user])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (file && user) {
      const storageRef = ref(storage, `documents/${user.uid}/${file.name}`)
      await uploadBytes(storageRef, file)
      const downloadURL = await getDownloadURL(storageRef)

      await addDoc(collection(db, "documents"), {
        userId: user.uid,
        name: file.name,
        url: downloadURL,
        createdAt: new Date().toISOString(),
      })

      setFile(null)
    }
  }

  const handleDelete = async (docId: string, fileName: string) => {
    if (user) {
      const storageRef = ref(storage, `documents/${user.uid}/${fileName}`)
      await deleteObject(storageRef)
      await db.collection("documents").doc(docId).delete()
    }
  }

  if (!user) {
    router.push("/auth")
    return null
  }

  return (
    <Layout>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-orange-600">Medical Documents</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4">
              <Input type="file" onChange={handleFileChange} />
              <Button
                onClick={handleUpload}
                disabled={!file}
                className="mt-2 bg-orange-600 hover:bg-orange-700 text-white"
              >
                Upload Document
              </Button>
            </div>
            <ul className="space-y-2">
              {documents.map((doc: any) => (
                <motion.li
                  key={doc.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex justify-between items-center bg-white p-2 rounded shadow"
                >
                  <a
                    href={doc.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-orange-600 hover:underline"
                  >
                    {doc.name}
                  </a>
                  <Button onClick={() => handleDelete(doc.id, doc.name)} variant="destructive">
                    Delete
                  </Button>
                </motion.li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </motion.div>
    </Layout>
  )
}

