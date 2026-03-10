<template>
  <el-container class="layout-container">

    <!-- 左侧菜单 -->
    <el-aside width="240px" class="aside">
      <div class="logo">
        <div class="logo-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span class="logo-text">RPA 检索系统</span>
      </div>

      <div class="menu-section">
        <div class="menu-label">主导航</div>
        <el-menu router :default-active="$route.path" class="menu">
          <el-menu-item index="/">
            <div class="menu-item-inner">
              <span class="menu-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <rect x="3" y="3" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/>
                  <rect x="14" y="3" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/>
                  <rect x="3" y="14" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/>
                  <rect x="14" y="14" width="7" height="7" rx="1" stroke="currentColor" stroke-width="2"/>
                </svg>
              </span>
              <span>控制台</span>
            </div>
          </el-menu-item>

          <el-menu-item index="/search">
            <div class="menu-item-inner">
              <span class="menu-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
                  <path d="M21 21l-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </span>
              <span>单次检索</span>
            </div>
          </el-menu-item>

          <el-menu-item index="/batch">
            <div class="menu-item-inner">
              <span class="menu-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M4 6h16M4 10h16M4 14h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </span>
              <span>批量任务</span>
            </div>
          </el-menu-item>

          <el-menu-item index="/task">
            <div class="menu-item-inner">
              <span class="menu-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M9 11l3 3L22 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </span>
              <span>任务管理</span>
            </div>
          </el-menu-item>
        </el-menu>
      </div>

      <div class="aside-footer">
        <div class="status-dot"></div>
        <span>系统运行中</span>
      </div>
    </el-aside>

    <!-- 右侧内容 -->
    <el-container class="right-container">
      <el-header class="header">
        <div class="header-left">
          <div class="breadcrumb">基于RPA的百度词条检索系统</div>
        </div>
        <div class="header-right">
          <div class="header-badge">
            <span class="badge-dot"></span>
            RPA 引擎就绪
          </div>
        </div>
      </el-header>

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>

  </el-container>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

* {
  font-family: 'DM Sans', sans-serif;
}

.layout-container {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: #f0f2f5;
}

/* ── 侧栏 ── */
.aside {
  background: #0f1117;
  height: 100vh;
  overflow-y: auto;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-right: none;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 20px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.logo-icon {
  width: 34px;
  height: 34px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.logo-text {
  font-size: 15px;
  font-weight: 600;
  color: #f1f1f1;
  letter-spacing: 0.3px;
}

.menu-section {
  padding: 20px 12px 0;
  flex: 1;
}

.menu-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: rgba(255,255,255,0.25);
  padding: 0 8px;
  margin-bottom: 8px;
}

.menu {
  border-right: none !important;
  background: transparent !important;
}

.menu-item-inner {
  display: flex;
  align-items: center;
  gap: 10px;
}

.menu-icon {
  display: flex;
  align-items: center;
  color: currentColor;
  opacity: 0.7;
}

:deep(.el-menu-item) {
  height: 42px;
  line-height: 42px;
  border-radius: 8px;
  margin-bottom: 2px;
  color: rgba(255,255,255,0.55) !important;
  font-size: 14px;
  font-weight: 400;
  transition: all 0.15s;
}

:deep(.el-menu-item:hover) {
  background: rgba(255,255,255,0.07) !important;
  color: rgba(255,255,255,0.9) !important;
}

:deep(.el-menu-item.is-active) {
  background: rgba(99, 102, 241, 0.18) !important;
  color: #a5b4fc !important;
  font-weight: 500;
}

:deep(.el-menu-item.is-active .menu-icon) {
  opacity: 1;
}

.aside-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255,255,255,0.06);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(255,255,255,0.3);
}

.status-dot {
  width: 7px;
  height: 7px;
  background: #34d399;
  border-radius: 50%;
  box-shadow: 0 0 6px #34d399;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ── 顶栏 ── */
.right-container {
  height: 100vh;
  overflow: hidden;
  flex: 1;
  min-width: 0;
}

.header {
  background: #ffffff;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  border-bottom: 1px solid #e8eaed;
  flex-shrink: 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.breadcrumb {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a2e;
  letter-spacing: -0.2px;
}

.header-badge {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  color: #059669;
  background: #d1fae5;
  padding: 5px 12px;
  border-radius: 20px;
  font-weight: 500;
}

.badge-dot {
  width: 6px;
  height: 6px;
  background: #34d399;
  border-radius: 50%;
}

/* ── 主内容 ── */
.main {
  background: #f5f6fa;
  padding: 0;
  overflow-y: auto;
  height: calc(100vh - 64px);
  flex: 1;
}
</style>