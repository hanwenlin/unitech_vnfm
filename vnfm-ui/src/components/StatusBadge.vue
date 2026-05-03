<template>
  <span class="status-badge" :class="stateClass">
    <span class="dot"></span>
    {{ state }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ state: string }>()

const stateClass = computed(() => {
  const map: Record<string, string> = {
    ACTIVE: 'status-active',
    ERROR: 'status-error',
    PROCESSING: 'status-processing',
    SCALING: 'status-processing',
    UPDATING: 'status-processing',
    TERMINATING: 'status-processing',
    PENDING: 'status-pending',
    NOT_INSTANTIATED: 'status-pending',
  }
  return map[props.state] || 'status-pending'
})
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.status-active {
  background: #f0f9eb;
  color: #67c23a;
}
.status-active .dot {
  background: #67c23a;
  animation: breathe 2s infinite;
}
.status-error {
  background: #fde2e2;
  color: #f56c6c;
}
.status-error .dot {
  background: #f56c6c;
  animation: breathe 2s infinite;
}
.status-processing {
  background: #ecf5ff;
  color: #409eff;
}
.status-processing .dot {
  background: #409eff;
  animation: breathe 2s infinite;
}
.status-pending {
  background: #fdf6ec;
  color: #e6a23c;
}
.status-pending .dot {
  background: #e6a23c;
}
@keyframes breathe {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}
</style>
