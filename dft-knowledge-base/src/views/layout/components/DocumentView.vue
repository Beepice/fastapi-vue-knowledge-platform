<template>
  <div class="document-view">
    <iframe :src="pdfUrl" class="pdf-iframe"></iframe>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter,useRoute } from 'vue-router'
import { breadcrumb } from '../store'

const router = useRouter()
const route = useRoute()

// 用路由参数拼 PDF 地址
const pdfUrl = computed(() => {
  const token = localStorage.getItem('token')
  return `${import.meta.env.VITE_API_BASE_URL}/api/documents/versions/${route.params.versionId}/documents/${route.params.documentId}/file?token=${token}`
})

onMounted(async () => {
  //面包屑载入
  const s = history.state
  if (s && s.toolName) {
    breadcrumb.value = {
      toolName: s.toolName,
      versionName: s.versionName,
      docTitle: s.docTitle,
      visible: true
    }
  }
})


</script>

<style scoped>
.pdf-iframe {
  width: 100%;
  height: calc(100vh);
  border: none;
}

</style>
