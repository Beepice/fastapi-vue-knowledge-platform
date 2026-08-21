<script setup>
import { breadcrumb } from './layout/store.js'
import AIRag from './AIRag.vue'
breadcrumb.value.visible = false
</script>

<template>
  <div class="home">
    <AIRag />
  </div>
</template>

<style scoped>
.home {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}
</style>
