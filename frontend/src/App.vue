<template>
  <div class="app-container">
    <!-- Calculator Card -->
    <div class="calculator-card">
      <div class="display-container">
        <div class="sub-display">{{ subDisplay }}</div>
        <div class="main-display">{{ display || '0' }}</div>
      </div>

      <div class="keypad">
        <button class="btn btn-action" @click="clearDisplay">C</button>
        <button class="btn btn-action" @click="deleteLast">DEL</button>
        <button class="btn btn-operator" @click="appendOperator('%')">%</button>
        <button class="btn btn-operator" @click="appendOperator('/')">/</button>

        <button class="btn" @click="appendNumber('7')">7</button>
        <button class="btn" @click="appendNumber('8')">8</button>
        <button class="btn" @click="appendNumber('9')">9</button>
        <button class="btn btn-operator" @click="appendOperator('*')">×</button>

        <button class="btn" @click="appendNumber('4')">4</button>
        <button class="btn" @click="appendNumber('5')">5</button>
        <button class="btn" @click="appendNumber('6')">6</button>
        <button class="btn btn-operator" @click="appendOperator('-')">-</button>

        <button class="btn" @click="appendNumber('1')">1</button>
        <button class="btn" @click="appendNumber('2')">2</button>
        <button class="btn" @click="appendNumber('3')">3</button>
        <button class="btn btn-operator" @click="appendOperator('+')">+</button>

        <button class="btn btn-zero" @click="appendNumber('0')">0</button>
        <button class="btn" @click="appendNumber('.')">.</button>
        <button class="btn btn-equals" @click="computeResult">=</button>
      </div>
    </div>

    <!-- History Card -->
    <div class="history-card">
      <div class="history-header">
        <h3>Calculation History</h3>
        <button class="btn-clear-history" @click="clearHistory">Clear</button>
      </div>
      <ul class="history-list">
        <li v-if="history.length === 0" class="empty-msg">No history yet</li>
        <li
          v-for="item in history"
          :key="item.id"
          class="history-item"
          @click="useHistory(item)"
        >
          <div class="history-expr">{{ item.expression }} =</div>
          <div class="history-res">{{ item.result }}</div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const API_URL = 'http://localhost:5000/api'

const display = ref('')
const subDisplay = ref('')
const history = ref([])

const appendNumber = (num) => {
  if (display.value === '0' && num !== '.') {
    display.value = num
  } else {
    display.value += num
  }
}

const appendOperator = (op) => {
  if (!display.value && op !== '-') return
  const lastChar = display.value.slice(-1)
  if (['+', '-', '*', '/', '%'].includes(lastChar)) {
    display.value = display.value.slice(0, -1) + op
  } else {
    display.value += op
  }
}

const clearDisplay = () => {
  display.value = ''
  subDisplay.value = ''
}

const deleteLast = () => {
  display.value = display.value.slice(0, -1)
}

const computeResult = async () => {
  if (!display.value) return

  try {
    const res = await fetch(`${API_URL}/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ expression: display.value }),
    })

    const data = await res.json()

    if (!res.ok) {
      alert(data.error || 'Calculation error')
      return
    }

    subDisplay.value = `${display.value} =`
    display.value = data.result.toString()
    await fetchHistory()
  } catch (err) {
    alert('Failed to connect to backend server')
  }
}

const fetchHistory = async () => {
  try {
    const res = await fetch(`${API_URL}/history`)
    if (res.ok) {
      history.value = await res.json()
    }
  } catch (err) {
    console.error('History fetch error:', err)
  }
}

const clearHistory = async () => {
  try {
    await fetch(`${API_URL}/history`, { method: 'DELETE' })
    history.value = []
  } catch (err) {
    alert('Failed to clear history')
  }
}

const useHistory = (item) => {
  display.value = item.result.toString()
  subDisplay.value = `${item.expression} =`
}

const handleKeydown = (e) => {
  if ((e.key >= '0' && e.key <= '9') || e.key === '.') appendNumber(e.key)
  if (['+', '-', '*', '/', '%'].includes(e.key)) appendOperator(e.key)
  if (e.key === 'Enter' || e.key === '=') computeResult()
  if (e.key === 'Backspace') deleteLast()
  if (e.key === 'Escape') clearDisplay()
}

onMounted(() => {
  fetchHistory()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.app-container {
  display: flex;
  gap: 25px;
  max-width: 850px;
  width: 100%;
  flex-wrap: wrap;
  justify-content: center;
}

.calculator-card, .history-card {
  background: #1e293b;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
}

.calculator-card {
  width: 340px;
}

.display-container {
  background: #0f172a;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
  text-align: right;
  min-height: 90px;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
}

.sub-display {
  font-size: 0.9rem;
  color: #94a3b8;
  min-height: 18px;
}

.main-display {
  color: #fff;
  font-size: 2rem;
  font-weight: bold;
  word-break: break-all;
}

.keypad {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.btn {
  background: #334155;
  border: none;
  color: #f8fafc;
  font-size: 1.25rem;
  padding: 16px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn:hover { background: #475569; }
.btn:active { transform: scale(0.96); }

.btn-operator { background: #4f46e5; }
.btn-operator:hover { background: #6366f1; }

.btn-action { background: #e11d48; }
.btn-action:hover { background: #f43f5e; }

.btn-equals { background: #10b981; }
.btn-equals:hover { background: #34d399; }

.history-card {
  width: 320px;
  display: flex;
  flex-direction: column;
  max-height: 480px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  border-bottom: 1px solid #334155;
  padding-bottom: 8px;
}

.btn-clear-history {
  background: transparent;
  color: #ef4444;
  border: 1px solid #ef4444;
  border-radius: 6px;
  padding: 4px 8px;
  cursor: pointer;
  font-size: 0.8rem;
}

.btn-clear-history:hover {
  background: #ef4444;
  color: #fff;
}

.history-list {
  list-style: none;
  overflow-y: auto;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
  background: #0f172a;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.history-item:hover {
  background: #1e293b;
  border: 1px solid #6366f1;
}

.history-expr {
  color: #94a3b8;
  font-size: 0.85rem;
}

.history-res {
  font-size: 1.1rem;
  font-weight: bold;
  color: #10b981;
}

.empty-msg {
  color: #64748b;
  text-align: center;
  margin-top: 20px;
}
</style>
