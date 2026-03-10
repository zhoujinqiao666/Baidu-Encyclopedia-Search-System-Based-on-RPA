<template>
  <div class="dashboard">

    <!-- 页头 -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-tag">控制台</div>
        <h2>系统总览</h2>
        <p>查看系统运行状态与检索数据统计</p>
      </div>
      <div class="header-right">
        <div class="last-update">上次更新：{{ lastUpdate }}</div>
        <button class="refresh-btn" @click="loadStats" :class="{ spinning: loading }">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path d="M23 4v6h-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M1 20v-6h6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          刷新
        </button>
      </div>
    </div>

    <!-- 骨架屏 -->
    <template v-if="loading">
      <div class="stat-cards">
        <div v-for="i in 4" :key="i" class="stat-card skeleton"></div>
      </div>
    </template>

    <!-- 数据已加载 -->
    <template v-else>

      <!-- 统计卡片 -->
      <div class="stat-cards">
        <div class="stat-card">
          <div class="stat-icon blue">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <polyline points="14 2 14 8 20 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="stat-body">
            <div class="stat-num">{{ stats.total_tasks }}</div>
            <div class="stat-label">总任务数</div>
          </div>
          <router-link to="/task" class="stat-link">查看 →</router-link>
        </div>

        <div class="stat-card">
          <div class="stat-icon purple">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
              <path d="M21 21l-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="stat-body">
            <div class="stat-num">{{ stats.total_items }}</div>
            <div class="stat-label">总词条数</div>
          </div>
          <div class="stat-sub">今日 +{{ stats.today_items }}</div>
        </div>

        <div class="stat-card">
          <div class="stat-icon green">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M22 11.08V12a10 10 0 11-5.93-9.14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <polyline points="22 4 12 14.01 9 11.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="stat-body">
            <div class="stat-num">{{ stats.success_items }}</div>
            <div class="stat-label">成功词条</div>
          </div>
          <div class="stat-sub success-rate">成功率 {{ stats.success_rate }}%</div>
        </div>

        <div class="stat-card">
          <div class="stat-icon red">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="stat-body">
            <div class="stat-num">{{ stats.failed_items }}</div>
            <div class="stat-label">失败词条</div>
          </div>
        </div>
      </div>

      <!-- 成功率进度条 -->
      <div class="card rate-card">
        <div class="rate-header">
          <span class="card-label">整体成功率</span>
          <span class="rate-pct">{{ stats.success_rate }}%</span>
        </div>
        <div class="rate-bar-wrap">
          <div class="rate-bar" :style="{ width: stats.success_rate + '%' }"></div>
        </div>
        <div class="rate-legend">
          <span class="legend-item success">
            <span class="legend-dot"></span>成功 {{ stats.success_items }}
          </span>
          <span class="legend-item fail">
            <span class="legend-dot"></span>失败 {{ stats.failed_items }}
          </span>
        </div>
      </div>

      <!-- 快捷入口 + 最近任务 -->
      <div class="bottom-grid">

        <!-- 快捷入口 -->
        <div class="card shortcut-card">
          <div class="card-label">快捷入口</div>
          <div class="shortcuts">
            <router-link to="/search" class="shortcut-item">
              <div class="shortcut-icon blue">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
                  <path d="M21 21l-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <div class="shortcut-info">
                <div class="shortcut-name">单次检索</div>
                <div class="shortcut-desc">搜索单个百科词条</div>
              </div>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" class="shortcut-arrow">
                <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </router-link>

            <router-link to="/batch" class="shortcut-item">
              <div class="shortcut-icon purple">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M4 6h16M4 10h16M4 14h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <div class="shortcut-info">
                <div class="shortcut-name">批量检索</div>
                <div class="shortcut-desc">上传列表批量抓取</div>
              </div>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" class="shortcut-arrow">
                <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </router-link>

            <router-link to="/task" class="shortcut-item">
              <div class="shortcut-icon green">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M9 11l3 3L22 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <div class="shortcut-info">
                <div class="shortcut-name">任务管理</div>
                <div class="shortcut-desc">查看历史检索任务</div>
              </div>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" class="shortcut-arrow">
                <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </router-link>
          </div>
        </div>

        <!-- 最近任务 -->
        <div class="card recent-card">
          <div class="recent-header">
            <div class="card-label">最近任务</div>
            <router-link to="/task" class="view-all">查看全部 →</router-link>
          </div>

          <div v-if="stats.recent_tasks.length === 0" class="recent-empty">
            暂无任务记录
          </div>

          <div v-else class="recent-list">
            <div
              v-for="task in stats.recent_tasks"
              :key="task.id"
              class="recent-item"
            >
              <div class="recent-left">
                <div class="recent-name">{{ task.task_name }}</div>
                <div class="recent-time">{{ task.created_at }}</div>
              </div>
              <div class="recent-right">
                <div class="recent-progress-bar">
                  <div class="recent-progress-fill" :style="{ width: task.progress + '%' }"></div>
                </div>
                <span class="recent-status-badge" :class="task.status">
                  {{ statusLabel(task.status) }}
                </span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </template>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getStats } from '../api/task'

const loading    = ref(true)
const lastUpdate = ref('—')
const stats      = ref({
  total_tasks:   0,
  total_items:   0,
  success_items: 0,
  failed_items:  0,
  today_items:   0,
  success_rate:  0,
  recent_tasks:  []
})

