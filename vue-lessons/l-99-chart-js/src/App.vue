<template>
  <header>
    <h1>chart js example</h1>
  </header>

  <main>
    <section class="chart-wrapper">
      <canvas ref="myChart" class="chart"></canvas>
    </section>
  </main>

</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { Chart } from 'chart.js/auto';

const myChart = ref()



onMounted(()=>{
  
    new Chart(myChart.value, {
    type: 'line',
    data: {
      labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
      datasets: [{
        label: '# of Votes',
        data: [12, 19, 3, 5, 2, 3],
        borderWidth: 10
      },
      {
        label: '# of Votes',
        data: [12, 9, 30, 51, 2, 3],
        borderWidth: 10
      }
    ]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
})
</script>



