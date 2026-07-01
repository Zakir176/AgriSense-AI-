import { openDB } from 'idb'

const DB_NAME = 'agrisense-db'
const DB_VERSION = 1
const STORE_API_CACHE = 'api-cache'
const STORE_SYNC_QUEUE = 'sync-queue'

const initDB = async () => {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
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
