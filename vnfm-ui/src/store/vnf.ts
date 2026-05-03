import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export interface VnfInstance {
  id: string
  name: string
  description?: string
  vnf_package_id?: string
  vnfd_id: string
  instantiation_state: string
  task_state: string
  vim_id?: string
  tenant_id?: string
  created_at: string
  updated_at: string
}

export interface VnfPackage {
  id: string
  name: string
  description?: string
  vnfd_id: string
  onboarding_state: string
  operational_state: string
  usage_state: string
  created_at: string
}

export const useVnfStore = defineStore('vnf', () => {
  const instances = ref<VnfInstance[]>([])
  const packages = ref<VnfPackage[]>([])
  const total = ref(0)

  async function fetchInstances(page = 1, pageSize = 20) {
    const res = await api.get('/vnflcm/vnf_instances', { params: { page, page_size: pageSize } })
    instances.value = res.data.items
    total.value = res.data.total
  }

  async function fetchPackages(page = 1, pageSize = 20) {
    const res = await api.get('/catalog/vnf_packages', { params: { page, page_size: pageSize } })
    packages.value = res.data.items
    total.value = res.data.total
  }

  return { instances, packages, total, fetchInstances, fetchPackages }
})