const loadStats = async () => {
  loading.value = true
  try {
    const res = await getStats()
    stats.value  = res.data
    const now    = new Date()
    lastUpdate.value = `${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}:${now.getSeconds().toString().padStart(2,'0')}`
  } catch (e) {
    console.error('加载统计失败', e)
  } finally {
    loading.value = false
  }
}

const statusLabel = (status) => {
  const map = { pending: '等待', running: '执行中', completed: '已完成' }
  return map[status] || status
}

onMounted(loadStats)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');

.dashboard {
  padding: 32px 36px;
  max-width: 1000px;
  font-family: 'DM Sans', sans-serif;
}

/* ── 页头 ── */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
}

.header-tag {
  display: inline-flex;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #6366f1;
  background: #eef2ff;
  padding: 4px 10px;
  border-radius: 6px;
  margin-bottom: 12px;
}

.page-header h2 {
  font-size: 26px;
  font-weight: 700;
  color: #0f1117;
  margin: 0 0 6px;
  letter-spacing: -0.5px;
}

.page-header p {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 4px;
}

.last-update {
  font-size: 12px;
  color: #9ca3af;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #6366f1;
  background: #eef2ff;
  border: none;
  border-radius: 8px;
  padding: 7px 14px;
  cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  transition: all 0.15s;
}

.refresh-btn:hover { background: #e0e7ff; }

.refresh-btn.spinning svg {
  animation: spin 0.6s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ── 统计卡片 ── */
.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.stat-card {
  background: #fff;
  border: 1px solid #e8eaed;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  position: relative;
}

.stat-card.skeleton {
  height: 88px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}

@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.stat-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon.blue   { background: #dbeafe; color: #2563eb; }
.stat-icon.purple { background: #ede9fe; color: #7c3aed; }
.stat-icon.green  { background: #d1fae5; color: #059669; }
.stat-icon.red    { background: #fee2e2; color: #dc2626; }

.stat-body { flex: 1; }

.stat-num {
  font-size: 26px;
  font-weight: 700;
  color: #0f1117;
  letter-spacing: -1px;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #9ca3af;
  font-weight: 500;
}

.stat-link {
  position: absolute;
  top: 14px;
  right: 16px;
  font-size: 12px;
  color: #6366f1;
  text-decoration: none;
  font-weight: 600;
}

.stat-sub {
  position: absolute;
  top: 14px;
  right: 16px;
  font-size: 11px;
  color: #9ca3af;
  font-weight: 500;
}

.stat-sub.success-rate { color: #059669; }

/* ── 卡片基础 ── */
.card {
  background: #fff;
  border: 1px solid #e8eaed;
  border-radius: 16px;
  padding: 22px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  margin-bottom: 16px;
}

.card-label {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #9ca3af;
  margin-bottom: 14px;
}

/* ── 成功率条 ── */
.rate-card { margin-bottom: 16px; }

.rate-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.rate-pct {
  font-size: 20px;
  font-weight: 700;
  color: #059669;
}

.rate-bar-wrap {
  height: 10px;
  background: #fee2e2;
  border-radius: 99px;
  overflow: hidden;
  margin-bottom: 10px;
}

.rate-bar {
  height: 100%;
  background: linear-gradient(90deg, #34d399, #059669);
  border-radius: 99px;
  transition: width 0.8s ease;
}

.rate-legend {
  display: flex;
  gap: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.legend-item.success .legend-dot { background: #34d399; }
.legend-item.fail    .legend-dot { background: #f87171; }

/* ── 底部双栏 ── */
.bottom-grid {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 16px;
}

/* ── 快捷入口 ── */
.shortcuts {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid #f0f0f5;
  background: #fafafa;
  text-decoration: none;
  transition: all 0.15s;
  cursor: pointer;
}

.shortcut-item:hover {
  border-color: #c4b5fd;
  background: #faf5ff;
}

.shortcut-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.shortcut-icon.blue   { background: #dbeafe; color: #2563eb; }
.shortcut-icon.purple { background: #ede9fe; color: #7c3aed; }
.shortcut-icon.green  { background: #d1fae5; color: #059669; }

.shortcut-info { flex: 1; }

.shortcut-name {
  font-size: 13px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 2px;
}

.shortcut-desc {
  font-size: 11px;
  color: #9ca3af;
}

.shortcut-arrow { color: #d1d5db; }

/* ── 最近任务 ── */
.recent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.recent-header .card-label { margin-bottom: 0; }

.view-all {
  font-size: 12px;
  color: #6366f1;
  text-decoration: none;
  font-weight: 600;
}

.recent-empty {
  text-align: center;
  padding: 30px 0;
  color: #9ca3af;
  font-size: 13px;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-radius: 10px;
  background: #fafafa;
  border: 1px solid #f0f0f5;
  gap: 16px;
}

.recent-name {
  font-size: 13px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 220px;
}

.recent-time {
  font-size: 11px;
  color: #9ca3af;
}

.recent-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.recent-progress-bar {
  width: 80px;
  height: 6px;
  background: #f3f4f6;
  border-radius: 99px;
  overflow: hidden;
}

.recent-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  border-radius: 99px;
  transition: width 0.4s;
}

.recent-status-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
  white-space: nowrap;
}

.recent-status-badge.pending   { background: #f3f4f6; color: #9ca3af; }
.recent-status-badge.running   { background: #ede9fe; color: #6366f1; }
.recent-status-badge.completed { background: #d1fae5; color: #059669; }
</style>