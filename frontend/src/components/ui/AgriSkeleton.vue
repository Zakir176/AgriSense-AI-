<template>
  <div :class="[baseClass, typeClass]"></div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'text',
    validator: (v) => ['text', 'card', 'chart', 'avatar', 'button', 'badge'].includes(v)
  },
  height: {
    type: String,
    default: ''
  },
  width: {
    type: String,
    default: ''
  }
})

const baseClass = 'animate-shimmer rounded-md'

const typeClass = computed(() => {
  // If height/width are specifically passed, we can merge them in the component via standard class/style bindings, 
  // but for predefined types we supply reasonable defaults.
  let cls = ''
  switch (props.type) {
    case 'text':
      cls = 'h-4 w-full'
      break
    case 'card':
      cls = 'h-32 w-full rounded-2xl'
      break
    case 'chart':
      cls = 'h-[300px] w-full rounded-2xl'
      break
    case 'avatar':
      cls = 'h-10 w-10 rounded-full'
      break
    case 'button':
      cls = 'h-10 w-32 rounded-xl'
      break
    case 'badge':
      cls = 'h-6 w-16 rounded-full'
      break
  }

  // Override if custom props provided
  if (props.height) cls = cls.replace(/h-[^\s]+/, props.height)
  if (props.width) cls = cls.replace(/w-[^\s]+/, props.width)

  return cls
})
</script>
