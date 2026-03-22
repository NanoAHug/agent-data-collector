# TODO

## 安全认证改进

### 1. API Key 认证（数据收集端）
- [x] 改用 `Authorization: Bearer <api_key>` header，不再用 query parameter
- [x] 使用 `secrets.compare_digest()` 防止时序攻击
- [ ] API key 用 SHA-256 哈希存储

### 2. Web 登录认证
- [ ] 密码用 SHA-256 哈希存储
- [ ] Cookie 添加 `secure=True, samesite="strict"`
- [ ] Session 保持内存存储

### 3. HTTPS 强制
- [ ] 生产环境强制 HTTPS 重定向
- [ ] 添加安全 headers（HSTS, X-Frame-Options 等）
- [ ] 文档中强调必须使用 HTTPS

### 4. Rate Limiting
- [ ] 不内置，用户可自行在 nginx 层面配置

## 依赖更新
- [ ] 添加 `passlib` 用于密码哈希（可选，如果用 SHA-256 内置库则不需要）
