# asset-metadata-service

图片和视频基础信息提取服务，只负责确定性媒体元数据，不负责 AI 标签和人工审核。

当前版本：v0.1.0  
输出契约：metadata-contract-v0.1

服务只维护素材固有事实，不维护 AI Tag，也不允许人工修改原始元数据。
图片比例、视频时长、分辨率等字段由确定性解析器产生。契约见
`docs/METADATA_CONTRACT.md`，JSON Schema 见 `schemas/metadata-result.schema.json`。
