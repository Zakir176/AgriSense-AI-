<template>
  <div class="space-y-6">
    <!-- ─── Header ─── -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 animate-fade-in-up">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">Farm Settings & Management</h1>
        <p class="mt-0.5 text-sm text-gray-550 dark:text-gray-400">
          Manage farm metadata, switch between cohorts, and configure role-based access for
          <span v-if="store.currentFarm" class="font-bold text-gray-700 dark:text-gray-300">{{ store.currentFarm.name }}</span>
          <span v-else class="italic text-gray-450">no active farm</span>
        </p>
      </div>
      <div v-if="isOwner" class="flex items-center gap-3 w-full sm:w-auto">
        <AgriButton
          variant="primary"
          icon="person_add"
          :disabled="isOffline"
          @click="openAddModal"
        >
          Add Farm Member
        </AgriButton>
      </div>
    </div>

    <!-- ─── Main Content Grid ─── -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- ─── Left Side: Farm Details & Creation ─── -->
      <div class="lg:col-span-1 space-y-6">
        <!-- Farm Info Card -->
        <AgriCard class="animate-fade-in-up delay-100">
          <template #header>
            <div class="flex items-center gap-2">
              <span class="material-icons-outlined text-gray-550">info</span>
              <h2 class="text-sm font-bold text-gray-900 dark:text-white">Farm Profile</h2>
            </div>
          </template>

          <form @submit.prevent="handleUpdateFarm" class="space-y-4">
            <AgriInput
              label="Farm Name"
              v-model="farmForm.name"
              placeholder="e.g. Prime Nest Poultry"
              required
              :disabled="!isOwner"
            />
            <AgriInput
              label="Location"
              v-model="farmForm.location"
              placeholder="e.g. Lusaka, Zambia"
              :disabled="!isOwner"
            />
            <div v-if="isOwner" class="pt-2">
              <AgriButton
                type="submit"
                variant="primary"
                :loading="updatingFarm"
                class="w-full"
              >
                Save Details
              </AgriButton>
            </div>
            <div v-else class="text-xs text-gray-400 dark:text-gray-500 italic mt-2 text-center">
              Only owners can edit farm settings. (Your role: {{ currentRole }})
            </div>
          </form>
        </AgriCard>

        <!-- Farms Switcher/Creation -->
        <AgriCard class="animate-fade-in-up delay-150">
          <template #header>
            <div class="flex items-center gap-2">
              <span class="material-icons-outlined text-gray-550">holiday_village</span>
              <h2 class="text-sm font-bold text-gray-900 dark:text-white">My Farms</h2>
            </div>
          </template>

          <div class="space-y-3">
            <div
              v-for="farm in store.farmsList"
              :key="farm.id"
              class="flex items-center justify-between p-3 rounded-xl border transition-colors cursor-pointer"
              :class="[
                store.currentFarm?.id === farm.id
                  ? 'border-primary-500/35 bg-primary-500/5 dark:bg-primary-600/10'
                  : 'border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-darkbg-50/30'
              ]"
              @click="switchFarm(farm)"
            >
              <div>
                <p class="text-xs font-bold text-gray-855 dark:text-gray-200">{{ farm.name }}</p>
                <p class="text-[10px] text-gray-450 dark:text-gray-500">{{ farm.location || 'No location set' }}</p>
              </div>
              <AgriBadge
                :variant="farm.role === 'owner' ? 'success' : farm.role === 'operator' ? 'primary' : 'secondary'"
              >
                {{ farm.role }}
              </AgriBadge>
            </div>

            <!-- New Farm Creation -->
            <div class="border-t border-gray-100 dark:border-gray-800 pt-4 mt-2">
              <p class="text-xs font-bold text-gray-800 dark:text-gray-300 mb-2">Create New Farm</p>
              <form @submit.prevent="handleCreateFarm" class="space-y-3">
                <AgriInput
                  placeholder="New farm name"
                  v-model="newFarm.name"
                  required
                />
                <AgriInput
                  placeholder="Location"
                  v-model="newFarm.location"
                />
                <AgriButton
                  type="submit"
                  variant="outline"
                  size="sm"
                  class="w-full"
                  :loading="creatingFarm"
                >
                  Create Farm
                </AgriButton>
              </form>
            </div>
          </div>
        </AgriCard>
      </div>

      <!-- ─── Right Side: Members list ─── -->
      <div class="lg:col-span-2">
        <AgriCard class="animate-fade-in-up delay-200" padding="none">
          <template #header>
            <div class="flex items-center gap-2">
              <span class="material-icons-outlined text-gray-550">people</span>
              <h2 class="text-sm font-bold text-gray-900 dark:text-white">Authorized Members</h2>
            </div>
          </template>

          <div class="p-6">
            <AgriTable
              :headers="tableHeaders"
              :items="members"
              :loading="loadingMembers"
            >
              <!-- Customize username rendering with icon -->
              <template #username="{ item }">
                <div class="flex items-center gap-2">
                  <span class="material-icons-outlined text-xs text-gray-400">account_circle</span>
                  <span>{{ item.username }}</span>
                  <span v-if="item.user_id === store.currentUser?.id" class="text-[10px] text-primary-500 font-bold bg-primary-50 dark:bg-primary-950/40 px-1.5 py-0.5 rounded-full">You</span>
                </div>
              </template>

              <!-- Render roles with specific Badges -->
              <template #role="{ item }">
                <div class="flex items-center gap-2">
                  <!-- In-line dropdown to update role for Owners -->
                  <div v-if="isOwner && item.user_id !== store.currentUser?.id && !isOffline" class="relative">
                    <select
                      v-model="item.role"
                      @change="updateMemberRole(item)"
                      class="text-xs font-semibold rounded-lg border border-gray-250 dark:border-gray-800 bg-white dark:bg-darkbg-100 py-1.5 px-2.5 outline-none focus:border-primary-500"
                    >
                      <option value="owner">Owner</option>
                      <option value="operator">Operator</option>
                      <option value="viewer">Viewer</option>
                    </select>
                  </div>
                  <AgriBadge
                    v-else
                    :variant="item.role === 'owner' ? 'success' : item.role === 'operator' ? 'primary' : 'secondary'"
                  >
                    {{ item.role }}
                  </AgriBadge>
                </div>
              </template>

              <!-- Actions column -->
              <template #actions="{ item }">
                <div class="flex justify-end">
                  <AgriButton
                    v-if="isOwner && item.user_id !== store.currentUser?.id"
                    variant="destructive"
                    size="sm"
                    icon="person_remove"
                    :disabled="isOffline"
                    @click="removeMember(item)"
                  >
                    Remove
                  </AgriButton>
                  <span v-else class="text-xs text-gray-400 italic">No actions</span>
                </div>
              </template>
            </AgriTable>
          </div>
        </AgriCard>
      </div>

    </div>

    <!-- ─── Add Member Modal ─── -->
    <AgriModal
      :show="showAddModal"
      title="Add Farm Member"
      @close="showAddModal = false"
    >
      <form @submit.prevent="handleAddMember" class="space-y-4">
        <p class="text-xs text-gray-500 dark:text-gray-400">
          Enter the exact username of the registered user account you wish to authorize.
        </p>

        <AgriInput
          label="Username"
          v-model="addForm.username"
          placeholder="e.g. operator_john"
          required
          icon="person"
        />

        <div class="flex flex-col gap-1.5">
          <label class="text-xs font-bold text-gray-500 uppercase dark:text-gray-400">Access Role</label>
          <select
            v-model="addForm.role"
            class="w-full text-sm font-medium rounded-xl border border-gray-250 dark:border-gray-800 bg-white dark:bg-darkbg-50/50 text-gray-900 dark:text-white p-3 outline-none focus:border-primary-500"
          >
            <option value="viewer">Viewer (Read-only data access)</option>
            <option value="operator">Operator (Log data, execute runs)</option>
            <option value="owner">Owner (Full admin privileges)</option>
          </select>
        </div>

        <div class="flex gap-3 justify-end pt-4 border-t border-gray-100 dark:border-gray-800">
          <AgriButton variant="outline" @click="showAddModal = false">
            Cancel
          </AgriButton>
          <AgriButton type="submit" variant="primary" :loading="addingMember">
            Add User
          </AgriButton>
        </div>
      </form>
    </AgriModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { store } from '../services/store'
