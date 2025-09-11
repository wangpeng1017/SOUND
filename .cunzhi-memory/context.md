# 项目上下文信息

- 项目已集成OpenVoice v2语音克隆功能：
1. 使用Hugging Face Spaces公开Demo实现零样本语音克隆
2. 集成Edge TTS作为备用方案确保服务稳定
3. API接口：/api/tts支持真实语音合成，/api/voices管理音色
4. 音频文件存储在Vercel Blob Storage
5. 实现位于api/tts/openvoice_inline.py（内联版本避免导入问题）
- 首页空白问题排查记录：
1. 通过Vercel CLI成功部署项目
2. 修复了browserTTS未定义错误
3. 所有资源和API正常加载
4. Vue应用正常挂载但main内容为空
5. 问题可能在于Home.vue的模板条件渲染逻辑
