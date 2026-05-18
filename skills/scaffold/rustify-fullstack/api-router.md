src/api/mod.rs：

```rust
pub mod ping;

use axum::{Router, http::StatusCode};

pub fn router() -> Router {
    Router::new()
        .nest("/v1", v1_router())
        .fallback(api_not_found)
}

fn v1_router() -> Router {
    Router::new()
        .merge(ping::router())
}

async fn api_not_found() -> StatusCode {
    StatusCode::NOT_FOUND
}
```

src/api/ping.rs：

```rust
use axum::{Router, routing::get};

pub fn router() -> Router {
    Router::new().route("/ping", get(|| async { "pong" }))
}
```

src/services/mod.rs：

```rust
// 业务逻辑模块
```

src/models/mod.rs：

```rust
// 响应结构模块
```
