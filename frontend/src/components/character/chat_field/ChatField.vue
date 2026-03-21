<script setup>

import InputField from "./input_field/InputField.vue";
import CharacterPhotoField from "./character_photo_field/CharacterPhotoField.vue";
import {computed, nextTick, ref, useTemplateRef} from "vue";
import ChatHistory from "./chat_history/ChatHistory.vue";

const props = defineProps(['friend'])
const modalRef = useTemplateRef('modal-ref')
const inputRef = useTemplateRef('input-ref')
const chatHistoryRef = useTemplateRef('chat-history-ref')
const history = ref([])
const scale = ref(1)  // 缩放比例
let isResizing = false
let startX = 0
let startY = 0
let startScale = 1

async function showModal() {
  modalRef.value.showModal()

  await nextTick()
  inputRef.value.focus()
}

const modalStyle = computed(() => {
  if (props.friend) {
    return {
      backgroundImage: `url(${props.friend.character.background_image})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
    }
  } else {
    return {}
  }
})

function handlePushBackMessage(msg) {
  history.value.push(msg)
  chatHistoryRef.value.scrollToBottom()
}

function handleAddToLastMessage(delta) {
  history.value.at(-1).content += delta
  chatHistoryRef.value.scrollToBottom()
}

function handlePushFrontMessage(msg) {
  history.value.unshift(msg)
}

// 关闭聊天框时自动切换回文字输入
function handleClose(){
  inputRef.value.close()
}

// 处理右下角拖动缩放
function handleResizeMouseDown(e) {
  isResizing = true
  startX = e.clientX
  startY = e.clientY
  startScale = scale.value
  e.preventDefault()
}

function handleMouseMove(e) {
  if (!isResizing) return
  
  const deltaX = e.clientX - startX
  const deltaY = e.clientY - startY
  const delta = Math.max(deltaX, deltaY)
  
  // 每 100px 改变 0.1 的缩放比例
  const newScale = startScale + (delta / 100) * 0.1
  scale.value = Math.max(0.5, Math.min(2, newScale))
}

function handleMouseUp() {
  isResizing = false
}

defineExpose({
  showModal,
})
</script>

<template>
  <dialog ref="modal-ref" class="modal" @close="handleClose" @mousemove="handleMouseMove" @mouseup="handleMouseUp" @mouseleave="handleMouseUp">
    <div 
      class="modal-box w-90 h-150 relative" 
      :style="{
        backgroundImage: `url(${props.friend?.character.background_image})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        transform: `scale(${scale})`,
        transformOrigin: 'center',
        transition: isResizing ? 'none' : 'transform 0.2s ease-out'
      }"
    >
      <button @click="modalRef.close()" class="btn btn-sm btn-circle btn-ghost bg-transparent absolute right-1 top-1 z-10">✕</button>
      
      <!-- 右下角拖动手柄 -->
      <div 
        class="absolute bottom-0 right-0 w-6 h-6 cursor-se-resize opacity-50 hover:opacity-100 transition-opacity"
        :style="{
          background: 'linear-gradient(135deg, transparent 50%, #999 50%)',
          zIndex: 50
        }"
        @mousedown="handleResizeMouseDown"
      />
      
      <ChatHistory
          ref="chat-history-ref"
          v-if="friend"
          :history="history"
          :friendId="friend.id"
          :character="friend.character"
          @pushFrontMessage="handlePushFrontMessage"
      />
      <InputField
          v-if="friend"
          ref="input-ref"
          :friendId="friend.id"
          @pushBackMessage="handlePushBackMessage"
          @addToLastMessage="handleAddToLastMessage"
      />
      <CharacterPhotoField v-if="friend" :character="friend.character" />
    </div>
  </dialog>
</template>

<style scoped>

</style>
