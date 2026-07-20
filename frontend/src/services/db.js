import { openDB } from 'idb'

const DB_VERSION = 2
const STORE_API_CACHE = 'api-cache'
const STORE_SYNC_QUEUE = 'sync-queue'
const STORE_REMINDERS = 'reminders'

const getDBName = () => {
  const token = localStorage.getItem('agrisense_token')
  if (!token) return 'agrisense-db-default'
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
    }).join(''))
    const payload = JSON.parse(jsonPayload)
    const username = payload.sub || 'default'
    return `agrisense-db-${username}`
  } catch (e) {
    return 'agrisense-db-default'
  }
}

export const initDB = async () => {
  const dbName = getDBName()
  return openDB(dbName, DB_VERSION, {
    upgrade(db, oldVersion, newVersion, transaction) {
      if (!db.objectStoreNames.contains(STORE_API_CACHE)) {
        // Cache for GET requests (key is URL)
        db.createObjectStore(STORE_API_CACHE, { keyPath: 'url' })
      }
      if (!db.objectStoreNames.contains(STORE_SYNC_QUEUE)) {
        // Queue for mutations (auto-incrementing ID)
        const queueStore = db.createObjectStore(STORE_SYNC_QUEUE, {
          keyPath: 'id',
          autoIncrement: true
        })
        queueStore.createIndex('timestamp', 'timestamp')
      }
      if (!db.objectStoreNames.contains(STORE_REMINDERS)) {
        db.createObjectStore(STORE_REMINDERS, { keyPath: 'id' })
      }
    }
  })
}

// ---- Cache Methods ----
export const getCachedRequest = async (url) => {
  const db = await initDB()
  const result = await db.get(STORE_API_CACHE, url)
  return result ? result.data : null
}

export const setCachedRequest = async (url, data) => {
  const db = await initDB()
  await db.put(STORE_API_CACHE, { url, data, timestamp: Date.now() })
}

// ---- Queue Methods ----
export const addToSyncQueue = async (url, method, payload) => {
  const db = await initDB()
  await db.add(STORE_SYNC_QUEUE, {
    url,
    method,
    payload,
    timestamp: Date.now()
  })
}

export const getSyncQueue = async () => {
  const db = await initDB()
  // Retrieve all queued actions, sorted by oldest first
  return db.getAllFromIndex(STORE_SYNC_QUEUE, 'timestamp')
}

export const removeFromSyncQueue = async (id) => {
  const db = await initDB()
  await db.delete(STORE_SYNC_QUEUE, id)
}

// ---- Reminder Methods ----
export const addReminder = async (reminder) => {
  const db = await initDB()
  await db.put(STORE_REMINDERS, reminder)
}

export const getReminders = async () => {
  const db = await initDB()
  return db.getAll(STORE_REMINDERS)
}

export const removeReminder = async (id) => {
  const db = await initDB()
  await db.delete(STORE_REMINDERS, id)
}
