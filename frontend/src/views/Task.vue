<template>
  <div class="task-page">

    <!-- 页头 -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-tag">任务管理</div>
        <h2>历史任务</h2>
        <p>查看所有检索任务的执行记录与词条结果</p>
      </div>
      <div class="header-right">
        <div class="filter-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.value"
            class="tab-btn"
            :class="{ active: activeTab === tab.value }"
            @click="activeTab = tab.value"
          >
            {{ tab.label }}
          </button>
        </div>
        <button class="refresh-btn" @click="loadTasks">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
            <path d="M23 4v6h-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M1 20v-6h6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          刷新
        </button>
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="skeleton-list">
      <div v-for="i in 4" :key="i" class="skeleton-item"></div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="filteredTasks.length === 0" class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
        <path d="M9 11l3 3L22 4" stroke="#d1d5db" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" stroke="#d1d5db" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
      <p>暂无{{ activeTab === 'all' ? '' : statusLabelMap[activeTab] }}任务记录</p>
      <router-link to="/search" class="empty-link">去创建第一个任务 →</router-link>
    </div>

    <!-- 任务列表 -->
    <div v-else class="task-list">
      <div
        v-for="task in filteredTasks"
        :key="task.id"
        class="task-card"
        :class="{ expanded: expandedTaskId === task.id }"
      >
        <!-- 任务主行 -->
        <div class="task-main" @click="toggleTask(task.id)">
          <div class="task-left">
            <div class="task-status-dot" :class="task.status"></div>
            <div class="task-info">
              <div class="task-name">{{ task.task_name }}</div>
              <div class="task-meta">
                <span>{{ task.created_at }}</span>
                <span class="meta-sep">·</span>
                <span>共 {{ task.total_count }} 个词条</span>
                <span v-if="task.status === 'running'" class="meta-sep">·</span>
                <span v-if="task.status === 'running'" class="running-hint">
                  正在抓取：{{ task.current_keyword }}
                </span>
              </div>
            </div>
          </div>

          <div class="task-right">
            <!-- 进度条 -->
            <div class="task-progress">
              <div class="progress-bar-wrap">
                <div class="progress-bar" :style="{ width: task.progress + '%' }"></div>
              </div>
              <span class="progress-text">{{ task.progress }}%</span>
            </div>

            <!-- 数量统计 -->
            <div class="task-counts">
              <span class="count-badge success">✓ {{ task.success_count }}</span>
              <span class="count-badge fail">✕ {{ task.failed_count }}</span>
            </div>

            <!-- 状态标签 -->
            <span class="status-badge" :class="task.status">
              {{ statusLabelMap[task.status] || task.status }}
            </span>

            <!-- 操作按钮 -->
            <div class="task-actions" @click.stop>
              <!-- 导出按钮（仅已完成任务显示） -->
              <button
                v-if="task.status === 'completed'"
                class="action-btn export"
                :class="{ loading: exportingId === task.id }"
                :disabled="exportingId === task.id"
                @click="handleExport(task)"
                title="导出 Excel"
              >
                <svg v-if="exportingId !== task.id" width="13" height="13" viewBox="0 0 24 24" fill="none">
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <polyline points="7 10 12 15 17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <line x1="12" y1="15" x2="12" y2="3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
                <svg v-else class="spin" width="13" height="13" viewBox="0 0 24 24" fill="none">
                  <path d="M21 12a9 9 0 11-6.219-8.56" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
                </svg>
              </button>
              <button class="action-btn delete" @click="confirmDelete(task)">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
                  <polyline points="3 6 5 6 21 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M10 11v6M14 11v6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  <path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>

            <!-- 展开箭头 -->
            <svg
              class="expand-arrow"
              :class="{ rotated: expandedTaskId === task.id }"
              width="14" height="14" viewBox="0 0 24 24" fill="none"
            >
              <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>

        <!-- 展开的词条列表 -->
        <transition name="expand">
          <div v-if="expandedTaskId === task.id" class="task-items-wrap">
            <div v-if="itemsLoading" class="items-loading">
              <svg class="spin" width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M21 12a9 9 0 11-6.219-8.56" stroke="#6366f1" stroke-width="2.5" stroke-linecap="round"/>
              </svg>
              加载词条中...
            </div>

            <div v-else-if="taskItemsMap[task.id] && taskItemsMap[task.id].length > 0" class="items-list">
              <div
                v-for="(item, idx) in taskItemsMap[task.id]"
                :key="item.id"
                class="item-row"
                :class="item.status"
              >
                <span class="item-idx">{{ idx + 1 }}</span>
                <div class="item-body">
                  <div class="item-keyword">{{ item.keyword }}</div>
                  <div v-if="item.title" class="item-result">→ {{ item.title }}</div>
                  <div v-if="item.summary" class="item-summary">{{ item.summary }}</div>
                  <div v-if="item.error_msg" class="item-error">{{ item.error_msg }}</div>
                </div>
                <div class="item-right">
                  <a v-if="item.url" :href="item.url" target="_blank" class="item-link" @click.stop>
                    原文 →
                  </a>
                  <span class="item-status" :class="item.status">
                    {{ item.status === 'success' ? '✓ 成功' : item.status === 'failed' ? '✕ 失败' : '等待' }}
                  </span>
                </div>
              </div>
            </div>

            <div v-else class="items-empty">该任务暂无词条记录</div>
          </div>
        </transition>

      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <transition name="modal">
      <div v-if="deleteTarget" class="modal-overlay" @click="deleteTarget = null">
        <div class="modal-box" @click.stop>
          <div class="modal-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="#ef4444" stroke-width="2"/>
              <line x1="12" y1="8" x2="12" y2="12" stroke="#ef4444" stroke-width="2" stroke-linecap="round"/>
              <line x1="12" y1="16" x2="12.01" y2="16" stroke="#ef4444" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="modal-title">确认删除</div>
          <div class="modal-desc">
            即将删除任务「{{ deleteTarget?.task_name }}」及其所有词条记录，此操作不可撤销。
          </div>
          <div class="modal-actions">
            <button class="modal-btn cancel" @click="deleteTarget = null">取消</button>
            <button class="modal-btn confirm" @click="doDelete" :disabled="deleting">
              {{ deleting ? '删除中...' : '确认删除' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getTasks, getTaskItems, deleteTask, exportTask } from '../api/task'

// ── 数据 ──────────────────────────────────────────────────
const tasks        = ref([])
const loading      = ref(true)
const itemsLoading = ref(false)
const expandedTaskId  = ref(null)
const taskItemsMap    = ref({})   // { taskId: [items] }
const deleteTarget    = ref(null)
const deleting        = ref(false)
const exportingId     = ref(null)   // 正在导出的任务 id，用于显示 loading

// ── 筛选 ──────────────────────────────────────────────────
const activeTab = ref('all')
const tabs = [
  { label: '全部',   value: 'all'       },
  { label: '执行中', value: 'running'   },
  { label: '已完成', value: 'completed' },
  { label: '等待中', value: 'pending'   },
]

const statusLabelMap = {
  pending:   '等待中',
  running:   '执行中',
  completed: '已完成',
}

const filteredTasks = computed(() => {
  if (activeTab.value === 'all') return tasks.value
  return tasks.value.filter(t => t.status === activeTab.value)
})

// ── 加载任务列表 ──────────────────────────────────────────
const loadTasks = async () => {
  loading.value = true
  try {
    const res = await getTasks()
    tasks.value = res.data
  } catch (e) {
    console.error('加载任务失败', e)
  } finally {
    loading.value = false
  }
}

// ── 展开 / 收起任务，懒加载词条 ─────────────────────────
const toggleTask = async (taskId) => {
  if (expandedTaskId.value === taskId) {
    expandedTaskId.value = null
    return
  }
  expandedTaskId.value = taskId

  // 已经加载过就不重复请求
  if (taskItemsMap.value[taskId]) return

  itemsLoading.value = true
  try {
    const res = await getTaskItems(taskId)
    taskItemsMap.value[taskId] = res.data
  } catch (e) {
    console.error('加载词条失败', e)
    taskItemsMap.value[taskId] = []
  } finally {
    itemsLoading.value = false
  }
}

// ── 删除 ──────────────────────────────────────────────────
const confirmDelete = (task) => { deleteTarget.value = task }

const doDelete = async () => {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await deleteTask(deleteTarget.value.id)
    tasks.value = tasks.value.filter(t => t.id !== deleteTarget.value.id)
    delete taskItemsMap.value[deleteTarget.value.id]
    if (expandedTaskId.value === deleteTarget.value.id) expandedTaskId.value = null
    deleteTarget.value = null
  } catch (e) {
    console.error('删除失败', e)
  } finally {
    deleting.value = false
  }
}

