<template>
  <div>
    <h2>VIM 管理</h2>
    <el-button type="primary" @click="showCreate = true">添加 VIM</el-button>
    <el-table :data="vims" style="width: 100%; margin-top: 16px" v-loading="loading">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="vim_type" label="类型" />
      <el-table-column prop="vim_url" label="URL" />
      <el-table-column prop="region_name" label="Region" />
      <el-table-column label="默认">
        <template #default="{ row }">
          <el-tag v-if="row.is_default" type="success">是</el-tag>
          <span v-else>否</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showCreate" title="添加 VIM" width="600px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.vim_type" style="width: 100%">
            <el-option label="Kubernetes" value="KUBERNETES" />
            <el-option label="OpenStack" value="OPENSTACK" />
          </el-select>
        </el-form-item>
        <el-form-item label="VIM URL">
          <el-input v-model="form.vim_url" />
        </el-form-item>
        <el-form-item label="Auth URL">
          <el-input v-model="form.auth_url" />
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" />
        </el-form-item>
        <el-form-item label="项目名">
          <el-input v-model="form.project_name" />
        </el-form-item>
        <el-form-item label="Region">
          <el-input v-model="form.region_name" />
        </el-form-item>
        <el-form-item label="默认">
          <el-switch v-model="form.is_default" />
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
import api from '../api'

const loading = ref(false)
const showCreate = ref(false)
const vims = ref<any[]>([])
const form = ref({
  name: '',
  vim_type: 'KUBERNETES',
  vim_url: '',
  auth_url: '',
  username: '',
  password: '',
  project_name: '',
  region_name: '',
  is_default: false,
})

onMounted(async () => {
  loading.value = true
  try {
    await fetchVims()
  } catch (err: any) {
    console.error('VimList load failed', err)
    ElMessage.error(`加载失败: ${err?.response?.data?.detail || err?.message || '未知错误'}`)
  } finally {
    loading.value = false
  }
})

async function fetchVims() {
  const res = await api.get('/vim/vim_auths', { params: { page_size: 1 } })
  vims.value = res.data.items
}

async function submit() {
  await api.post('/vim/vim_auths', form.value)
  ElMessage.success('创建成功')
  showCreate.value = false
  await fetchVims()
}

async function remove(row: any) {
  await ElMessageBox.confirm('确认删除？', '警告', { type: 'warning' })
  await api.delete(`/vim/vim_auths/${row.id}`)
  ElMessage.success('删除成功')
  await fetchVims()
}
</script>
