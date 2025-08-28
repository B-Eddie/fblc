import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useUser } from '../contexts/UserContext';
import database from '@react-native-firebase/database';

export default function StudyTimer() {
  const [time, setTime] = useState(0);
  const [isActive, setIsActive] = useState(false);
  const { user } = useUser();

  useEffect(() => {
    if (!user) return;

    const timerRef = database().ref(`users/${user.uid}/timer`);
    const onValueChange = timerRef.on('value', (snapshot) => {
      const data = snapshot.val();
      if (data) {
        setTime(data.time);
        setIsActive(data.isActive);
      }
    });

    return () => timerRef.off('value', onValueChange);
  }, [user]);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (isActive) {
      interval = setInterval(() => {
        setTime((prevTime) => {
          const newTime = prevTime + 1;
          if (user) {
            database().ref(`users/${user.uid}/timer`).set({
              time: newTime,
              isActive: true
            });
          }
          return newTime;
        });
      }, 1000);
    }

    return () => clearInterval(interval);
  }, [isActive, user]);

  const toggleTimer = () => {
    const newIsActive = !isActive;
    setIsActive(newIsActive);
    if (user) {
      database().ref(`users/${user.uid}/timer`).set({
        time,
        isActive: newIsActive
      });
    }
  };

  const resetTimer = () => {
    setTime(0);
    setIsActive(false);
    if (user) {
      database().ref(`users/${user.uid}/timer`).set({
        time: 0,
        isActive: false
      });
    }
  };

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes
      .toString()
      .padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Study Timer</Text>
      <Text style={styles.time}>{formatTime(time)}</Text>
      <View style={styles.buttonContainer}>
        <TouchableOpacity style={styles.button} onPress={toggleTimer}>
          <Text style={styles.buttonText}>{isActive ? 'Pause' : 'Start'}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.button} onPress={resetTimer}>
          <Text style={styles.buttonText}>Reset</Text>
        </TouchableOpacity>
      </View>
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
  time: {
    fontSize: 48,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 10,
    borderRadius: 5,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
  },
});

