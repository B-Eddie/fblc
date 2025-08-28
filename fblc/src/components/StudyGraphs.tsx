import React from 'react';
import { View, Text, StyleSheet, Dimensions } from 'react-native';
import { LineChart, BarChart } from 'react-native-chart-kit';

const weeklyData = [
  { day: "Mon", hours: 2 },
  { day: "Tue", hours: 3 },
  { day: "Wed", hours: 5 },
  { day: "Thu", hours: 4 },
  { day: "Fri", hours: 3 },
  { day: "Sat", hours: 6 },
  { day: "Sun", hours: 4 },
];

const monthlyData = [
  { week: "W1", hours: 20 },
  { week: "W2", hours: 25 },
  { week: "W3", hours: 30 },
  { week: "W4", hours: 28 },
];

export default function StudyGraphs() {
  const screenWidth = Dimensions.get('window').width;

  const chartConfig = {
    backgroundGradientFrom: '#ffffff',
    backgroundGradientTo: '#ffffff',
    color: (opacity = 1) => `rgba(64, 93, 230, ${opacity})`,
    strokeWidth: 2,
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Study Progress</Text>
      <Text style={styles.subtitle}>Weekly Progress</Text>
      <BarChart
        data={{
          labels: weeklyData.map(d => d.day),
          datasets: [{ data: weeklyData.map(d => d.hours) }]
        }}
        width={screenWidth - 40}
        height={220}
        yAxisLabel="hrs "
        chartConfig={chartConfig}
        style={styles.chart}
      />
      <Text style={styles.subtitle}>Monthly Progress</Text>
      <LineChart
        data={{
          labels: monthlyData.map(d => d.week),
          datasets: [{ data: monthlyData.map(d => d.hours) }]
        }}
        width={screenWidth - 40}
        height={220}
        yAxisLabel="hrs "
        chartConfig={chartConfig}
        bezier
        style={styles.chart}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: '#fff',
    borderRadius: 10,
    marginHorizontal: 10,
    marginVertical: 10,
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
  subtitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 20,
    marginBottom: 10,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
});