// ── 导出 ──────────────────────────────────────────────────
const handleExport = async (task) => {
  if (exportingId.value) return
  exportingId.value = task.id
  try {
    await exportTask(task.id, task.task_name)
  } catch (e) {
    console.error('导出失败', e)
    alert('导出失败，请检查后端服务是否正常')
  } finally {
    exportingId.value = null
  }
}

onMounted(loadTasks)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');

.task-page {
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
  gap: 16px;
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
  gap: 10px;
  flex-shrink: 0;
  padding-top: 4px;
}

/* ── 筛选 Tab ── */
.filter-tabs {
  display: flex;
  background: #f3f4f6;
  border-radius: 8px;
  padding: 3px;
  gap: 2px;
}

.tab-btn {
  font-size: 12px;
  font-weight: 600;
  padding: 5px 12px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  transition: all 0.15s;
}

.tab-btn.active {
  background: #fff;
  color: #6366f1;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
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

/* ── 骨架屏 ── */
.skeleton-list { display: flex; flex-direction: column; gap: 10px; }

.skeleton-item {
  height: 72px;
  border-radius: 14px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}

@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ── 空状态 ── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  gap: 12px;
}

.empty-state p {
  font-size: 14px;
  color: #9ca3af;
  margin: 0;
}

.empty-link {
  font-size: 13px;
  color: #6366f1;
  font-weight: 600;
  text-decoration: none;
}

