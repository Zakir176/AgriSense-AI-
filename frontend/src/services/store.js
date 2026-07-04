import { reactive } from 'vue'

export const store = reactive({
  currentUser: null,
  currentFarm: null,
  activeBatch: null,
  batchesList: [],
  alertsList: [],
  farmsList: [],
  latestInferenceResult: null
})
