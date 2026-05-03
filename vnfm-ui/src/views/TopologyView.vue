<template>
  <div>
    <h2>VNF 拓扑 - {{ instance?.name }}</h2>
    <div ref="chartRef" style="width: 100%; height: 600px; background: #f5f7fa; border-radius: 8px;" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import api from '../api'

const route = useRoute()
const chartRef = ref<HTMLDivElement>()
const instance = ref<any>(null)

onMounted(async () => {
  const id = route.params.id as string
  const res = await api.get(`/vnflcm/vnf_instances/${id}`)
  instance.value = res.data

  const chart = echarts.init(chartRef.value!)

  // Generate mock topology nodes based on metadata
  const nodes = [
    { id: 'vnf', name: instance.value.name, category: 0, symbolSize: 80 },
    { id: 'vdu1', name: 'VDU-1', category: 1, symbolSize: 50 },
    { id: 'vdu2', name: 'VDU-2', category: 1, symbolSize: 50 },
    { id: 'cp1', name: 'CP-Mgmt', category: 2, symbolSize: 40 },
    { id: 'cp2', name: 'CP-Data', category: 2, symbolSize: 40 },
    { id: 'vl1', name: 'VL-Mgmt', category: 3, symbolSize: 40 },
    { id: 'vl2', name: 'VL-Data', category: 3, symbolSize: 40 },
  ]

  const links = [
    { source: 'vnf', target: 'vdu1' },
    { source: 'vnf', target: 'vdu2' },
    { source: 'vdu1', target: 'cp1' },
    { source: 'vdu1', target: 'cp2' },
    { source: 'vdu2', target: 'cp2' },
    { source: 'cp1', target: 'vl1' },
    { source: 'cp2', target: 'vl2' },
  ]

  chart.setOption({
    tooltip: {},
    legend: { data: ['VNF', 'VDU', 'CP', 'VL'] },
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: nodes,
        links: links,
        categories: [
          { name: 'VNF' },
          { name: 'VDU' },
          { name: 'CP' },
          { name: 'VL' },
        ],
        roam: true,
        label: { show: true },
        force: { repulsion: 300 },
        lineStyle: { color: 'source', curveness: 0.1 },
      },
    ],
  })
})
</script>
