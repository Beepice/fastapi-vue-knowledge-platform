<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowDown } from '@element-plus/icons-vue'
import ToolSidebar from './components/ToolSidebar.vue'
import { breadcrumb } from './store.js'


const router = useRouter()
const username = ref('')

onMounted(() => {
  // 从 localStorage 读用户信息
  const userStr = localStorage.getItem('user')

  if (userStr) {
    const user = JSON.parse(userStr)
    username.value = user.username
  }
})

function handleCommand(command) {
  if (command === 'logout') {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }
}
</script>

<template>
  <div class="layout">
    <!-- 顶部导航栏 -->
    <header class="navbar">
    <div class="navbar-left">
        <!-- 用户名 + 下拉菜单 -->
        <el-dropdown trigger="click" @command="handleCommand">
          <span v-if="username" class="user-info">
            {{ username }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <span v-else class="user-info">
            <router-link v-if="!username" to="/login" class="login-link">
            未登录
            </router-link>
          </span>
          <template #dropdown>

            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
    </el-dropdown>
    <!-- 面包屑：只在看文档时显示 -->
    <el-breadcrumb
    v-if="breadcrumb.visible"
    separator="/"
    class="navbar-breadcrumb"
    >
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item v-if="breadcrumb.toolName">
        {{ breadcrumb.toolName }}
      </el-breadcrumb-item>
      <el-breadcrumb-item v-if="breadcrumb.versionName">
        {{ breadcrumb.versionName }}
      </el-breadcrumb-item>
      <el-breadcrumb-item v-if="breadcrumb.docTitle">
        {{ breadcrumb.docTitle }}
      </el-breadcrumb-item>
    </el-breadcrumb>
    <!-- 面包屑结束 -->

    </div>
    <div class="navbar-right">
      <span class="logo">🚀 知识库</span>
    </div>
    </header>
  </div>

    <!-- 下方内容区域 -->
  <main class="content">
      <!-- 左侧工具栏 -->
      <ToolSidebar />

      <!-- 右侧路由出口 -->
      <div class="main-area">
         <router-view />
      </div>
  </main>
</template>


<style scoped>
.layout {
  max-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  height: 40px;
  background-color: #ddddef;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  /* 左右两端撑开,左端最靠左，右端最靠右 */
  justify-content: space-between;
  padding: 0 24px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 999;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 12px;   /* 用户名和面包屑之间的间距 */
}

.logo {
  font-size: 20px;
  font-weight: bold;
}

.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}


.content {
  margin-top: 40px;
  display: flex;
  flex: 1;
}

.main-area {
  flex: 1;
  padding: 0px;
  overflow-y: auto;
}

</style>
