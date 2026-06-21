import { reactive } from 'vue'

export const store = reactive({
  currentFarm: null,
  activeBatch: null,
  batchesList: [],
  alertsList: []
})
