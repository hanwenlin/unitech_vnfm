<template>
  <div>
    <h2>Dashboard</h2>
    <el-row :gutter="16">
      <el-col :span="6">
        <el-card>
          <div class="stat-label">VNF 实例总数</div>
          <div class="stat-value">{{ stats.total_instances }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-label">运行中</div>
          <div class="stat-value" style="color: #67C23A">{{ stats.active }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-label">异常</div>
          <div class="stat-value" style="color: #F56C6C">{{ stats.error }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-label">处理中</div>
          <div class="stat-value" style="color: #409EFF">{{ stats.processing }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="12">
        <el-card title="状态分布">
          <v-chart :option="pieOption" style="height: 300px" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card title="VIM 健康状态">
          <el-table :data="vims" style="width: 100%">
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="vim_type" label="类型" />
            <el-table-column prop="vim_url" label="URL" />
            <el-table-column label="状态">
              <template #default>
                <el-tag type="success">正常</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import api from '../api'

use([CanvasRenderer, PieChart, TooltipComponent, LegendComponent])

const stats = ref({ total_instances: 0, active: 0, error: 0, processing: 0, pending: 0 })
const vims = ref([])

const pieOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { top: '5%', left: 'center' },
  series: [
    {
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: false, position: 'center' },
      emphasis: { label: { show: true, fontSize: 20, fontWeight: 'bold' } },
      data: [
        { value: stats.value.active, name: 'ACTIVE', itemStyle: { color: '#67C23A' } },
        { value: stats.value.error, name: 'ERROR', itemStyle: { color: '#F56C6C' } },
        { value: stats.value.processing, name: 'PROCESSING', itemStyle: { color: '#409EFF' } },
        { value: stats.value.pending, name: 'PENDING', itemStyle: { color: '#E6A23C' } },
      ],
    },
  ],
}))

onMounted(async () => {
  const res = await api.get('/vnflcm/vnf_instances', { params: { page: 1, page_size: 1000 } })
  const items = res.data.items || []
  stats.value.total_instances = items.length
  stats.value.active = items.filter((i: any) => i.task_state === 'ACTIVE').length
  stats.value.error = items.filter((i: any) => i.task_state === 'ERROR').length
  stats.value.processing = items.filter((i: any) => i.task_state === 'PROCESSING' || i.task_state === 'SCALING' || i.task_state === 'UPDATING').length
  stats.value.pending = items.filter((i: any) => i.task_state === 'PENDING').length

  const vimRes = await api.get('/vim/vim_auths', { params: { page: 1, page_size: 100 } })
  vims.value = vimRes.data.items || []
})
</script>

<style scoped>
.stat-label {
  font-size: 14px;
  color: #606266;
}
.stat-value {
  font-size: 32px;
  font-weight: bold;
  margin-top: 8px;
}
</style>
