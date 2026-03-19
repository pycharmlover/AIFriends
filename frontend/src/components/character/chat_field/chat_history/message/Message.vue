<script setup>

import {useUserStore} from "../../../../../stores/user.js";
import PlayTts from "./tts/PlayTts.vue";

defineProps(['message', 'character', 'friendId'])

const user = useUserStore()
</script>

<template>
  <div v-if="message.content">
    <div v-if="message.role === 'ai'" class="chat chat-start">
      <div class="chat-image avatar">
        <div class="w-10 rounded-full">
          <img :src="character.photo" alt="">
        </div>
      </div>
      <div class="chat-bubble whitespace-pre-wrap break-all">{{ message.content }}</div>
      <PlayTts :text="message.content" :friendId="friendId" />
    </div>
    <div v-else class="chat chat-end">
      <div class="chat-image avatar">
        <div class="w-10 rounded-full">
          <img :src="user.photo" alt="">>
        </div>
      </div>
      <div class="chat-bubble chat-bubble-success whitespace-pre-wrap break-all">{{ message.content }}</div>
    </div>
  </div>
</template>

<style scoped>

</style>