/* ── 任务列表 ── */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-card {
  background: #fff;
  border: 1px solid #e8eaed;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  transition: box-shadow 0.2s;
}

.task-card.expanded {
  border-color: #c4b5fd;
  box-shadow: 0 4px 16px rgba(99,102,241,0.1);
}

/* ── 任务主行 ── */
.task-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  cursor: pointer;
  gap: 16px;
  transition: background 0.15s;
}

.task-main:hover { background: #fafafa; }

.task-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.task-status-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  flex-shrink: 0;
}

.task-status-dot.pending   { background: #d1d5db; }
.task-status-dot.running   { background: #6366f1; box-shadow: 0 0 6px rgba(99,102,241,0.5); animation: pulse 1.2s infinite; }
.task-status-dot.completed { background: #34d399; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.4; }
}

.task-name {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

.task-meta {
  font-size: 12px;
  color: #9ca3af;
  display: flex;
  align-items: center;
  gap: 5px;
}

.meta-sep { color: #d1d5db; }

.running-hint {
  color: #6366f1;
  font-weight: 500;
}

.task-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

/* ── 进度 ── */
.task-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar-wrap {
  width: 80px;
  height: 6px;
  background: #f3f4f6;
  border-radius: 99px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  border-radius: 99px;
  transition: width 0.4s;
}

.progress-text {
  font-size: 12px;
  color: #9ca3af;
  min-width: 32px;
}

/* ── 数量 ── */
.task-counts {
  display: flex;
  gap: 6px;
}

.count-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 7px;
  border-radius: 6px;
}

.count-badge.success { background: #d1fae5; color: #059669; }
.count-badge.fail    { background: #fee2e2; color: #dc2626; }

/* ── 状态标签 ── */
.status-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 6px;
  white-space: nowrap;
}

.status-badge.pending   { background: #f3f4f6; color: #9ca3af; }
.status-badge.running   { background: #ede9fe; color: #6366f1; }
.status-badge.completed { background: #d1fae5; color: #059669; }

/* ── 操作按钮 ── */
.task-actions { display: flex; gap: 4px; }

.action-btn {
  width: 30px;
  height: 30px;
  border-radius: 7px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.action-btn.export {
  background: #eef2ff;
  color: #6366f1;
}

.action-btn.export:hover:not(:disabled) {
  background: #e0e7ff;
}

.action-btn.export:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.action-btn.delete {
  background: #fff0f0;
  color: #dc2626;
}

.action-btn.delete:hover {
  background: #fee2e2;
}

.expand-arrow {
  color: #9ca3af;
  transition: transform 0.2s;
  flex-shrink: 0;
}

.expand-arrow.rotated { transform: rotate(180deg); }

/* ── 词条列表 ── */
.task-items-wrap {
  border-top: 1px solid #f0f0f5;
  padding: 16px 20px;
  background: #fafafa;
}

.items-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  font-size: 13px;
  padding: 8px 0;
}

.items-empty {
  font-size: 13px;
  color: #9ca3af;
  text-align: center;
  padding: 16px 0;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.item-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid #f0f0f5;
  background: #fff;
}

.item-row.success { border-color: #bbf7d0; }
.item-row.failed  { border-color: #fecaca; }

.item-idx {
  font-size: 11px;
  color: #9ca3af;
  min-width: 20px;
  text-align: right;
  padding-top: 2px;
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}

.item-body { flex: 1; min-width: 0; }

.item-keyword {
  font-size: 13px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 2px;
}

.item-result {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 2px;
}

.item-summary {
  font-size: 12px;
  color: #9ca3af;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  display: box;
  line-clamp: 2;
  box-orient: vertical;
}

.item-error {
  font-size: 12px;
  color: #dc2626;
}

.item-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  flex-shrink: 0;
}

.item-link {
  font-size: 11px;
  font-weight: 600;
  color: #6366f1;
  text-decoration: none;
}

.item-link:hover { text-decoration: underline; }

.item-status {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 5px;
}

.item-status.success { background: #d1fae5; color: #059669; }
.item-status.failed  { background: #fee2e2; color: #dc2626; }
.item-status.pending { background: #f3f4f6; color: #9ca3af; }

/* ── 展开动画 ── */
.expand-enter-active, .expand-leave-active {
  transition: all 0.25s ease;
  overflow: hidden;
}
.expand-enter-from, .expand-leave-to {
  opacity: 0;
  max-height: 0;
}
.expand-enter-to, .expand-leave-from {
  opacity: 1;
  max-height: 2000px;
}

/* ── 删除弹窗 ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-box {
  background: #fff;
  border-radius: 18px;
  padding: 32px;
  width: 360px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}

.modal-icon {
  margin-bottom: 14px;
  display: flex;
  justify-content: center;
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  color: #0f1117;
  margin-bottom: 10px;
}

.modal-desc {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.6;
  margin-bottom: 24px;
}

.modal-actions {
  display: flex;
  gap: 10px;
}

.modal-btn {
  flex: 1;
  height: 42px;
  border-radius: 10px;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  transition: all 0.15s;
}

.modal-btn.cancel {
  background: #f3f4f6;
  color: #374151;
}

.modal-btn.cancel:hover { background: #e5e7eb; }

.modal-btn.confirm {
  background: #ef4444;
  color: #fff;
}

.modal-btn.confirm:hover:not(:disabled) { background: #dc2626; }
.modal-btn.confirm:disabled { opacity: 0.6; cursor: not-allowed; }

/* 弹窗动画 */
.modal-enter-active, .modal-leave-active { transition: all 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal-box, .modal-leave-to .modal-box { transform: scale(0.95); }

/* 转圈 */
.spin { animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>