import { api } from '../services/api'
import { useToast } from '../composables/useToast'

const toast = useToast()

// ── State ──────────────────────────────────
const loadingMembers = ref(false)
const updatingFarm = ref(false)
const creatingFarm = ref(false)
const addingMember = ref(false)
const showAddModal = ref(false)
const isOffline = ref(!navigator.onLine)

const members = ref([])
const farmForm = ref({ name: '', location: '' })
const newFarm = ref({ name: '', location: '' })
const addForm = ref({ username: '', role: 'operator' })

const tableHeaders = [
  { text: 'User', value: 'username', sortable: true },
  { text: 'Full Name', value: 'full_name', sortable: true },
  { text: 'Role Permissions', value: 'role', sortable: false },
  { text: 'Actions', value: 'actions', sortable: false, align: 'right' }
]

// ── Computed ──────────────────────────────
const isOwner = computed(() => {
  return store.currentFarm?.role === 'owner'
})

const currentRole = computed(() => {
  return store.currentFarm?.role || 'none'
})

// ── Watchers ──────────────────────────────
watch(() => store.currentFarm, (newFarmVal) => {
  if (newFarmVal) {
    farmForm.value.name = newFarmVal.name
    farmForm.value.location = newFarmVal.location || ''
    fetchMembers()
  } else {
    members.value = []
  }
}, { immediate: true })

