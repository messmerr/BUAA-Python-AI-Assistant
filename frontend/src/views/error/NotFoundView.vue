<template>
  <div class="not-found">
    <h1>404</h1>
    <p>页面不存在</p>
    <el-button type="primary" @click="$router.push('/')">
      返回首页
    </el-button>
  </div>
</template>

<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  text-align: center;
}

.not-found h1 {
  font-size: 72px;
  color: #409eff;
  margin-bottom: 20px;
}

.not-found p {
  font-size: 18px;
  color: #606266;
  margin-bottom: 30px;
}
</style>
