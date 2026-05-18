基础依赖：

```toml
[package]
name = "{project_name}"
version = "0.1.0"
edition = "2024"

[dependencies]
axum = "0.8"
tokio = { version = "1", features = ["macros", "rt-multi-thread", "net"] }
tower-http = { version = "0.6", features = ["fs"] }
serde = { version = "1", features = ["derive"] }
```

按需添加：

```toml
# 数据库
rusqlite = { version = "0.35", features = ["bundled"] }

# HTTP 客户端
reqwest = { version = "0.12", default-features = false, features = ["json", "rustls-tls"] }

# 日志
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }

# JSON
serde_json = "1"

# UUID
uuid = { version = "1", features = ["v4"] }

# 时间
chrono = "0.4"

# CORS
# tower-http features 中加 "cors"
```
