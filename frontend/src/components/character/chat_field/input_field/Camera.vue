<script setup>
import {ref, onMounted, onBeforeUnmount, useTemplateRef} from "vue"
import CameraIcon from "../../icons/CameraIcon.vue"

const props = defineProps(['onFrameCapture'])

const videoRef = useTemplateRef('video-ref')
const canvasRef = useTemplateRef('canvas-ref')
const isActive = ref(false)
const stream = ref(null)
const frameInterval = ref(null)

async function startCamera() {
  try {
    stream.value = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 640 }, height: { ideal: 480 } },
      audio: false
    })
    
    // 等待 video 元素挂载
    await new Promise(resolve => setTimeout(resolve, 100))
    
    if (videoRef.value) {
      videoRef.value.srcObject = stream.value
      isActive.value = true

      // 每 500ms 抽取一帧
      frameInterval.value = setInterval(captureFrame, 500)
    }
  } catch (err) {
    // console.error('摄像头访问失败:', err)
  }
}

function stopCamera() {
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop())
    stream.value = null
  }
  if (frameInterval.value) {
    clearInterval(frameInterval.value)
    frameInterval.value = null
  }
  isActive.value = false
}

function captureFrame() {
  if (!videoRef.value || !canvasRef.value) return

  const ctx = canvasRef.value.getContext('2d')
  canvasRef.value.width = videoRef.value.videoWidth
  canvasRef.value.height = videoRef.value.videoHeight
  ctx.drawImage(videoRef.value, 0, 0)

  // 转为 Base64
  const imageBase64 = canvasRef.value.toDataURL('image/jpeg', 0.8).split(',')[1]
  props.onFrameCapture(imageBase64)
}

function toggleCamera() {
  if (isActive.value) {
    stopCamera()
  } else {
    startCamera()
  }
}

onBeforeUnmount(() => {
  stopCamera()
})

defineExpose({
  isActive,
  toggleCamera,
})
</script>

<template>
  <div class="flex flex-col gap-2 w-full">
    <!-- 摄像头视频预览 -->
    <div v-if="isActive" class="relative w-full bg-black rounded-lg overflow-hidden">
      <video
        ref="video-ref"
        autoplay
        playsinline
        class="w-full h-auto"
      />
      <canvas ref="canvas-ref" class="hidden" />
    </div>

    <!-- 摄像头按钮 -->
    <button
      @click="toggleCamera"
      :class="{ 'btn-error': isActive, 'btn-primary': !isActive }"
      class="btn btn-sm gap-1 w-full"
    >
      <CameraIcon />
      {{ isActive ? '关闭摄像头' : '打开摄像头' }}
    </button>
  </div>
</template>

<style scoped>
</style>
