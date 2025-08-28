import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { useUser } from '../contexts/UserContext';
import auth from '@react-native-firebase/auth';
import StudyTimer from '../components/StudyTimer';
import Leaderboard from '../components/Leaderboard';
import TaskManager from '../components/TaskManager';
import MotivationalBot from '../components/MotivationalBot';
import StudyGraphs from '../components/StudyGraphs';

export default function DashboardScreen() {
  const [activeTab, setActiveTab] = useState('timer');
  const { user } = useUser();

  const handleSignOut = async () => {
    try {
      await auth().signOut();
    } catch (error) {
      console.error('Error signing out: ', error);
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'timer':
        return <StudyTimer />;
      case 'leaderboard':
        return <Leaderboard />;
      case 'tasks':
        return <TaskManager />;
      case 'motivation':
        return <MotivationalBot />;
      case 'graphs':
        return <StudyGraphs />;
      default:
        return null;
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Study Competition Platform</Text>
        <TouchableOpacity style={styles.signOutButton} onPress={handleSignOut}>
          <Text style={styles.signOutButtonText}>Sign Out</Text>
        </TouchableOpacity>
      </View>
      <Text style={styles.welcome}>Welcome, {user?.email}!</Text>
      <View style={styles.tabContainer}>
        {['timer', 'leaderboard', 'tasks', 'motivation', 'graphs'].map((tab) => (
          <TouchableOpacity
            key={tab}
            style={[styles.tab, activeTab === tab && styles.activeTab]}
            onPress={() => setActiveTab(tab)}
          >
            <Text style={[styles.tabText, activeTab === tab && styles.activeTabText]}>
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
      {renderContent()}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  signOutButton: {
    backgroundColor: '#007AFF',
    padding: 10,
    borderRadius: 5,
  },
  signOutButtonText: {
    color: 'white',
  },
  welcome: {
    fontSize: 18,
    marginBottom: 20,
  },
  tabContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  tab: {
    padding: 10,
    borderRadius: 5,
    backgroundColor: '#f0f0f0',
  },
  activeTab: {
    backgroundColor: '#007AFF',
  },
  tabText: {
    color: 'black',
  },
  activeTabText: {
    color: 'white',
  },
});