// ── Methods ──────────────────────────────
const fetchMembers = async () => {
  if (!store.currentFarm) return
  loadingMembers.value = true
  try {
    const list = await api.farms.listMembers(store.currentFarm.id)
    members.value = list
  } catch (err) {
    console.error('Failed to load farm members:', err)
    toast.error('Could not load members list')
  } finally {
    loadingMembers.value = false
  }
}

const handleUpdateFarm = async () => {
  if (!store.currentFarm) return
  updatingFarm.value = true
  try {
    const updated = await api.farms.update(store.currentFarm.id, {
      name: farmForm.value.name,
      location: farmForm.value.location
    })
    
    // Update store list
    const index = store.farmsList.findIndex(f => f.id === store.currentFarm.id)
    if (index > -1) {
      store.farmsList[index].name = updated.name
      store.farmsList[index].location = updated.location
    }
    store.currentFarm.name = updated.name
    store.currentFarm.location = updated.location
    
    toast.success('Farm details updated successfully')
  } catch (err) {
    console.error('Failed to update farm details:', err)
    toast.error(err.message || 'Failed to update farm')
  } finally {
    updatingFarm.value = false
  }
}

const handleCreateFarm = async () => {
  creatingFarm.value = true
  try {
    const created = await api.farms.create({
      name: newFarm.value.name,
      location: newFarm.value.location
    })
    
    // Reload farm list
    const list = await api.farms.list()
    store.farmsList = list
    
    newFarm.value.name = ''
    newFarm.value.location = ''
    
    toast.success(`Created farm "${created.name}"`)
  } catch (err) {
    console.error('Failed to create new farm:', err)
    toast.error(err.message || 'Failed to create farm')
  } finally {
    creatingFarm.value = false
  }
}

const openAddModal = () => {
  addForm.value.username = ''
  addForm.value.role = 'operator'
  showAddModal.value = true
}

const handleAddMember = async () => {
  if (!store.currentFarm) return
  addingMember.value = true
  try {
    const response = await api.farms.addMember(store.currentFarm.id, {
      username: addForm.value.username,
      role: addForm.value.role
    })
    
    members.value.push(response)
    showAddModal.value = false
    toast.success(`User "${response.username}" added as ${response.role}`)
  } catch (err) {
    console.error('Failed to add farm member:', err)
    toast.error(err.message || 'Could not add member')
  } finally {
    addingMember.value = false
  }
}

const updateMemberRole = async (member) => {
  if (!store.currentFarm) return
  try {
    await api.farms.updateMember(store.currentFarm.id, member.user_id, {
      role: member.role
    })
    toast.success(`Role for ${member.username} updated to ${member.role}`)
  } catch (err) {
    console.error('Failed to update member role:', err)
    toast.error(err.message || 'Could not update role')
    // Reset from db
    fetchMembers()
  }
}

const removeMember = async (member) => {
  if (!store.currentFarm) return
  if (!confirm(`Are you sure you want to remove user "${member.username}" from this farm?`)) return
  
  try {
    await api.farms.removeMember(store.currentFarm.id, member.user_id)
    members.value = members.value.filter(m => m.user_id !== member.user_id)
    toast.success(`User "${member.username}" removed from farm`)
  } catch (err) {
    console.error('Failed to remove member:', err)
    toast.error(err.message || 'Could not remove member')
  }
}

const switchFarm = (farm) => {
  store.currentFarm = farm
}

const updateOnlineStatus = () => {
  isOffline.value = !navigator.onLine
}

// ── Lifecycle ──────────────────────────────
onMounted(() => {
  fetchMembers()
  window.addEventListener('online', updateOnlineStatus)
  window.addEventListener('offline', updateOnlineStatus)
})
</script>
