<script setup>
import { ref, nextTick } from 'vue'
import { marked } from 'marked'
import { ChatDotRound, Loading } from '@element-plus/icons-vue'
import axios from 'axios'


const userInput = ref('')
const messages = ref([
  {
    role: 'assistant',
    content: '你好！我是 IC DFT 知识库助手。你可以问我关于 ATPG、Scan Insertion、Fault Simulation 等问题。'
  }
])
const loading = ref(false)
const messageList = ref(null)

marked.use({breaks: true})

function renderMarkdown(text) {
  return marked.parse(text)
}

async function sendQuestion() {
  if (!userInput.value.trim() || loading.value) return

  const question = userInput.value.trim()
  messages.value.push({ role: 'user', content: question })
  userInput.value = ''
    // 创建空的 AI 消息（用来逐步填充）
  messages.value.push({
    role: 'assistant',
    content: ''
  })
  const aiMessageIndex = messages.value.length - 1
  loading.value = true
  scrollToBottom()

  try {
    const response = await fetch(
    `${import.meta.env.VITE_API_BASE_URL}/api/rag/embeddings/question/ask`,
    {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({params:{
          question: question,
          top_k: 5
        }})
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    // ← 读取流式响应
    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
      while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n\n')

      for (const line of lines) {
          const data = line

          // 结束标记
          if (data === '[DONE]') {
            loading.value = false
            scrollToBottom()
            return
          }

          // 追加到 AI 消息
          messages.value[aiMessageIndex].content += data
          scrollToBottom()
      }
    }
    loading.value = false
    scrollToBottom()

  } catch (error) {
    messages.value[aiMessageIndex].content = '抱歉，请求失败：' + error.message
    loading.value = false
    scrollToBottom()
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

function scrollToBottom() {
  nextTick(() => {
    messageList.value?.scrollTo(0, messageList.value.scrollHeight)
  })
}
</script>

<template>
  <div class="ai-rag">
    <!-- 头部 -->
    <div class="rag-header">
      <el-icon><ChatDotRound /></el-icon>
      <span>AI 问答</span>
    </div>
    
    <!-- 消息列表 -->
    <div class="message-list" ref="messageList">
      <div 
        v-for="(msg, index) in messages" 
        :key="index"
        :class="['message', msg.role]"
      >
        <div class="content" v-html="renderMarkdown(msg.content)"></div>
      </div>
      
      <div v-if="loading" class="message assistant loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        思考中...
      </div>
    </div>
    
    <!-- 输入框 -->
    <div class="input-area">
      <el-input
        v-model="userInput"
        type="textarea"
        :rows="2"
        placeholder="输入问题，例如：ATPG 流程是什么？"
        @keyup.enter.ctrl="sendQuestion"
      />
      <el-button 
        type="primary" 
        @click="sendQuestion"
        :loading="loading"
      >
        发送
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.ai-rag {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background: white;
}

.rag-header {
  padding: 16px 24px;
  border-bottom: 1px solid #e4e7ed;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  font-size: 16px;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: #fafafa;
}

.message {
  margin-bottom: 16px;
  max-width: 85%;
}

.message.assistant {
  margin-right: auto;
}

.message.user {
  margin-left: auto;
}

.message .content {
  padding: 12px 16px;
  border-radius: 8px;
  background: white;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  line-height: 1.6;
}

.message.user .content {
  background: #409eff;
  color: white;
}

.message.loading {
  color: #909399;
  display: flex;
  align-items: center;
  gap: 8px;
}

.input-area {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e4e7ed;
  background: white;
}

.input-area .el-input {
  flex: 1;
}

.content :deep(p) {
  margin: 0 0 8px 0;
}

.content :deep(p:last-child) {
  margin-bottom: 0;
}

.content :deep(ul), 
.content :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.content :deep(code) {
  background: #f4f4f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.content :deep(pre) {
  background: #f4f4f5;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
}
</style>
