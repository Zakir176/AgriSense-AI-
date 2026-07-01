import { getCachedRequest, setCachedRequest, addToSyncQueue } from './db'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1'

async function request(path, options = {}) {
  const token = localStorage.getItem('agrisense_token')
  const headers = { ...options.headers }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const isMutation = ['POST', 'PUT', 'DELETE'].includes(options.method)

  // Set Content-Type to JSON unless we are uploading files/FormData or urlencoded bodies
  if (options.body && !(options.body instanceof FormData) && !(options.body instanceof URLSearchParams)) {
    headers['Content-Type'] = 'application/json'
    options.body = JSON.stringify(options.body)
  }

  // --- OFFLINE INTERCEPTOR ---
  if (!navigator.onLine) {
    if (!isMutation) {
      // GET: Read from IndexedDB cache
      const cached = await getCachedRequest(path)
      if (cached) {
        console.log(`[Offline] Served ${path} from cache`)
        return cached
      }
      throw new Error('You are offline and no cached data is available for this request.')
    } else {
      // Mutation: Queue it for background sync
      let payloadToQueue = options.body
      if (options.body instanceof URLSearchParams) {
        // Can't easily store URLSearchParams in IndexedDB without converting
        payloadToQueue = Object.fromEntries(options.body.entries())
      } else if (typeof options.body === 'string') {
        payloadToQueue = JSON.parse(options.body)
      }
      
      await addToSyncQueue(path, options.method, payloadToQueue)
      console.log(`[Offline] Queued ${options.method} request to ${path}`)
      
      // Return a mocked success response so UI updates optimistically
      return { success: true, offline: true, id: Date.now() } // Mock ID just in case
    }
  }

  // --- ONLINE BEHAVIOR ---
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers
  })

  if (!response.ok) {
    if (response.status === 401 && path !== '/auth/token') {
      localStorage.removeItem('agrisense_token')
      window.location.href = '/login'
    }
    let errorDetail = 'Request failed'
    try {
      const errJson = await response.json()
      errorDetail = errJson.detail || errorDetail
    } catch (_) {}
    throw new Error(typeof errorDetail === 'string' ? errorDetail : JSON.stringify(errorDetail))
  }

  if (response.status === 204) {
    return null
  }

  const jsonResponse = await response.json()

  // Cache successful GET requests
  if (!isMutation) {
    await setCachedRequest(path, jsonResponse)
  }

  return jsonResponse
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
    },

    async register(username, password, fullName) {
      // Create the account
      await request('/auth/register', {
        method: 'POST',
        body: { username, password, full_name: fullName || null }
      })
      // Auto-login after successful registration
      return this.login(username, password)
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
    },
    update(id, data) {
      return request(`/readings/${id}`, {
        method: 'PUT',
        body: data
      })
    },
    delete(id) {
      return request(`/readings/${id}`, {
        method: 'DELETE'
      })
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
    },
    update(id, data) {
      return request(`/growth/${id}`, {
        method: 'PUT',
        body: data
      })
    },
    delete(id) {
      return request(`/growth/${id}`, {
        method: 'DELETE'
      })
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
    },
    delete(id) {
      return request(`/medications/${id}`, {
        method: 'DELETE'
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
  },

  // Analytics/Insights (Client-Side Calculated Recommendations to match backend mockup specs)
  analytics: {
    async getRecommendations(batchId) {
      try {
        const [readings, growth] = await Promise.all([
          api.readings.list(batchId),
          api.growth.list(batchId)
        ])

        const recommendations = []

        // If no readings, return a default prompt to log data
        if (readings.length === 0) {
          return [
            {
              type: 'info',
              title: 'Data Collection',
              message: 'Log feed, water, and growth samples to enable diagnostic recommendations.'
            }
          ]
        }

        // Calculate FCR
        const latestWeight = growth.length > 0 ? growth[0].avg_weight_g : null
        const totalFeed = readings.reduce((sum, r) => sum + (r.feed_kg || 0), 0)
        const totalMortality = readings.reduce((sum, r) => sum + (r.mortality_count || 0), 0)

        let birdCount = 1000
        try {
          const batches = await api.batches.list()
          const currentBatch = batches.find(b => b.id === Number(batchId))
          if (currentBatch) {
            birdCount = currentBatch.bird_count
          }
        } catch (_) {}

        const currentBirds = Math.max(1, birdCount - totalMortality)

        if (latestWeight && totalFeed > 0) {
          const startingWeightG = 42
          const totalG = (latestWeight * currentBirds) - (startingWeightG * birdCount)
          const biomassGainKg = Math.max(0, totalG / 1000)
          const fcr = biomassGainKg > 0 ? totalFeed / biomassGainKg : null

          if (fcr) {
            if (fcr >= 1.5 && fcr <= 1.75) {
              recommendations.push({
                type: 'success',
                title: 'FCR Optimal',
                message: `Feed Conversion Ratio is at a highly efficient ${fcr.toFixed(2)}. Nutrient absorption and flock conversion rate are matching industrial benchmark standards.`
              })
            } else if (fcr > 1.75 && fcr <= 1.9) {
              recommendations.push({
                type: 'warning',
                title: 'FCR Deviation',
                message: `Feed Conversion Ratio is elevated at ${fcr.toFixed(2)}. Consider checking feeder height to reduce waste, and verify ventilation levels to optimize bird activity.`
              })
            } else if (fcr > 1.9) {
              recommendations.push({
                type: 'danger',
                title: 'FCR Inefficiency',
                message: `FCR is high at ${fcr.toFixed(2)}. Immediate flock check suggested. Ensure feed formulation is correct, temperature is regulated, and check for sub-clinical health indicators.`
              })
            }
          }
        }

        // Check for latest mortality rates
        const mortalityRate = birdCount > 0 ? (totalMortality / birdCount) * 100 : 0
        if (mortalityRate > 5) {
          recommendations.push({
            type: 'danger',
            title: 'High Cumulative Mortality',
            message: `Cumulative flock mortality is at ${mortalityRate.toFixed(1)}%. Inspect environment logs, check water sanitation, and consult veterinarian if losses persist.`
          })
        } else if (mortalityRate > 2) {
          recommendations.push({
            type: 'warning',
            title: 'Elevated Cumulative Mortality',
            message: `Flock mortality has reached ${mortalityRate.toFixed(1)}%. Review biosecurity protocols and check environmental comfort levels.`
          })
        } else {
          recommendations.push({
            type: 'success',
            title: 'Low Flock Mortality',
            message: `Flock mortality is well controlled at ${mortalityRate.toFixed(1)}% (below target threshold of 2.0%). Keep up the strict biosecurity.`
          })
        }

        // Check feed/water ratio
        const totalWater = readings.reduce((sum, r) => sum + (r.water_litres || 0), 0)
        if (totalFeed > 0 && totalWater > 0) {
          const ratio = totalWater / totalFeed
          if (ratio < 1.6) {
            recommendations.push({
              type: 'warning',
              title: 'Low Water-Feed Ratio',
              message: `Water intake is low relative to feed intake (${ratio.toFixed(2)}:1). Check water lines, nozzle flow rates, and ambient temperatures.`
            })
          } else if (ratio > 2.2) {
            recommendations.push({
              type: 'warning',
              title: 'High Water-Feed Ratio',
              message: `Water intake is elevated relative to feed (${ratio.toFixed(2)}:1). This can indicate high house temperatures. Ensure fans are active.`
            })
          } else {
            recommendations.push({
              type: 'success',
              title: 'Hydration Balanced',
              message: `Water-to-feed ratio is balanced at ${ratio.toFixed(2)}:1, indicating normal digestability and temperature comfort.`
            })
          }
        }

        if (recommendations.length === 0) {
          recommendations.push({
            type: 'info',
            title: 'Standard Insights',
            message: 'Flock metric indicators are within expected margins. Continue tracking daily feed, water, and weight gains.'
          })
        }

        return recommendations
      } catch (err) {
        console.error('Error generating recommendations:', err)
        return [
          {
            type: 'info',
            title: 'Analytics Insights',
            message: 'Additional data needed or backend error occurred when checking recommendations.'
          }
        ]
      }
    }
  }
}
