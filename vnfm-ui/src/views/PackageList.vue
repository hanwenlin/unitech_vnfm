<template>
  <div>
    <h2>VNF 包管理</h2>
    <el-button type="primary" @click="showCreate = true">上传包</el-button>
    <el-table :data="store.packages" style="width: 100%; margin-top: 16px" v-loading="loading">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="vnfd_id" label="VNFD ID" />
      <el-table-column prop="provider" label="提供商" />
      <el-table-column prop="onboarding_state" label="状态" />
      <el-table-column prop="operational_state" label="运营状态" />
      <el-table-column prop="created_at" label="创建时间" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showCreate" title="创建 VNF 包" width="700px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
        <el-form-item label="VNFD ID">
          <el-input v-model="form.vnfd_id" />
        </el-form-item>
        <el-form-item label="提供商">
          <el-input v-model="form.provider" />
        </el-form-item>
        <el-form-item label="TOSCA 模板">
          <el-input v-model="form.tosca_template" type="textarea" :rows="10" placeholder="粘贴 TOSCA YAML 内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="submit">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useVnfStore } from '../store/vnf'
import api from '../api'

const store = useVnfStore()
const loading = ref(false)
const showCreate = ref(false)
const form = ref({
  name: '',
  description: '',
  vnfd_id: '',
  provider: '',
  tosca_template: '',
})

onMounted(async () => {
  loading.value = true
  await store.fetchPackages()
  loading.value = false
})

async function submit() {
  await api.post('/catalog/vnf_packages', form.value)
  ElMessage.success('创建成功')
  showCreate.value = false
  await store.fetchPackages()
}

async function remove(row: any) {
  await ElMessageBox.confirm('确认删除？', '警告', { type: 'warning' })
  await api.delete(`/catalog/vnf_packages/${row.id}`)
  ElMessage.success('删除成功')
  await store.fetchPackages()
}
</script>
