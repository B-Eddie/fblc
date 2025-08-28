import React from 'react';
import { View, Text, Image, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface PostProps {
  post: {
    username: string;
    studyTime: string;
    subject: string;
    imageUrl: string;
  };
}

export default function StudyPost({ post }: PostProps) {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Image
          style={styles.avatar}
          source={{ uri: `https://i.pravatar.cc/150?u=${post.username}` }}
        />
        <Text style={styles.username}>{post.username}</Text>
      </View>
      <Image source={{ uri: post.imageUrl }} style={styles.image} />
      <View style={styles.footer}>
        <View style={styles.actions}>
          <TouchableOpacity>
            <Ionicons name="heart-outline" size={24} color="black" />
          </TouchableOpacity>
          <TouchableOpacity>
            <Ionicons name="chatbubble-outline" size={24} color="black" />
          </TouchableOpacity>
        </View>
        <Text style={styles.caption}>
          Studied {post.subject} for {post.studyTime}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: 'white',
    marginBottom: 10,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    marginRight: 10,
  },
  username: {
    fontWeight: 'bold',
  },
  image: {
    width: '100%',
    height: 400,
  },
  footer: {
    padding: 10,
  },
  actions: {
    flexDirection: 'row',
    marginBottom: 5,
  },
  caption: {
    marginTop: 5,
  },
});

