import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

const motivationalMessages = [
  "You've got this! Keep pushing forward!",
  "Every minute of study counts. You're making progress!",
  "Stay focused and achieve your goals. You're doing great!",
  "Believe in yourself. You're capable of amazing things!",
  "Your hard work will pay off. Keep going!",
];

export default function MotivationalBot() {
  const [message, setMessage] = useState('');

  const getMotivation = () => {
    const randomIndex = Math.floor(Math.random() * motivationalMessages.length);
    setMessage(motivationalMessages[randomIndex]);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Motivational Bot</Text>
      <View style={styles.messageContainer}>
        {message ? (
          <Text style={styles.message}>{message}</Text>
        ) : (
          <Text style={styles.placeholder}>Tap the button for motivation!</Text>
        )}
      </View>
      <TouchableOpacity style={styles.button} onPress={getMotivation}>
        <Text style={styles.buttonText}>Get Motivation</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: '#fff',
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  messageContainer: {
    height: 100,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  message: {
    fontSize: 18,
    textAlign: 'center',
  },
  placeholder: {
    fontSize: 16,
    color: '#999',
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 10,
    borderRadius: 5,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    textAlign: 'center',
  },
});

