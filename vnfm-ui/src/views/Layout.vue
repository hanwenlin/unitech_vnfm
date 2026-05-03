<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">L-VNFM</div>
      <el-menu :default-active="route.path" router class="menu" background-color="#001529" text-color="#fff" active-text-color="#409EFF">
        <el-menu-item index="/">
          <el-icon><DataAnalysis /></el-icon>
          <span>Dashboard</span>
        </el-menu-item>
        <el-menu-item index="/instances">
          <el-icon><List /></el-icon>
          <span>VNF 实例</span>
        </el-menu-item>
        <el-menu-item index="/packages">
          <el-icon><Box /></el-icon>
          <span>VNF 包</span>
        </el-menu-item>
        <el-menu-item index="/vims">
          <el-icon><OfficeBuilding /></el-icon>
          <span>VIM 管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div style="flex: 1"></div>
        <div class="user-info">
          <span>{{ auth.username }}</span>
          <el-button text size="small" @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  height: 100vh;
}
.aside {
  background: #001529;
  color: #fff;
}
.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: 22px;
  font-weight: bold;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.menu {
  border-right: none;
}
.header {
  display: flex;
  align-items: center;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
