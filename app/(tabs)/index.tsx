import React, { useState, useEffect } from 'react';
import { View, Text, Button, TextInput, StyleSheet, FlatList, Alert, TouchableOpacity } from 'react-native';
import { initializeApp } from 'firebase/app';
import { getFirestore, collection, addDoc, getDocs, updateDoc, doc, deleteDoc } from 'firebase/firestore';
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, onAuthStateChanged } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyAVRWpJwugoIxoF7bU-En8-nVkruydQbyo",
  authDomain: "fblc-real.firebaseapp.com",
  projectId: "fblc-real",
  storageBucket: "fblc-real.firebasestorage.app",
  messagingSenderId: "701995629464",
  appId: "1:701995629464:web:dadef7f7515acfe08ac9ed"
};
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const auth = getAuth(app);

const motivationalQuotes = [
  "You're doing great! Keep pushing forward!",
  "Success is the sum of small efforts repeated daily.",
  "Don't watch the clock; do what it does. Keep going!",
  "The future depends on what you do today.",
  "Stay focused and never give up. You're closer than you think!"
];

export default function App() {
  const [studySessions, setStudySessions] = useState([]);
  const [sessionName, setSessionName] = useState('');
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [motivationalMessage, setMotivationalMessage] = useState('');

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const querySnapshot = await getDocs(collection(db, 'sessions'));
      const sessions = querySnapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
      setStudySessions(sessions);
    } catch (error) {
      Alert.alert('Error', 'Unable to fetch sessions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const addSession = async () => {
    if (!sessionName) {
      Alert.alert('Error', 'Please enter a session name.');
      return;
    }

    setLoading(true);
    try {
      const docRef = await addDoc(collection(db, 'sessions'), {
        name: sessionName,
        participants: 1,
        duration: 0,
        leaderboardScore: 0,
        createdAt: new Date(),
        createdBy: user.email,
      });
      setStudySessions((prev) => [...prev, { id: docRef.id, name: sessionName, participants: 1, duration: 0, leaderboardScore: 0, createdBy: user.email }]);
      setSessionName('');
    } catch (error) {
      Alert.alert('Error', 'Unable to add session. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const deleteSession = async (id) => {
    try {
      await deleteDoc(doc(db, 'sessions', id));
      setStudySessions((prev) => prev.filter((session) => session.id !== id));
    } catch (error) {
      Alert.alert('Error', 'Unable to delete session.');
    }
  };

  const incrementScore = async (id) => {
    try {
      const sessionRef = doc(db, 'sessions', id);
      const session = studySessions.find((session) => session.id === id);
      const newScore = (session.leaderboardScore || 0) + 10;
      await updateDoc(sessionRef, { leaderboardScore: newScore });
      setStudySessions((prev) => prev.map((s) => (s.id === id ? { ...s, leaderboardScore: newScore } : s)));
      setMotivationalMessage(motivationalQuotes[Math.floor(Math.random() * motivationalQuotes.length)]);
    } catch (error) {
      Alert.alert('Error', 'Unable to update score.');
    }
  };

  const register = async () => {
    try {
      await createUserWithEmailAndPassword(auth, email, password);
      Alert.alert('Success', 'User registered successfully!');
    } catch (error) {
      Alert.alert('Error', error.message);
    }
  };

  const login = async () => {
    try {
      await signInWithEmailAndPassword(auth, email, password);
      Alert.alert('Success', 'Logged in successfully!');
    } catch (error) {
      Alert.alert('Error', error.message);
    }
  };

  useEffect(() => {
    onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      if (currentUser) fetchSessions();
    });
  }, []);

  if (!user) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>StudySprint - Login</Text>
        <TextInput
          style={styles.input}
          placeholder="Email"
          value={email}
          onChangeText={setEmail}
        />
        <TextInput
          style={styles.input}
          placeholder="Password"
          secureTextEntry
          value={password}
          onChangeText={setPassword}
        />
        <Button title="Login" onPress={login} />
        <Button title="Register" onPress={register} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>StudySprint</Text>
      <Text>Welcome, {user.email}</Text>
      <Text style={styles.motivationalMessage}>{motivationalMessage}</Text>
      <TextInput
        style={styles.input}
        placeholder="Enter session name"
        value={sessionName}
        onChangeText={setSessionName}
      />
      <Button title="Add Session" onPress={addSession} disabled={loading} />
      <FlatList
        data={studySessions.sort((a, b) => b.leaderboardScore - a.leaderboardScore)}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.sessionItem}>
            <Text style={styles.sessionName}>{item.name}</Text>
            <Text>Participants: {item.participants}</Text>
            <Text>Duration: {item.duration} minutes</Text>
            <Text>Score: {item.leaderboardScore}</Text>
            <Text>Created By: {item.createdBy}</Text>
            <Button title="+10 Points" onPress={() => incrementScore(item.id)} />
            <Button title="Delete" onPress={() => deleteSession(item.id)} />
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f8f9fa',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  input: {
    height: 40,
    borderColor: '#ccc',
    borderWidth: 1,
    marginBottom: 20,
    paddingHorizontal: 10,
  },
  sessionItem: {
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#ccc',
  },
  sessionName: {
    fontWeight: 'bold',
    fontSize: 18,
  },
  motivationalMessage: {
    fontStyle: 'italic',
    marginVertical: 10,
    color: '#28a745',
  },
});