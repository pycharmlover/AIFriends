<script setup>
import {ref} from "vue"
import HornIcon from "../../../../icons/Horn.vue"
import streamApi from "../../../../../../js/http/streamApi.js"

const props = defineProps(['text', 'friendId'])

const isPlaying = ref(false)

// 将 base64 字符串转为 Uint8Array
function base64ToUint8Array(base64) {
  const binary = atob(base64)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i)
  }
  return bytes
}

// 合并多个 Uint8Array 为一个完整 ArrayBuffer
function mergeChunks(chunks) {
  const totalLength = chunks.reduce((sum, c) => sum + c.length, 0)
  const merged = new Uint8Array(totalLength)
  let offset = 0
  for (const chunk of chunks) {
    merged.set(chunk, offset)
    offset += chunk.length
  }
  return merged.buffer
}

async function play() {
  if (isPlaying.value) return
  isPlaying.value = true

  const chunks = []

  try {
    // 1. 收集所有音频块
    await streamApi('/api/friend/message/tts/', {
      body: {
        friend_id: props.friendId,
        text: props.text,
      },
      onmessage: (data, done) => {
        if (done) return
        if (data.audio) {
          chunks.push(base64ToUint8Array(data.audio))
        }
      },
    })

    // 2. 合并为完整 mp3 buffer 后统一解码播放
    if (chunks.length === 0) return
    const fullBuffer = mergeChunks(chunks)
    const ctx = new AudioContext()
    const audioBuffer = await ctx.decodeAudioData(fullBuffer)
    const source = ctx.createBufferSource()
    source.buffer = audioBuffer
    source.connect(ctx.destination)
    source.start(0)
    source.onended = () => ctx.close()
  } finally {
    isPlaying.value = false
  }
}
</script>

<template>
  <button
    class="btn btn-xs btn-ghost btn-circle mt-1 ml-1 opacity-60 hover:opacity-100 transition-opacity"
    :class="{ 'animate-pulse': isPlaying }"
    :disabled="isPlaying"
    @click="play"
    title="重新播放语音"
  >
    <HornIcon />
  </button>
</template>

<style scoped>
</style>

