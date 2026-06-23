import { ref } from 'vue'

// 面包屑数据
export const breadcrumb = ref({
  toolName: '',
  versionName: '',
  docTitle: '',
  // 还有一个标记：当前是否在看文档
  visible: false
})
