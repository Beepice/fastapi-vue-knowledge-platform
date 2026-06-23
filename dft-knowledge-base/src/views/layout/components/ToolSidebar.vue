<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'


const router = useRouter()
const tools = ref([])       // 工具列表
const loading = ref(false)
const activeToolId = ref(null)
const activeVersionId = ref(null)

// 调用后端接口获取所有工具
onMounted(async () => {
  loading.value = true
  try {
    const res = await request.get('/api/documents/tools')
    tools.value = await res.data
    // 并发请求所有版本（速度快很多
    // 获取版本数据挂到对应工具上）
    const versionPromises = tools.value.map(async (tool) => {
      const verRes = await request.get(`/api/documents/tools/${tool.id}/versions`)
      return { tool_id: tool.id, versionsModel: verRes.data }
    })
    const versionResults = await Promise.all(versionPromises)
    for (const {tool_id, versionsModel } of versionResults) {
      const tool = tools.value.find(t => t.id === tool_id)
      if (tool) tool.versions = versionsModel
    }
  } catch (e) {
    console.error('获取工具列表失败', e)
  } finally {
    loading.value = false
  }
})


// 懒加载：点击版本名 → 加载对应的文档列表页
async function loadDocuments(version) {
  const verRes = await request.get(`/api/documents/versions/${version.id}/documents`)
  version.documents = verRes.data
}

async function openDocuments(tool,version,document){
    router.push({
        path: `/documents/${version.id}/${document.id}`,
        query: { toolName: tool.toolName, versionName: version.toolVersion },
        state: {
        toolName: tool.toolName,
        versionName: version.toolVersion,
        docTitle: document.title
        }
    })
}


const showUploadDialog = ref(false)  // 暂存待上传的文件
const uploadFile = ref(null)
const uploadForm = ref({
  toolName: '',
  versionName: '',
  title: '',
  tags: ''
})
const fileUploadMessage = ref()

// 第1步：文件拖入/选择后，先弹窗
function handleUpload(options) {
  uploadFile.value = options.file    // 暂存文件
  showUploadDialog.value = true      // 弹出表单
}

async function doUpload() {  //上传文件到后端
  try {
  const formData = new FormData()
  formData.append('file', uploadFile.value)
  formData.append('tool_name', uploadForm.value.toolName)
  formData.append('tool_version', uploadForm.value.versionName)
  formData.append('title', uploadForm.value.title)
  formData.append('tags', uploadForm.value.tags)

  await request.post(
  '/api/documents/upload_documents',
  formData,
  )

  ElMessage.success('上传成功！')
  showUploadDialog.value = false
  // 清空表单
  uploadForm.value = { toolName: '', versionName: '', title: '', tags: '' }
  uploadFile.value = null
  // 刷新侧边栏列表...
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('上传失败：' + (error.response?.data?.detail || error.message))
  }
}

</script>

<template>
  <aside class="tool-sidebar">
    <el-menu
      :default-active="activeVersionId"
      class="sidebar-menu"
      style="height: 100%;"
    >
      <!-- 每个 tool 是一个子菜单组 -->
      <el-sub-menu
        v-for="tool in tools"
        :key="tool.id"
        :index="String(tool.id)"
      >
        <template #title>
          <span>{{ tool.toolName }}</span>
        </template>

        <!-- tool 下面的 versions 作为子菜单 -->
        <el-sub-menu
          v-for="version in tool.versions"
          :key="version.id"
          :index="String(version.id)"
          @click="loadDocuments(version)"
        >
          <template #title>
          <span>{{version.toolVersion }}</span>
          </template>
              <!-- versions 下面显示具体文档作为菜单项 -->
            <el-menu-item
              v-for="document in version.documents"
              :key="document.id"
              :index="String(document.id)"
              @click="openDocuments(tool,version,document)"
            >
              {{document.title }}
            </el-menu-item>
        </el-sub-menu>
      </el-sub-menu>
      <!-- 加载中 -->
      <div v-if="loading" class="sidebar-loading">加载中...</div>
    </el-menu>
    <!-- 上传区域 -->
    <div class="upload-area">
      <el-upload
        action=""
        :http-request="handleUpload"
        :show-file-list="false"
        accept=".pdf"
        drag
      >
        <div class="upload-content">
          <span>文档上传</span>
        </div>
      </el-upload>
    </div>
    <!-- 上传表单弹窗 -->
    <el-dialog v-model="showUploadDialog" title="上传文档" width="400px">
    <el-form :model="uploadForm" label-width="80px">
      <el-form-item label="工具名">
        <el-input v-model="uploadForm.toolName" placeholder="如 tssent,synopsys等" />
      </el-form-item>
      <el-form-item label="版本名称">
        <el-input v-model="uploadForm.versionName" placeholder="如 2021.1" />
      </el-form-item>
      <el-form-item label="标题">
        <el-input v-model="uploadForm.title" placeholder="文档标题,取文件名" />
      </el-form-item>
      <el-form-item label="标签">
        <el-input v-model="uploadForm.tags" placeholder="逗号分隔，如 ATPG,BSCAN" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showUploadDialog = false">取消</el-button>
      <el-button type="primary" @click="doUpload">确认上传</el-button>
    </template>
  </el-dialog>
  </aside>
</template>

<style scoped>
.tool-sidebar {
  width: 220px;
  min-width: 220px;
  border-right: 1px solid #e8e8e8;
  background-color: #fafafa;
  overflow-y: auto;
  height: calc(100vh - 60px); /* 减去顶部导航栏高度 */
  position: sticky;
  top: 60px;
  flex-direction: column;
  display:flex;
}

.sidebar-loading {
  padding: 16px;
  text-align: center;
  color: #999;
}
</style>
