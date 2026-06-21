const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

async function request(path, options = {}) {
  const token = localStorage.getItem('agrisense_token')
  const headers = { ...options.headers }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  // Set Content-Type to JSON unless we are uploading files/FormData or urlencoded bodies
  if (options.body && !(options.body instanceof FormData) && !(options.body instanceof URLSearchParams)) {
    headers['Content-Type'] = 'application/json'
    options.body = JSON.stringify(options.body)
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers
  })

  if (!response.ok) {
    let errorDetail = 'Request failed'
    try {
      const errJson = await response.json()
      errorDetail = errJson.detail || errorDetail
    } catch (_) {}
    throw new Error(errorDetail)
  }

  if (response.status === 204) {
    return null
  }

  return response.json()
}

export const api = {
  // Authentication
  auth: {
    async login(username, password) {
      // FastAPI OAuth2PasswordRequestForm expects url-encoded payload
      const params = new URLSearchParams()
      params.append('username', username)
      params.append('password', password)

      const result = await request('/auth/token', {
        method: 'POST',
        body: params
      })
      if (result && result.access_token) {
        localStorage.setItem('agrisense_token', result.access_token)
      }
      return result
    },
    
    getMe() {
      return request('/auth/me')
    }
  },

  // Farms
  farms: {
    list() {
      return request('/farms')
    },
    create(data) {
      return request('/farms', {
        method: 'POST',
        body: data
      })
    }
  },

  // Batches
  batches: {
    list(farmId = null) {
      const url = farmId ? `/batches?farm_id=${farmId}` : '/batches'
      return request(url)
    },
    create(data) {
      return request('/batches', {
        method: 'POST',
        body: data
      })
    },
    update(id, data) {
      return request(`/batches/${id}`, {
        method: 'PUT',
        body: data
      })
    },
    delete(id) {
      return request(`/batches/${id}`, {
        method: 'DELETE'
      })
    }
  },

  // Readings (Feed & Water)
  readings: {
    list(batchId = null) {
      const url = batchId ? `/readings?batch_id=${batchId}` : '/readings'
      return request(url)
    },
    create(data) {
      return request('/readings', {
        method: 'POST',
        body: data
      })
    },
    getSummary(batchId) {
      return request(`/readings/summary/${batchId}`)
    }
  },

  // Growth
  growth: {
    list(batchId = null) {
      const url = batchId ? `/growth?batch_id=${batchId}` : '/growth'
      return request(url)
    },
    create(data) {
      return request('/growth', {
        method: 'POST',
        body: data
      })
    },
    getSummary(batchId) {
      return request(`/growth/summary/${batchId}`)
    }
  },

  // Medications
  medications: {
    list(batchId = null) {
      const url = batchId ? `/medications?batch_id=${batchId}` : '/medications'
      return request(url)
    },
    create(data) {
      return request('/medications', {
        method: 'POST',
        body: data
      })
    },
    update(id, data) {
      return request(`/medications/${id}`, {
        method: 'PUT',
        body: data
      })
    }
  },

  // Alerts
  alerts: {
    list(batchId = null, unacknowledgedOnly = false) {
      let url = '/alerts'
      const params = []
      if (batchId !== null) params.push(`batch_id=${batchId}`)
      if (unacknowledgedOnly) params.push(`unacknowledged_only=true`)
      if (params.length > 0) url += `?${params.join('&')}`
      return request(url)
    },
    acknowledge(id) {
      return request(`/alerts/${id}`, {
        method: 'PUT',
        body: { acknowledged: true }
      })
    }
  },

  // AI Visual Monitor / Inference
  inference: {
    uploadVideo(batchId, file) {
      const formData = new FormData()
      formData.append('batch_id', batchId)
      formData.append('file', file)

      return request('/inference/video', {
        method: 'POST',
        body: formData
      })
    },
    list(batchId = null) {
      const url = batchId ? `/inference/clips?batch_id=${batchId}` : '/inference/clips'
      return request(url)
    }
  }
}
