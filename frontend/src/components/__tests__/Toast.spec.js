import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeEach } from 'vitest'
import Toast from '../Toast.vue'
import { useToast } from '../../composables/useToast'

describe('Toast.vue', () => {
  let toast

  beforeEach(() => {
    toast = useToast()
    // Clear toasts before each test
    toast.toasts.value = []
  })

  it('renders correctly when there are no toasts', () => {
    const wrapper = mount(Toast)
    expect(wrapper.text()).toBe('')
  })

  it('renders a toast when added', async () => {
    const wrapper = mount(Toast)
    
    toast.success('Test success message', 0)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.text()).toContain('Test success message')
    expect(wrapper.find('.text-emerald-500').exists()).toBe(true)
  })

  it('removes a toast when close button is clicked', async () => {
    const wrapper = mount(Toast)
    
    toast.error('Test error message', 0)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.text()).toContain('Test error message')
    
    const closeBtn = wrapper.find('button')
    await closeBtn.trigger('click')
    
    expect(wrapper.text()).not.toContain('Test error message')
  })
})
