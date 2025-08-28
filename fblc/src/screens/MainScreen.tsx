import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StudyTimer } from '../components/StudyTimer';
import { Leaderboard } from '../components/Leaderboard';
import { TaskManager } from '../components/TaskManager';
import { MotivationalBot } from '../components/MotivationalBot';
import { Chat } from '../components/Chat';
import { StudyGraphs } from '../components/StudyGraphs';
import { useUser } from '../contexts/UserContext';

export default function MainScreen() {
  const [activeTab, setActiveTab] = useState('timer');
  const { user, setUser } = useUser();
  const navigation = useNavigation();

  const handleSignOut = async () => {
    // Implement sign out logic here
    setUser(null);
    navigation.navigate('Home');
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'timer':
        return <StudyTimer />;
      case 'leaderboard':
        return <Leaderboard />;
      case 'tasks':
        return <TaskManager />;
      case 'chat':
        return <Chat />;
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
        <TouchableOpacity onPress={handleSignOut}>
          <Text style={styles.signOutText}>Sign Out</Text>
        </TouchableOpacity>
      </View>
      <Text style={styles.welcomeText}>Welcome, {user?.email}!</Text>
      <View style={styles.tabContainer}>
        {['timer', 'leaderboard', 'tasks', 'chat', 'motivation', 'graphs'].map((tab) => (
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
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#ffffff',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  signOutText: {
    color: '#405DE6',
  },
  welcomeText: {
    fontSize: 16,
    padding: 16,
  },
  tabContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-around',
    padding: 8,
    backgroundColor: '#ffffff',
  },
  tab: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 20,
    marginBottom: 8,
  },
  activeTab: {
    backgroundColor: '#405DE6',
  },
  tabText: {
    color: '#405DE6',
  },
  activeTabText: {
    color: '#ffffff',
  },
});

