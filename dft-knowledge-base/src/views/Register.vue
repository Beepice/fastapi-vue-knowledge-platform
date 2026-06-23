<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const email = ref('')
const password = ref('')
const username = ref('')

async function handleRegister() {
  try {
    const response = await request.post(
    '/api/users',
    {
      user: {
        email: email.value,
        username:username.value,
        password: password.value
      }
    })
    // response.data 里就是后端返回的 JWT token 和用户信息
    window.location.href='/login'
  } catch (error) {
    console.error('注册失败:', error.response?.data)
    // error.response.data 里是后端返回的错误信息
  }
}
</script>

<template>
  <div class="login-page">
    <!-- 左侧背景区域 -->
    <div class="left-panel">
      <div class="brand">
        <h1 style="color:white">🌟 DFT 知识库</h1>
        IC 设计与验证技术知识平台
        <p class="desc">集成电路 DFT（可测试性设计）领域专业知识库，涵盖扫描链、BIST、ATPG、边界扫描等核心内容。</p>
      </div>
    </div>

    <!-- 右侧登录区域 -->
    <div class="right-panel">
      <div class="logo" style="position: absolute; top: 70px; right: 40px;">🚀</div>
      <div class="login-form">
        <h2>注册账号</h2>

        <el-form label-position="top" size="large">
          <el-form-item>
            <el-input
              v-model="email"
              placeholder="请输入注册用户邮箱，不要重复注册"
              prefix-icon="User"
            />
          </el-form-item>

          <el-form-item>
            <el-input
              v-model="username"
              type="text"
              placeholder="请输入用户名"
              prefix-icon="User"
            />
          </el-form-item>

          <el-form-item>
            <el-input
              v-model="password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <el-button
            type="primary"
            style="width: 100%; height: 44px; font-size: 16px;"
            @click="handleRegister"
          >注册账号</el-button>
        </el-form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  padding: 150px;
  display: flex;
  height: 70vh;
  background: url('/png/城市背景.png');
}

/* 左侧背景 */
.left-panel {
  width: 45%;
  background: url('/png/深色背景.png') no-repeat center center / cover;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: #fff;
}

.brand h1 {
  font-size: 32px;
  margin-bottom: 16px;
}

.brand > p {
  font-size: 18px;
  opacity: 0.9;
  margin-bottom: 24px;
}

.desc {
  font-size: 14px !important;
  line-height: 1.8;
  opacity: 0.7;
}

/* 右侧登录区 */
.right-panel {
  width: 55%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5ff;
  position: relative !important;
}


.logo {
  font-size: 80px;
  animation: float 3s ease-in-out infinite;
  filter: drop-shadow(0 0 20px rgba(255,255,255,0.3)) brightness(1.1);
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.login-form {
  width: 500px;
  padding: 40px;
}

.login-form h2 {
  text-align: center;
  margin-bottom: 32px;
  color: #445;
  font-size: 32px;
}

.forgot-link {
  color: #409eff;
  text-decoration: none;
}

.register-tip {
  text-align: center;
  margin-top: 20px;
  color: #999;
  font-size: 14px;
}

.register-tip a {
  color: #409eff;
  text-decoration: none;
}
</style>
