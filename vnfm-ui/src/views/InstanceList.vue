<template>
  <div>
    <h2>VNF 实例列表</h2>
    <el-button type="primary" @click="showCreate = true">创建实例</el-button>
    <el-table :data="store.instances" style="width: 100%; margin-top: 16px" v-loading="loading">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="vnfd_id" label="VNFD ID" />
      <el-table-column prop="instantiation_state" label="实例化状态" />
      <el-table-column label="任务状态">
        <template #default="{ row }">
          <StatusBadge :state="row.task_state" />
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" />
      <el-table-column label="操作" width="380">
        <template #default="{ row }">
          <el-button size="small" @click="instantiate(row)" :disabled="row.task_state !== 'PENDING'">实例化</el-button>
          <el-button size="small" @click="terminate(row)" :disabled="row.task_state === 'PENDING' || row.task_state === 'TERMINATING'">终止</el-button>
          <el-button size="small" @click="scale(row)" :disabled="row.task_state !== 'ACTIVE'">扩缩容</el-button>
          <el-button size="small" @click="goTopology(row)">拓扑</el-button>
          <el-button size="small" type="danger" @click="remove(row)" :disabled="row.task_state !== 'PENDING' && row.task_state !== 'ERROR'">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showCreate" title="创建 VNF 实例" width="600px">
      <el-form :model="createForm" label-width="120px">
        <el-form-item label="名称">
          <el-input v-model="createForm.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="VNF 包">
          <el-select v-model="createForm.vnf_package_id" @change="onPackageChange" style="width: 100%">
            <el-option v-for="p in packages" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="VNFD ID">
          <el-input v-model="createForm.vnfd_id" disabled />
        </el-form-item>
        <el-form-item label="VIM">
          <el-select v-model="createForm.vim_id" style="width: 100%">
            <el-option v-for="v in vims" :key="v.id" :label="v.name" :value="v.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="submitCreate">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showScale" title="扩缩容" width="400px">
      <el-form :model="scaleForm" label-width="100px">
        <el-form-item label="类型">
          <el-radio-group v-model="scaleForm.type">
            <el-radio label="scale_out">扩容</el-radio>
            <el-radio label="scale_in">缩容</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showScale = false">取消</el-button>
        <el-button type="primary" @click="submitScale">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useVnfStore } from '../store/vnf'
import api from '../api'
import StatusBadge from '../components/StatusBadge.vue'
import { connectWebSocket, disconnectWebSocket } from '../api/ws'

const router = useRouter()
const store = useVnfStore()
const loading = ref(false)
const showCreate = ref(false)
const showScale = ref(false)
const packages = ref<any[]>([])
const vims = ref<any[]>([])
const currentRow = ref<any>(null)

const createForm = ref({ name: '', description: '', vnf_package_id: '', vnfd_id: '', vim_id: '' })
const scaleForm = ref({ type: 'scale_out' })

onMounted(async () => {
  loading.value = true
  await store.fetchInstances()
  const pkgRes = await api.get('/catalog/vnf_packages', { params: { page_size: 1000 } })
  packages.value = pkgRes.data.items
  const vimRes = await api.get('/vim/vim_auths', { params: { page_size: 1000 } })
  vims.value = vimRes.data.items
  loading.value = false

  connectWebSocket((data) => {
    const idx = store.instances.findIndex((i) => i.id === data.vnf_instance_id)
    if (idx !== -1) {
      store.instances[idx].task_state = data.state
    }
  })
})

onUnmounted(() => {
  disconnectWebSocket()
})

function onPackageChange(pkgId: string) {
  const pkg = packages.value.find((p) => p.id === pkgId)
  if (pkg) {
    createForm.value.vnfd_id = pkg.vnfd_id
  }
}

async function submitCreate() {
  await api.post('/vnflcm/vnf_instances', createForm.value)
  ElMessage.success('创建成功')
  showCreate.value = false
  await store.fetchInstances()
}

async function instantiate(row: any) {
  await ElMessageBox.confirm('确认实例化该 VNF？', '提示')
  await api.post(`/vnflcm/vnf_instances/${row.id}/instantiate`, { params: {} })
  ElMessage.success('实例化指令已下发')
  await store.fetchInstances()
}

async function terminate(row: any) {
  await ElMessageBox.confirm('确认终止该 VNF？', '警告', { type: 'warning' })
  await api.post(`/vnflcm/vnf_instances/${row.id}/terminate`, { params: {} })
  ElMessage.success('终止指令已下发')
  await store.fetchInstances()
}

function scale(row: any) {
  currentRow.value = row
  showScale.value = true
}

async function submitScale() {
  await api.post(`/vnflcm/vnf_instances/${currentRow.value.id}/scale`, { params: scaleForm.value })
  ElMessage.success('扩缩容指令已下发')
  showScale.value = false
  await store.fetchInstances()
}

async function remove(row: any) {
  await ElMessageBox.confirm('确认删除该 VNF 实例？', '警告', { type: 'warning' })
  await api.delete(`/vnflcm/vnf_instances/${row.id}`)
  ElMessage.success('删除成功')
  await store.fetchInstances()
}

function goTopology(row: any) {
  router.push(`/topology/${row.id}`)
}
</script>
