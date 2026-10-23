# asset-metadata-service

图片和视频基础信息提取服务，只负责确定性媒体元数据，不负责 AI 标签和人工审核。

当前版本：v0.2.0  
输出契约：metadata-contract-v0.1

服务只维护素材固有事实，不维护 AI Tag，也不允许人工修改原始元数据。
图片比例、视频时长、分辨率等字段由确定性解析器产生。契约见
`docs/METADATA_CONTRACT.md`，JSON Schema 见 `schemas/metadata-result.schema.json`。

运行时 API：

```text
GET  /healthz
POST /v1/metadata
POST /v1/video-preview
```

当前 `/v1/metadata` API 接收已经由图片/视频探针提取出的确定性字段，并负责
规范化、校验和返回统一结果。

`POST /v1/video-preview` 接收原始视频二进制，使用容器内 `ffmpeg` 在视频全程
采样四帧，返回 1280×1280 的 JPEG 2×2 联系表。响应头
`X-Video-Duration` 包含检测到的时长。该接口不会持久化视频或预览帧。
